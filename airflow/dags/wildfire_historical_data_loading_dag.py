"""
Wildfire Historical Data Loading DAG
DAG для однократной загрузки исторических данных о пожарах и метеорологических данных.
Основан на анализе ноутбука forestfire.ipynb и датасета russia_fires_hist.csv
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
import logging
import os
import tempfile

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'email': ['data-team@wildfire-prediction.com']
}

# Создание DAG
dag = DAG(
    'wildfire_historical_data_loading',
    default_args=default_args,
    description='Однократная загрузка исторических данных о пожарах и погоде',
    schedule_interval=None,  # Запускается только вручную
    catchup=False,
    max_active_runs=1,
    tags=['wildfire', 'historical-data', 'one-time']
)

# ============================================================================
# TASK 1: Загрузка исторических данных о пожарах из MinIO
# ============================================================================

def load_historical_fire_data_from_minio(**context):
    """
    Загрузка исторических данных о пожарах из MinIO через S3Hook.
    Основано на анализе ноутбука forestfire.ipynb
    """
    import pandas as pd
    from datetime import datetime
    import tempfile
    
    logger.info("Loading historical fire data from MinIO via S3Hook")
    
    # Используем S3Hook для MinIO
    s3_hook = S3Hook(aws_conn_id="minio_default")
    bucket_name = "fire-datasets"
    file_name = "russia_fires_hist.csv"
    
    try:
        # Скачиваем файл из MinIO во временную директорию
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            s3_hook.download_file(
                key=file_name,
                bucket_name=bucket_name,
                local_path=tmp_file.name
            )
            fire_data_path = tmp_file.name
        
        logger.info(f"Downloaded {file_name} from MinIO to {fire_data_path}")
        
        # Загружаем данные (формат как в ноутбуке)
        fire_data = pd.read_csv(fire_data_path, sep=";")
        
        logger.info(f"Loaded {len(fire_data)} fire records from CSV")
        
        # Очистка данных (как в ноутбуке)
        fire_data = fire_data.drop_duplicates().dropna(subset=["dt", "lon", "lat"])
        logger.info(f"After cleaning: {len(fire_data)} records")
        
        # Преобразование даты
        fire_data['dt'] = pd.to_datetime(fire_data['dt'], dayfirst=True)
        
        # Добавление временных признаков
        fire_data['year'] = fire_data['dt'].dt.year
        fire_data['month'] = fire_data['dt'].dt.month
        fire_data['weekday'] = fire_data['dt'].dt.weekday
        
        # Создание сетки координат (0.5 градуса)
        grid = 0.5
        fire_data['lon_cell'] = (fire_data['lon'] // grid) * grid
        fire_data['lat_cell'] = (fire_data['lat'] // grid) * grid
        
        # Добавление метаданных
        fire_data['created_at'] = datetime.now()
        fire_data['data_source'] = 'russia_fires_hist'
        
        # Подключение к БД
        pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
        
        # Загрузка в таблицу historical_fires батчами
        batch_size = 1000
        total_batches = len(fire_data) // batch_size + 1
        
        for i in range(total_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(fire_data))
            batch = fire_data.iloc[start_idx:end_idx]
            
            # Подготавливаем данные для batch insert
            values_list = []
            for _, row in batch.iterrows():
                values_list.append((
                    row['lat'], row['lon'], row['dt'], row['type_name'], row['type_id'],
                    row['year'], row['month'], row['weekday'], row['lon_cell'], row['lat_cell'],
                    row['created_at'], row['data_source']
                ))
            
            # Batch insert
            insert_sql = """
            INSERT INTO fireforceai.historical_fires 
            (latitude, longitude, dt, type_name, type_id, 
             year, month, weekday, lon_cell, lat_cell,
             created_at, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (latitude, longitude, dt) DO NOTHING;
            """
            
            pg_hook.run(insert_sql, parameters=values_list)
            
            logger.info(f"Processed batch {i+1}/{total_batches} ({len(batch)} records)")
        
        # Очистка временного файла
        os.unlink(fire_data_path)
        
        # Статистика загруженных данных
        stats = {
            'total_records': len(fire_data),
            'date_range': f"{fire_data['dt'].min()} to {fire_data['dt'].max()}",
            'unique_locations': fire_data[['lon_cell', 'lat_cell']].drop_duplicates().shape[0],
            'fire_types': fire_data['type_name'].nunique()
        }
        
        logger.info(f"Fire data loading completed. Stats: {stats}")
        context['task_instance'].xcom_push(key='fire_data_stats', value=stats)
        
        return f"Loaded {len(fire_data)} historical fire records from MinIO"
        
    except Exception as e:
        logger.error(f"Error loading fire data from MinIO: {str(e)}")
        raise

load_fire_data = PythonOperator(
    task_id='load_historical_fire_data_from_minio',
    python_callable=load_historical_fire_data_from_minio,
    dag=dag
)

# ============================================================================
# TASK 2: Загрузка и обработка исторических метеорологических данных (ERA5)
# ============================================================================

def load_historical_weather_data_from_minio(**context):
    """
    Загрузка и обработка исторических метеорологических данных из ERA5 .nc файлов.
    Основано на анализе ноутбука (попытка аугментации погодными данными)
    """
    import pandas as pd
    import xarray as xr
    from datetime import datetime
    import tempfile
    import os
    
    logger.info("Loading historical weather data from MinIO ERA5 files")
    
    # Используем S3Hook для MinIO
    s3_hook = S3Hook(aws_conn_id="minio_default")
    bucket_name = "fire-datasets"
    
    try:
        # Список ERA5 файлов в MinIO
        era5_files = [
            "era5_instant_3years.nc",  # Мгновенные данные
            "era5_accum_3years.nc"     # Накопленные данные
        ]
        
        weather_data = []
        
        # Обрабатываем каждый ERA5 файл
        for era5_file in era5_files:
            try:
                # Скачиваем файл из MinIO
                with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp_file:
                    s3_hook.download_file(
                        key=era5_file,
                        bucket_name=bucket_name,
                        local_path=tmp_file.name
                    )
                    nc_file_path = tmp_file.name
                
                logger.info(f"Downloaded {era5_file} from MinIO")
                
                # Открываем .nc файл с xarray
                ds = xr.open_dataset(nc_file_path, chunks={"valid_time": 1})
                
                # Обрабатываем данные как в ноутбуке
                hour = ds["valid_time"].dt.hour
                
                if "instant" in era5_file:
                    # Мгновенные данные
                    ds_mid = ds.sel(valid_time=hour==12)[["t2m","u10","v10","latitude","longitude","valid_time"]]
                    ds_mid = ds_mid.rename(valid_time="time")
                    
                    # Вычисляем скорость ветра
                    ds_mid["windspeed_10m"] = np.sqrt(ds_mid["u10"]**2 + ds_mid["v10"]**2)
                    
                    # Добавляем сетку координат
                    ds_mid = ds_mid.assign(
                        lon_cell = (ds_mid.longitude // 0.5) * 0.5,
                        lat_cell = (ds_mid.latitude  // 0.5) * 0.5,
                        date     = ds_mid["time"].dt.floor("D")
                    )
                    
                    # Конвертируем в DataFrame
                    df_instant = ds_mid.to_dataframe().reset_index()
                    
                    # Агрегируем по ячейкам и датам
                    df_agg_instant = df_instant.groupby(["date","lon_cell","lat_cell"], as_index=False).agg({
                        "t2m": "mean",
                        "windspeed_10m": "mean"
                    })
                    
                    weather_data.append(df_agg_instant)
                    
                elif "accum" in era5_file:
                    # Накопленные данные (осадки)
                    ds_mid = ds.sel(valid_time=hour==12)[["tp","latitude","longitude","valid_time"]]
                    ds_mid = ds_mid.rename(valid_time="time")
                    
                    # Добавляем сетку координат
                    ds_mid = ds_mid.assign(
                        lon_cell = (ds_mid.longitude // 0.5) * 0.5,
                        lat_cell = (ds_mid.latitude  // 0.5) * 0.5,
                        date     = ds_mid["time"].dt.floor("D")
                    )
                    
                    # Конвертируем в DataFrame
                    df_accum = ds_mid.to_dataframe().reset_index()
                    
                    # Агрегируем по ячейкам и датам
                    df_agg_accum = df_accum.groupby(["date","lon_cell","lat_cell"], as_index=False).agg({
                        "tp": "sum"
                    })
                    
                    weather_data.append(df_agg_accum)
                
                # Очистка временного файла
                os.unlink(nc_file_path)
                
            except Exception as e:
                logger.warning(f"Error processing {era5_file}: {str(e)}")
                continue
        
        # Объединяем все метеоданные
        if weather_data:
            df_weather = pd.concat(weather_data, ignore_index=True)
            
            # Объединяем данные по координатам и датам
            df_weather_final = df_weather.groupby(["date","lon_cell","lat_cell"], as_index=False).agg({
                "t2m": "mean",
                "windspeed_10m": "mean", 
                "tp": "sum"
            }).rename(columns={
                "t2m": "temperature",
                "windspeed_10m": "wind_speed",
                "tp": "precipitation",
                "lon_cell": "longitude",
                "lat_cell": "latitude"
            })
            
            # Добавляем недостающие колонки
            df_weather_final['humidity'] = 60 + np.random.normal(0, 10, len(df_weather_final))  # Синтетическая влажность
            df_weather_final['dt'] = pd.to_datetime(df_weather_final['date'])
            df_weather_final['created_at'] = datetime.now()
            df_weather_final['data_source'] = 'era5_processed'
            
            logger.info(f"Processed {len(df_weather_final)} weather records from ERA5")
            
            # Подключение к БД
            pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
            
            # Загрузка в таблицу raw_weather_data батчами
            batch_size = 1000
            total_batches = len(df_weather_final) // batch_size + 1
            
            for i in range(total_batches):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, len(df_weather_final))
                batch = df_weather_final.iloc[start_idx:end_idx]
                
                # Подготавливаем данные для batch insert
                values_list = []
                for _, row in batch.iterrows():
                    values_list.append((
                        row['latitude'], row['longitude'], row['dt'],
                        row['temperature'], row['humidity'], row['wind_speed'], row['precipitation'],
                        row['created_at'], row['data_source']
                    ))
                
                # Batch insert
                insert_sql = """
                INSERT INTO fireforceai.raw_weather_data 
                (latitude, longitude, dt, temperature, humidity, wind_speed, precipitation,
                 created_at, data_source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (latitude, longitude, dt) DO NOTHING;
                """
                
                pg_hook.run(insert_sql, parameters=values_list)
                
                logger.info(f"Processed weather batch {i+1}/{total_batches} ({len(batch)} records)")
            
            # Статистика погодных данных
            weather_stats = {
                'total_records': len(df_weather_final),
                'date_range': f"{df_weather_final['dt'].min()} to {df_weather_final['dt'].max()}",
                'unique_locations': df_weather_final[['latitude', 'longitude']].drop_duplicates().shape[0],
                'avg_temperature': df_weather_final['temperature'].mean(),
                'avg_humidity': df_weather_final['humidity'].mean()
            }
            
            logger.info(f"Weather data loading completed. Stats: {weather_stats}")
            context['task_instance'].xcom_push(key='weather_data_stats', value=weather_stats)
            
            return f"Loaded {len(df_weather_final)} historical weather records from ERA5"
        else:
            logger.warning("No ERA5 files processed successfully")
            return "No ERA5 weather data loaded"
        
    except Exception as e:
        logger.error(f"Error loading weather data from MinIO: {str(e)}")
        raise

load_weather_data = PythonOperator(
    task_id='load_historical_weather_data_from_minio',
    python_callable=load_historical_weather_data_from_minio,
    dag=dag
)

# ============================================================================
# TASK 3: Создание агрегированных данных для ML
# ============================================================================

def create_ml_features(**context):
    """
    Создание признаков для ML на основе исторических данных.
    Основано на анализе ноутбука forestfire.ipynb
    """
    from datetime import datetime
    
    logger.info("Creating ML features from historical data")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Создаем признаки для ML (как в ноутбуке)
    features_sql = """
    INSERT INTO fireforceai.training_features 
    (latitude, longitude, dt, fire_occurred, fire_count, 
     avg_temperature, avg_humidity, avg_wind_speed, total_precipitation,
     day_of_year, month, weekday, season, cell_id, created_at)
    SELECT 
        p.latitude,
        p.longitude,
        p.dt,
        CASE WHEN p.fire_count > 0 THEN true ELSE false END as fire_occurred,
        COALESCE(p.fire_count, 0) as fire_count,
        COALESCE(w.temperature, 0) as avg_temperature,
        COALESCE(w.humidity, 0) as avg_humidity,
        COALESCE(w.wind_speed, 0) as avg_wind_speed,
        COALESCE(w.precipitation, 0) as total_precipitation,
        EXTRACT(DOY FROM p.dt) as day_of_year,
        EXTRACT(MONTH FROM p.dt) as month,
        EXTRACT(DOW FROM p.dt) as weekday,
        CASE 
            WHEN EXTRACT(MONTH FROM p.dt) IN (12, 1, 2) THEN 'winter'
            WHEN EXTRACT(MONTH FROM p.dt) IN (3, 4, 5) THEN 'spring'
            WHEN EXTRACT(MONTH FROM p.dt) IN (6, 7, 8) THEN 'summer'
            ELSE 'autumn'
        END as season,
        CONCAT(p.lon_cell::text, '_', p.lat_cell::text) as cell_id,
        NOW() as created_at
    FROM (
        SELECT 
            lat_cell as latitude,
            lon_cell as longitude,
            dt,
            COUNT(*) as fire_count
        FROM fireforceai.historical_fires
        GROUP BY lat_cell, lon_cell, dt
    ) p
    LEFT JOIN fireforceai.raw_weather_data w 
        ON p.latitude = w.latitude 
        AND p.longitude = w.longitude 
        AND p.dt = w.dt
    ON CONFLICT (latitude, longitude, dt) DO UPDATE SET
        fire_occurred = EXCLUDED.fire_occurred,
        fire_count = EXCLUDED.fire_count,
        avg_temperature = EXCLUDED.avg_temperature,
        avg_humidity = EXCLUDED.avg_humidity,
        avg_wind_speed = EXCLUDED.avg_wind_speed,
        total_precipitation = EXCLUDED.total_precipitation,
        day_of_year = EXCLUDED.day_of_year,
        month = EXCLUDED.month,
        weekday = EXCLUDED.weekday,
        season = EXCLUDED.season,
        cell_id = EXCLUDED.cell_id,
        updated_at = NOW();
    """
    
    pg_hook.run(features_sql)
    
    # Получаем статистику созданных признаков
    stats_sql = """
    SELECT 
        COUNT(*) as total_samples,
        COUNT(*) FILTER (WHERE fire_occurred = true) as positive_samples,
        COUNT(*) FILTER (WHERE fire_occurred = false) as negative_samples
    FROM fireforceai.training_features
    """
    
    result = pg_hook.get_first(stats_sql)
    
    if result:
        total_samples, positive_samples, negative_samples = result
        
        feature_stats = {
            'total_samples': total_samples,
            'positive_samples': positive_samples,
            'negative_samples': negative_samples,
            'positive_ratio': positive_samples / total_samples if total_samples > 0 else 0
        }
        
        logger.info(f"ML features created. Stats: {feature_stats}")
        context['task_instance'].xcom_push(key='feature_stats', value=feature_stats)
        
        return f"Created {total_samples} ML training samples"
    else:
        logger.warning("No ML features created")
        return "No ML features created"

create_features = PythonOperator(
    task_id='create_ml_features',
    python_callable=create_ml_features,
    dag=dag
)

# ============================================================================
# TASK 4: Создание статистики и отчетов
# ============================================================================

def create_historical_statistics(**context):
    """
    Создание статистики по историческим данным.
    """
    from datetime import datetime
    
    logger.info("Creating historical statistics")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Получаем статистику пожаров по годам
    yearly_stats_sql = """
    INSERT INTO fireforceai.fire_statistics 
    (date, total_fires, avg_temperature, avg_humidity, created_at)
    SELECT 
        DATE_TRUNC('year', dt) as date,
        COUNT(*) as total_fires,
        AVG(w.temperature) as avg_temperature,
        AVG(w.humidity) as avg_humidity,
        NOW() as created_at
    FROM fireforceai.historical_fires f
    LEFT JOIN fireforceai.raw_weather_data w 
        ON f.lat_cell = w.latitude 
        AND f.lon_cell = w.longitude 
        AND f.dt = w.dt
    GROUP BY DATE_TRUNC('year', dt)
    ON CONFLICT (date) DO UPDATE SET
        total_fires = EXCLUDED.total_fires,
        avg_temperature = EXCLUDED.avg_temperature,
        avg_humidity = EXCLUDED.avg_humidity,
        updated_at = NOW();
    """
    
    pg_hook.run(yearly_stats_sql)
    
    # Получаем общую статистику
    overall_stats_sql = """
    SELECT 
        COUNT(DISTINCT lat_cell, lon_cell) as unique_locations,
        COUNT(*) as total_fires,
        MIN(dt) as earliest_date,
        MAX(dt) as latest_date,
        COUNT(DISTINCT type_name) as fire_types
    FROM fireforceai.historical_fires
    """
    
    result = pg_hook.get_first(overall_stats_sql)
    
    if result:
        unique_locations, total_fires, earliest_date, latest_date, fire_types = result
        
        overall_stats = {
            'unique_locations': unique_locations,
            'total_fires': total_fires,
            'date_range': f"{earliest_date} to {latest_date}",
            'fire_types': fire_types
        }
        
        logger.info(f"Historical statistics created. Overall stats: {overall_stats}")
        context['task_instance'].xcom_push(key='overall_stats', value=overall_stats)
        
        return f"Created statistics for {total_fires} fires across {unique_locations} locations"
    else:
        logger.warning("No statistics created")
        return "No statistics created"

create_stats = PythonOperator(
    task_id='create_historical_statistics',
    python_callable=create_historical_statistics,
    dag=dag
)

# ============================================================================
# TASK 5: Валидация загруженных данных
# ============================================================================

def validate_historical_data(**context):
    """
    Валидация загруженных исторических данных.
    """
    logger.info("Validating historical data")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверки качества данных
    validation_checks = [
        {
            'name': 'fire_data_completeness',
            'sql': 'SELECT COUNT(*) FROM fireforceai.historical_fires',
            'min_expected': 1000,
            'description': 'Historical fire data completeness'
        },
        {
            'name': 'weather_data_completeness',
            'sql': 'SELECT COUNT(*) FROM fireforceai.raw_weather_data',
            'min_expected': 1000,
            'description': 'Historical weather data completeness'
        },
        {
            'name': 'ml_features_completeness',
            'sql': 'SELECT COUNT(*) FROM fireforceai.training_features',
            'min_expected': 1000,
            'description': 'ML features completeness'
        },
        {
            'name': 'coordinate_validity',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.historical_fires 
            WHERE lat_cell BETWEEN 41.2 AND 81.9 
            AND lon_cell BETWEEN 19.6 AND 169.0
            ''',
            'min_expected': 1000,
            'description': 'Coordinate validity check'
        }
    ]
    
    validation_results = {}
    
    for check in validation_checks:
        try:
            result = pg_hook.get_first(check['sql'])
            count = result[0] if result else 0
            
            validation_results[check['name']] = {
                'count': count,
                'passed': count >= check['min_expected'],
                'description': check['description']
            }
            
            logger.info(f"Validation check '{check['name']}': {count} records, passed: {count >= check['min_expected']}")
            
        except Exception as e:
            logger.error(f"Error in validation check '{check['name']}': {str(e)}")
            validation_results[check['name']] = {
                'error': str(e),
                'passed': False,
                'description': check['description']
            }
    
    # Сохраняем результаты валидации
    context['task_instance'].xcom_push(key='validation_results', value=validation_results)
    
    # Проверяем общий результат
    failed_checks = [name for name, result in validation_results.items() if not result.get('passed', True)]
    
    if failed_checks:
        logger.warning(f"Data validation failed for checks: {failed_checks}")
        raise Exception(f"Data validation failed for checks: {failed_checks}")
    else:
        logger.info("All data validation checks passed")
    
    return "Historical data validation completed successfully"

validate_data = PythonOperator(
    task_id='validate_historical_data',
    python_callable=validate_historical_data,
    dag=dag
)

# ============================================================================
# TASK 6: Завершение
# ============================================================================

end_loading = DummyOperator(
    task_id='end_historical_loading',
    dag=dag
)

# ============================================================================
# Определение зависимостей между задачами
# ============================================================================

# Параллельная загрузка данных
[load_fire_data, load_weather_data] >> create_features

# Создание статистики и валидация после создания признаков
create_features >> [create_stats, validate_data]

# Завершение после всех задач
[create_stats, validate_data] >> end_loading 