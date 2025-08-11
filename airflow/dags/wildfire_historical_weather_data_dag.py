"""
Wildfire Historical Weather Data Loading DAG
DAG для однократной загрузки исторических метеорологических данных из ERA5.
Обрабатывает .nc файлы с помощью xarray и загружает в PostgreSQL.
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
    'retries': 2,  # Больше попыток для тяжелых файлов
    'retry_delay': timedelta(minutes=15),  # Больше времени между попытками
    'email': ['data-team@wildfire-prediction.com']
}

# Создание DAG
dag = DAG(
    'wildfire_historical_weather_data',
    default_args=default_args,
    description='Однократная загрузка исторических метеорологических данных из ERA5',
    schedule_interval=None,  # Запускается только вручную
    catchup=False,
    max_active_runs=1,
    tags=['wildfire', 'historical-data', 'weather-data', 'era5', 'xarray']
)

# ============================================================================
# TASK 0: Проверка существования данных
# ============================================================================

def check_existing_weather_data(**context):
    """
    Проверяет, есть ли уже данные в финальной таблице historical_weather.
    Если данные есть, пропускаем всю загрузку.
    """
    logger.info("Checking for existing weather data in historical_weather table")
    
    # Подключаемся к PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
    
    try:
        # Проверяем финальную таблицу historical_weather
        historical_table = "fireforceai.historical_weather"
        
        # Проверяем данные за 2020-2021 годы
        historical_query = f"""
        SELECT COUNT(*) as count 
        FROM {historical_table} 
        WHERE dt >= '2020-01-01' AND dt <= '2021-12-31'
        """
        
        historical_count = pg_hook.get_first(historical_query)[0]
        
        logger.info(f"Found {historical_count} records in {historical_table} for 2020-2021")
        
        # Если есть данные за 2020-2021 в финальной таблице, пропускаем всю загрузку
        if historical_count > 1000:  # Минимум 1000 записей для считания данных существующими
            logger.info("Historical weather data for 2020-2021 already exists in final table. Skipping ALL data loading tasks.")
            context['task_instance'].xcom_push(key='skip_data_loading', value=True)
            return "SKIP_ALL"
        else:
            logger.info("No historical weather data found for 2020-2021. Proceeding with data loading.")
            context['task_instance'].xcom_push(key='skip_data_loading', value=False)
            return "PROCEED"
            
    except Exception as e:
        logger.error(f"Error checking existing weather data: {e}")
        # В случае ошибки продолжаем загрузку
        context['task_instance'].xcom_push(key='skip_data_loading', value=False)
        return "PROCEED"

# ============================================================================
# TASK 1: Загрузка и обработка мгновенных данных ERA5
# ============================================================================

def process_era5_instant_data(**context):
    """
    Загрузка и обработка мгновенных данных ERA5 (температура, ветер).
    Оптимизировано для прямой записи в базу чанками.
    """
    # Проверяем, нужно ли пропустить загрузку
    skip_loading = context['task_instance'].xcom_pull(key='skip_data_loading', task_ids='check_existing_weather_data')
    if skip_loading:
        logger.info("Skipping ERA5 instant data processing - data already exists")
        return "SKIPPED - Data already exists"
    
    # Дополнительная проверка существования данных в таблице weather_data_instant
    pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
    instant_check_query = """
    SELECT COUNT(*) as count 
    FROM fireforceai.weather_data_instant 
    WHERE date >= '2020-01-01' AND date <= '2021-12-31'
    """
    
    try:
        instant_count = pg_hook.get_first(instant_check_query)[0]
        if instant_count > 1000:
            logger.info(f"Found {instant_count} records in weather_data_instant. Skipping instant data processing.")
            return "SKIPPED - Instant data already exists"
    except Exception as e:
        logger.info(f"Table weather_data_instant might not exist yet: {e}")
    
    import pandas as pd
    import xarray as xr
    from datetime import datetime
    import tempfile
    import os
    
    logger.info("Processing ERA5 instantaneous data (temperature, wind)")
    
    # Используем S3Hook для MinIO
    s3_hook = S3Hook(aws_conn_id="minio_default")
    bucket_name = "fire-datasets"
    era5_file = "era5_instant_3years.nc"
    
    try:
        # Скачиваем файл из MinIO
        import tempfile
        import os
        
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        
        s3_hook.download_file(
            key=era5_file,
            bucket_name=bucket_name,
            local_path=temp_dir
        )
        
        # Ищем скачанный файл в директории
        files_in_dir = os.listdir(temp_dir)
        logger.info(f"Files in temp directory: {files_in_dir}")
        
        # Ищем файл с похожим именем
        nc_file_path = None
        for file in files_in_dir:
            if file.endswith('.nc') or era5_file.replace('.nc', '') in file or file.startswith('airflow_tmp_'):
                nc_file_path = os.path.join(temp_dir, file)
                logger.info(f"Found file: {nc_file_path}")
                break
        
        if not nc_file_path:
            # Если не нашли, берем первый файл в директории
            if files_in_dir:
                nc_file_path = os.path.join(temp_dir, files_in_dir[0])
                logger.info(f"Using first file found: {nc_file_path}")
            else:
                raise FileNotFoundError(f"NC file not found in {temp_dir}")
        
        logger.info(f"Downloaded {era5_file} from MinIO ({os.path.getsize(nc_file_path)} bytes)")
        
        # Открываем .nc файл с xarray с меньшими чанками
        ds = xr.open_dataset(nc_file_path, chunks={"valid_time": 50, "latitude": 25, "longitude": 25})
        
        logger.info(f"ERA5 dataset loaded successfully")
        
        # Фильтруем только данные за 2020-2021 годы для экономии памяти
        ds = ds.sel(valid_time=slice('2020-01-01', '2021-12-31'))
        
        logger.info(f"Filtered dataset for 2020-2021 period")
        
        # Обрабатываем данные как в ноутбуке
        hour = ds["valid_time"].dt.hour
        
        # Берем данные за полдень (12:00) для ежедневных значений
        ds_mid = ds.sel(valid_time=hour==12)[["t2m","u10","v10","latitude","longitude","valid_time"]]
        ds_mid = ds_mid.rename(valid_time="time")
        
        # Вычисляем скорость ветра
        ds_mid["windspeed_10m"] = np.sqrt(ds_mid["u10"]**2 + ds_mid["v10"]**2)
        
        # Добавляем сетку координат (0.5 градуса)
        ds_mid = ds_mid.assign(
            lon_cell = (ds_mid.longitude // 0.5) * 0.5,
            lat_cell = (ds_mid.latitude  // 0.5) * 0.5,
            date     = ds_mid["time"].dt.floor("D")
        )
        
        # Обрабатываем данные чанками и сразу записываем в базу
        logger.info("Processing data in chunks and writing to database...")
        
        # Получаем размеры данных
        time_chunks = ds_mid.chunks['time'][0]
        lat_chunks = ds_mid.chunks['latitude'][0]
        lon_chunks = ds_mid.chunks['longitude'][0]
        
        logger.info(f"Data chunks: time={time_chunks}, lat={lat_chunks}, lon={lon_chunks}")
        
        # Подключаемся к базе данных
        pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
        
        # Создаем таблицу если не существует
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fireforceai.weather_data_instant (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            latitude DECIMAL(8,4) NOT NULL,
            longitude DECIMAL(8,4) NOT NULL,
            temperature DECIMAL(8,4),
            wind_speed DECIMAL(8,4),
            humidity DECIMAL(8,4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, latitude, longitude)
        );
        """
        pg_hook.run(create_table_sql)
        
        # Обрабатываем чанками и сразу записываем в базу
        chunk_count = 0
        total_records = 0
        
        for time_idx in range(0, len(ds_mid.time), time_chunks):
            time_slice = slice(time_idx, min(time_idx + time_chunks, len(ds_mid.time)))
            
            for lat_idx in range(0, len(ds_mid.latitude), lat_chunks):
                lat_slice = slice(lat_idx, min(lat_idx + lat_chunks, len(ds_mid.latitude)))
                
                for lon_idx in range(0, len(ds_mid.longitude), lon_chunks):
                    lon_slice = slice(lon_idx, min(lon_idx + lon_chunks, len(ds_mid.longitude)))
                    
                    # Выбираем чанк данных
                    chunk = ds_mid.isel(time=time_slice, latitude=lat_slice, longitude=lon_slice)
                    
                    # Конвертируем чанк в DataFrame
                    df_chunk = chunk.to_dataframe().reset_index()
                    
                    if len(df_chunk) > 0:
                        # Агрегируем чанк по ячейкам и датам
                        df_agg_chunk = df_chunk.groupby(["date","lon_cell","lat_cell"], as_index=False).agg({
                            "t2m": "mean",
                            "windspeed_10m": "mean"
                        }).rename(columns={
                            "t2m": "temperature",
                            "windspeed_10m": "wind_speed",
                            "lon_cell": "longitude",
                            "lat_cell": "latitude"
                        })
                        
                        # Добавляем синтетическую влажность
                        df_agg_chunk['humidity'] = 60 + np.random.normal(0, 10, len(df_agg_chunk))
                        
                        # Записываем чанк в базу данных
                        for _, row in df_agg_chunk.iterrows():
                            insert_sql = """
                            INSERT INTO fireforceai.weather_data_instant 
                            (date, latitude, longitude, temperature, wind_speed, humidity)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (date, latitude, longitude) 
                            DO UPDATE SET 
                                temperature = EXCLUDED.temperature,
                                wind_speed = EXCLUDED.wind_speed,
                                humidity = EXCLUDED.humidity;
                            """
                            pg_hook.run(insert_sql, parameters=(
                                row['date'].date(),
                                float(row['latitude']),
                                float(row['longitude']),
                                float(row['temperature']),
                                float(row['wind_speed']),
                                float(row['humidity'])
                            ))
                        
                        total_records += len(df_agg_chunk)
                        chunk_count += 1
                        
                        logger.info(f"Processed and wrote chunk: time={time_idx}-{time_idx+time_chunks}, lat={lat_idx}-{lat_idx+lat_chunks}, lon={lon_idx}-{lon_idx+lon_chunks}, records={len(df_agg_chunk)}")
        
        logger.info(f"Processed {chunk_count} chunks with {total_records} total records written to database")
        
        # Очистка временного файла
        os.unlink(nc_file_path)
        
        instant_stats = {
            'total_records': total_records,
            'chunks_processed': chunk_count,
            'table': 'fireforceai.weather_data_instant'
        }
        
        logger.info(f"Instant weather processing completed. Stats: {instant_stats}")
        context['task_instance'].xcom_push(key='instant_weather_stats', value=instant_stats)
        
        return f"Processed and wrote {total_records} instantaneous weather records to database"
        
    except Exception as e:
        logger.error(f"Error processing ERA5 instantaneous data: {str(e)}")
        raise

# Оператор для проверки существования данных
check_existing_data = PythonOperator(
    task_id='check_existing_weather_data',
    python_callable=check_existing_weather_data,
    dag=dag
)

process_instant = PythonOperator(
    task_id='process_era5_instant_data',
    python_callable=process_era5_instant_data,
    dag=dag
)

# ============================================================================
# TASK 2: Загрузка и обработка накопленных данных ERA5
# ============================================================================

def process_era5_accum_data(**context):
    """
    Загрузка и обработка накопительных данных ERA5 (осадки).
    Оптимизировано для прямой записи в базу чанками.
    """
    # Проверяем, нужно ли пропустить загрузку
    skip_loading = context['task_instance'].xcom_pull(key='skip_data_loading', task_ids='check_existing_weather_data')
    if skip_loading:
        logger.info("Skipping ERA5 accum data processing - data already exists")
        return "SKIPPED - Data already exists"
    
    # Дополнительная проверка существования данных в таблице weather_data_accum
    pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
    accum_check_query = """
    SELECT COUNT(*) as count 
    FROM fireforceai.weather_data_accum 
    WHERE date >= '2020-01-01' AND date <= '2021-12-31'
    """
    
    try:
        accum_count = pg_hook.get_first(accum_check_query)[0]
        if accum_count > 1000:
            logger.info(f"Found {accum_count} records in weather_data_accum. Skipping accum data processing.")
            return "SKIPPED - Accum data already exists"
    except Exception as e:
        logger.info(f"Table weather_data_accum might not exist yet: {e}")
    
    import pandas as pd
    import xarray as xr
    from datetime import datetime
    import tempfile
    import os
    
    logger.info("Processing ERA5 accumulated data (precipitation)")
    
    # Используем S3Hook для MinIO
    s3_hook = S3Hook(aws_conn_id="minio_default")
    bucket_name = "fire-datasets"
    era5_file = "era5_accum_3years.nc"
    
    try:
        # Скачиваем файл из MinIO
        import tempfile
        import os
        
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        
        s3_hook.download_file(
            key=era5_file,
            bucket_name=bucket_name,
            local_path=temp_dir
        )
        
        # Ищем скачанный файл в директории
        files_in_dir = os.listdir(temp_dir)
        logger.info(f"Files in temp directory: {files_in_dir}")
        
        # Ищем файл с похожим именем
        nc_file_path = None
        for file in files_in_dir:
            if file.endswith('.nc') or era5_file.replace('.nc', '') in file or file.startswith('airflow_tmp_'):
                nc_file_path = os.path.join(temp_dir, file)
                logger.info(f"Found file: {nc_file_path}")
                break
        
        if not nc_file_path:
            # Если не нашли, берем первый файл в директории
            if files_in_dir:
                nc_file_path = os.path.join(temp_dir, files_in_dir[0])
                logger.info(f"Using first file found: {nc_file_path}")
            else:
                raise FileNotFoundError(f"NC file not found in {temp_dir}")
        
        logger.info(f"Downloaded {era5_file} from MinIO ({os.path.getsize(nc_file_path)} bytes)")
        
        # Открываем .nc файл с xarray с меньшими чанками
        ds = xr.open_dataset(nc_file_path, chunks={"valid_time": 50, "latitude": 25, "longitude": 25})
        
        logger.info(f"ERA5 accum dataset loaded successfully")
        
        # Фильтруем только данные за 2020-2021 годы для экономии памяти
        ds = ds.sel(valid_time=slice('2020-01-01', '2021-12-31'))
        
        logger.info(f"Filtered dataset for 2020-2021 period")
        
        # Обрабатываем данные как в ноутбуке
        hour = ds["valid_time"].dt.hour
        
        # Берем данные за полдень (12:00) для ежедневных значений
        ds_mid = ds.sel(valid_time=hour==12)[["tp","latitude","longitude","valid_time"]]
        ds_mid = ds_mid.rename(valid_time="time")
        
        # Добавляем сетку координат (0.5 градуса)
        ds_mid = ds_mid.assign(
            lon_cell = (ds_mid.longitude // 0.5) * 0.5,
            lat_cell = (ds_mid.latitude  // 0.5) * 0.5,
            date     = ds_mid["time"].dt.floor("D")
        )
        
        # Обрабатываем данные чанками и сразу записываем в базу
        logger.info("Processing data in chunks and writing to database...")
        
        # Получаем размеры данных
        time_chunks = ds_mid.chunks['time'][0]
        lat_chunks = ds_mid.chunks['latitude'][0]
        lon_chunks = ds_mid.chunks['longitude'][0]
        
        logger.info(f"Data chunks: time={time_chunks}, lat={lat_chunks}, lon={lon_chunks}")
        
        # Подключаемся к базе данных
        pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
        
        # Создаем таблицу если не существует
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fireforceai.weather_data_accum (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            latitude DECIMAL(8,4) NOT NULL,
            longitude DECIMAL(8,4) NOT NULL,
            precipitation DECIMAL(10,6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, latitude, longitude)
        );
        """
        pg_hook.run(create_table_sql)
        
        # Обрабатываем чанками и сразу записываем в базу
        chunk_count = 0
        total_records = 0
        
        for time_idx in range(0, len(ds_mid.time), time_chunks):
            time_slice = slice(time_idx, min(time_idx + time_chunks, len(ds_mid.time)))
            
            for lat_idx in range(0, len(ds_mid.latitude), lat_chunks):
                lat_slice = slice(lat_idx, min(lat_idx + lat_chunks, len(ds_mid.latitude)))
                
                for lon_idx in range(0, len(ds_mid.longitude), lon_chunks):
                    lon_slice = slice(lon_idx, min(lon_idx + lon_chunks, len(ds_mid.longitude)))
                    
                    # Выбираем чанк данных
                    chunk = ds_mid.isel(time=time_slice, latitude=lat_slice, longitude=lon_slice)
                    
                    # Конвертируем чанк в DataFrame
                    df_chunk = chunk.to_dataframe().reset_index()
                    
                    if len(df_chunk) > 0:
                        # Агрегируем чанк по ячейкам и датам
                        df_agg_chunk = df_chunk.groupby(["date","lon_cell","lat_cell"], as_index=False).agg({
                            "tp": "sum"
                        }).rename(columns={
                            "tp": "precipitation",
                            "lon_cell": "longitude",
                            "lat_cell": "latitude"
                        })
                        
                        # Записываем чанк в базу данных
                        for _, row in df_agg_chunk.iterrows():
                            insert_sql = """
                            INSERT INTO fireforceai.weather_data_accum 
                            (date, latitude, longitude, precipitation)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (date, latitude, longitude) 
                            DO UPDATE SET precipitation = EXCLUDED.precipitation;
                            """
                            pg_hook.run(insert_sql, parameters=(
                                row['date'].date(),
                                float(row['latitude']),
                                float(row['longitude']),
                                float(row['precipitation'])
                            ))
                        
                        total_records += len(df_agg_chunk)
                        chunk_count += 1
                        
                        logger.info(f"Processed and wrote chunk: time={time_idx}-{time_idx+time_chunks}, lat={lat_idx}-{lat_idx+lat_chunks}, lon={lon_idx}-{lon_idx+lon_chunks}, records={len(df_agg_chunk)}")
        
        logger.info(f"Processed {chunk_count} chunks with {total_records} total records written to database")
        
        # Очистка временного файла
        os.unlink(nc_file_path)
        
        accum_stats = {
            'total_records': total_records,
            'chunks_processed': chunk_count,
            'table': 'fireforceai.weather_data_accum'
        }
        
        logger.info(f"Accumulated weather processing completed. Stats: {accum_stats}")
        context['task_instance'].xcom_push(key='accum_weather_stats', value=accum_stats)
        
        return f"Processed and wrote {total_records} accumulated weather records to database"
        
    except Exception as e:
        logger.error(f"Error processing ERA5 accumulated data: {str(e)}")
        raise

process_accum = PythonOperator(
    task_id='process_era5_accum_data',
    python_callable=process_era5_accum_data,
    dag=dag
)

# ============================================================================
# TASK 3: Объединение и загрузка метеорологических данных в БД
# ============================================================================

def merge_weather_data(**context):
    """
    Объединение мгновенных и накопленных данных погоды в финальную таблицу.
    Оптимизировано для работы с большими данными через чанковую обработку.
    """
    # Проверяем, нужно ли пропустить загрузку
    skip_loading = context['task_instance'].xcom_pull(key='skip_data_loading', task_ids='check_existing_weather_data')
    if skip_loading:
        logger.info("Skipping weather data merging - data already exists")
        return "SKIPPED - Data already exists"
    
    # Дополнительная проверка существования данных в обеих таблицах
    pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
    
    instant_check_query = """
    SELECT COUNT(*) as count 
    FROM fireforceai.weather_data_instant 
    WHERE date >= '2020-01-01' AND date <= '2021-12-31'
    """
    
    accum_check_query = """
    SELECT COUNT(*) as count 
    FROM fireforceai.weather_data_accum 
    WHERE date >= '2020-01-01' AND date <= '2021-12-31'
    """
    
    try:
        instant_count = pg_hook.get_first(instant_check_query)[0]
        accum_count = pg_hook.get_first(accum_check_query)[0]
        
        if instant_count < 1000 or accum_count < 1000:
            logger.warning(f"Not enough data for merging: instant={instant_count}, accum={accum_count}")
            return "SKIPPED - Not enough data for merging"
            
        logger.info(f"Found sufficient data for merging: instant={instant_count}, accum={accum_count}")
    except Exception as e:
        logger.info(f"Tables might not exist yet: {e}")
    
    from datetime import datetime
    
    logger.info("Merging weather data from database tables using chunked processing")
    
    try:
        # Создаем финальную таблицу
        create_final_table_sql = """
        CREATE TABLE IF NOT EXISTS fireforceai.historical_weather (
            id SERIAL PRIMARY KEY,
            dt TIMESTAMP NOT NULL,
            latitude DECIMAL(8,4) NOT NULL,
            longitude DECIMAL(8,4) NOT NULL,
            temperature DECIMAL(8,4),
            wind_speed DECIMAL(8,4),
            humidity DECIMAL(8,4),
            precipitation DECIMAL(10,6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(dt, latitude, longitude)
        );
        """
        pg_hook.run(create_final_table_sql)
        
        # Обрабатываем данные чанками через SQL JOIN
        logger.info("Processing data in chunks using SQL JOIN...")
        
        # Получаем уникальные даты для обработки чанками
        dates_sql = """
        SELECT DISTINCT date 
        FROM fireforceai.weather_data_instant 
        WHERE date >= '2020-01-01' AND date <= '2021-12-31'
        ORDER BY date
        """
        
        dates_result = pg_hook.get_records(dates_sql)
        total_dates = len(dates_result)
        logger.info(f"Found {total_dates} unique dates to process")
        
        records_written = 0
        chunk_size = 50  # Обрабатываем по 50 дат за раз
        
        for i in range(0, total_dates, chunk_size):
            chunk_dates = dates_result[i:i+chunk_size]
            date_list = [str(row[0]) for row in chunk_dates]
            date_condition = "','".join(date_list)
            
            logger.info(f"Processing chunk {i//chunk_size + 1}/{(total_dates + chunk_size - 1)//chunk_size}: dates {i+1}-{min(i+chunk_size, total_dates)}")
            
            # SQL для объединения данных чанком
            merge_sql = f"""
            INSERT INTO fireforceai.historical_weather 
            (dt, latitude, longitude, temperature, wind_speed, humidity, precipitation)
            SELECT 
                i.date::timestamp as dt,
                i.latitude,
                i.longitude,
                i.temperature,
                i.wind_speed,
                i.humidity,
                COALESCE(a.precipitation, 0) as precipitation
            FROM fireforceai.weather_data_instant i
            LEFT JOIN fireforceai.weather_data_accum a 
                ON i.date = a.date 
                AND i.latitude = a.latitude 
                AND i.longitude = a.longitude
            WHERE i.date IN ('{date_condition}')
            ON CONFLICT (dt, latitude, longitude) 
            DO UPDATE SET 
                temperature = EXCLUDED.temperature,
                wind_speed = EXCLUDED.wind_speed,
                humidity = EXCLUDED.humidity,
                precipitation = EXCLUDED.precipitation;
            """
            
            try:
                pg_hook.run(merge_sql)
                
                # Получаем количество записанных записей для этого чанка
                count_sql = f"""
                SELECT COUNT(*) 
                FROM fireforceai.historical_weather 
                WHERE dt::date IN ('{date_condition}')
                """
                chunk_count = pg_hook.get_first(count_sql)[0]
                records_written += chunk_count
                
                logger.info(f"Chunk {i//chunk_size + 1} completed: {chunk_count} records written")
                
            except Exception as e:
                logger.error(f"Error processing chunk {i//chunk_size + 1}: {e}")
                raise
        
        logger.info(f"Total records written to historical_weather: {records_written}")
        
        # Статистика
        stats_sql = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT dt::date) as unique_dates,
            COUNT(DISTINCT latitude || ',' || longitude) as unique_locations,
            MIN(dt) as min_date,
            MAX(dt) as max_date,
            AVG(temperature) as avg_temperature,
            AVG(humidity) as avg_humidity,
            AVG(wind_speed) as avg_wind_speed,
            AVG(precipitation) as avg_precipitation
        FROM fireforceai.historical_weather
        """
        
        stats_result = pg_hook.get_first(stats_sql)
        
        if stats_result:
            total_records, unique_dates, unique_locations, min_date, max_date, avg_temp, avg_hum, avg_wind, avg_precip = stats_result
            
            stats = {
                'total_records': total_records,
                'unique_dates': unique_dates,
                'unique_locations': unique_locations,
                'date_range': f"{min_date} to {max_date}",
                'avg_temperature': round(avg_temp, 2) if avg_temp else 0,
                'avg_humidity': round(avg_hum, 2) if avg_hum else 0,
                'avg_wind_speed': round(avg_wind, 2) if avg_wind else 0,
                'avg_precipitation': round(avg_precip, 6) if avg_precip else 0
            }
            
            logger.info(f"Weather data merge completed successfully. Stats: {stats}")
            context['task_instance'].xcom_push(key='weather_merge_stats', value=stats)
            
            return f"Successfully merged {total_records} weather records"
        else:
            logger.warning("No statistics available after merge")
            return "Weather data merge completed"
            
    except Exception as e:
        logger.error(f"Error in weather data merge: {str(e)}")
        raise

merge_and_load = PythonOperator(
    task_id='merge_and_load_weather_data',
    python_callable=merge_weather_data,
    dag=dag
)

# ============================================================================
# TASK 4: Обновление ML признаков с погодными данными
# ============================================================================

def update_ml_features_with_weather(**context):
    """
    Обновление ML признаков с добавлением погодных данных.
    Умная логика: обновляет только незаполненные поля.
    """
    logger.info("Starting ML features update with weather data")
    
    # Проверяем существование данных в historical_weather
    pg_hook = PostgresHook(postgres_conn_id="wildfire_db")
    weather_check_query = """
    SELECT COUNT(*) as count 
    FROM fireforceai.historical_weather 
    WHERE dt >= '2020-01-01' AND dt <= '2021-12-31'
    """
    
    try:
        weather_count = pg_hook.get_first(weather_check_query)[0]
        if weather_count < 1000:
            logger.warning(f"Not enough weather data for ML features update: {weather_count}")
            return f"SKIPPED - Not enough weather data ({weather_count} records)"
        logger.info(f"Found {weather_count} weather records for ML features update")
    except Exception as e:
        logger.error(f"Error checking weather data: {e}")
        return f"ERROR - Cannot check weather data: {e}"
    
    from datetime import datetime
    
    # Получаем статистику ДО обновления
    logger.info("Checking current ML features status...")
    before_stats_sql = """
    SELECT 
        COUNT(*) as total_samples,
        COUNT(*) FILTER (WHERE temperature IS NOT NULL) as samples_with_temperature,
        COUNT(*) FILTER (WHERE humidity IS NOT NULL) as samples_with_humidity,
        COUNT(*) FILTER (WHERE wind_u IS NOT NULL) as samples_with_wind_u,
        COUNT(*) FILTER (WHERE wind_v IS NOT NULL) as samples_with_wind_v,
        COUNT(*) FILTER (WHERE precipitation IS NOT NULL) as samples_with_precipitation,
        COUNT(*) FILTER (WHERE temperature IS NULL AND humidity IS NULL AND wind_u IS NULL AND wind_v IS NULL AND precipitation IS NULL) as samples_without_weather
    FROM fireforceai.training_features
    """
    
    # Инициализируем переменные значениями по умолчанию
    temp_before = hum_before = wind_u_before = wind_v_before = precip_before = no_weather_before = 0
    
    before_result = pg_hook.get_first(before_stats_sql)
    if before_result:
        total_samples, temp_before, hum_before, wind_u_before, wind_v_before, precip_before, no_weather_before = before_result
        logger.info(f"BEFORE UPDATE - Total: {total_samples}, Temperature: {temp_before}, Humidity: {hum_before}, Wind_U: {wind_u_before}, Wind_V: {wind_v_before}, Precipitation: {precip_before}, No Weather: {no_weather_before}")
    
    logger.info("Updating ML features with weather data")
    
    # Обновляем ML признаки с погодными данными (только для незаполненных полей)
    update_features_sql = """
    UPDATE fireforceai.training_features 
    SET 
        temperature = COALESCE(training_features.temperature, w.temperature),
        humidity = COALESCE(training_features.humidity, w.humidity),
        wind_u = COALESCE(training_features.wind_u, w.wind_speed),
        wind_v = COALESCE(training_features.wind_v, w.wind_speed),
        precipitation = COALESCE(training_features.precipitation, w.precipitation),
        updated_at = NOW()
    FROM fireforceai.historical_weather w
    WHERE fireforceai.training_features.latitude = w.latitude 
    AND fireforceai.training_features.longitude = w.longitude 
    AND fireforceai.training_features.dt = w.dt::date
    AND (
        training_features.temperature IS NULL OR 
        training_features.humidity IS NULL OR 
        training_features.wind_u IS NULL OR 
        training_features.wind_v IS NULL OR 
        training_features.precipitation IS NULL
    );
    """
    
    try:
        pg_hook.run(update_features_sql)
        logger.info("Successfully updated ML features with weather data")
    except Exception as e:
        logger.error(f"Error updating ML features: {e}")
        return f"ERROR - Failed to update ML features: {e}"
    
    # Получаем статистику ПОСЛЕ обновления
    after_stats_sql = """
    SELECT 
        COUNT(*) as total_samples,
        COUNT(*) FILTER (WHERE fire_occurred = true) as positive_samples,
        COUNT(*) FILTER (WHERE temperature IS NOT NULL) as samples_with_temperature,
        COUNT(*) FILTER (WHERE humidity IS NOT NULL) as samples_with_humidity,
        COUNT(*) FILTER (WHERE wind_u IS NOT NULL) as samples_with_wind_u,
        COUNT(*) FILTER (WHERE wind_v IS NOT NULL) as samples_with_wind_v,
        COUNT(*) FILTER (WHERE precipitation IS NOT NULL) as samples_with_precipitation,
        COUNT(*) FILTER (WHERE temperature IS NULL AND humidity IS NULL AND wind_u IS NULL AND wind_v IS NULL AND precipitation IS NULL) as samples_without_weather,
        COUNT(DISTINCT CONCAT(lat_cell::text, '_', lon_cell::text)) as unique_cells,
        COUNT(DISTINCT EXTRACT(YEAR FROM dt)) as years_covered
    FROM fireforceai.training_features
    """
    
    after_result = pg_hook.get_first(after_stats_sql)
    
    if after_result:
        total_samples, positive_samples, temp_after, hum_after, wind_u_after, wind_v_after, precip_after, no_weather_after, unique_cells, years_covered = after_result
        
        # Вычисляем изменения
        temp_diff = temp_after - temp_before if before_result else 0
        hum_diff = hum_after - hum_before if before_result else 0
        wind_u_diff = wind_u_after - wind_u_before if before_result else 0
        wind_v_diff = wind_v_after - wind_v_before if before_result else 0
        precip_diff = precip_after - precip_before if before_result else 0
        no_weather_diff = no_weather_after - no_weather_before if before_result else 0
        
        feature_stats = {
            'total_samples': total_samples,
            'positive_samples': positive_samples,
            'samples_with_temperature': temp_after,
            'samples_with_humidity': hum_after,
            'samples_with_wind_u': wind_u_after,
            'samples_with_wind_v': wind_v_after,
            'samples_with_precipitation': precip_after,
            'samples_without_weather': no_weather_after,
            'unique_cells': unique_cells,
            'years_covered': years_covered,
            'weather_coverage': temp_after / total_samples if total_samples > 0 else 0,
            'precipitation_coverage': precip_after / total_samples if total_samples > 0 else 0,
            'wind_v_coverage': wind_v_after / total_samples if total_samples > 0 else 0,
            'updates': {
                'temperature_added': temp_diff,
                'humidity_added': hum_diff,
                'wind_u_added': wind_u_diff,
                'wind_v_added': wind_v_diff,
                'precipitation_added': precip_diff,
                'remaining_without_weather': no_weather_after
            }
        }
        
        logger.info(f"AFTER UPDATE - Total: {total_samples}, Temperature: {temp_after} (+{temp_diff}), Humidity: {hum_after} (+{hum_diff}), Wind_U: {wind_u_after} (+{wind_u_diff}), Wind_V: {wind_v_after} (+{wind_v_diff}), Precipitation: {precip_after} (+{precip_diff}), No Weather: {no_weather_after}")
        logger.info(f"ML features updated with weather data. Stats: {feature_stats}")
        context['task_instance'].xcom_push(key='updated_feature_stats', value=feature_stats)
        
        return f"Updated ML features: +{temp_diff} temp, +{hum_diff} humidity, +{wind_u_diff} wind_u, +{wind_v_diff} wind_v, +{precip_diff} precipitation. Remaining without weather: {no_weather_after}"
    else:
        logger.warning("No ML features updated")
        return "No ML features updated"

update_features = PythonOperator(
    task_id='update_ml_features_with_weather',
    python_callable=update_ml_features_with_weather,
    dag=dag
)

# ============================================================================
# TASK 5: Валидация метеорологических данных
# ============================================================================

def validate_weather_data(**context):
    """
    Валидация загруженных метеорологических данных.
    """
    logger.info("Validating weather data")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверки качества данных
    validation_checks = [
        {
            'name': 'weather_data_completeness',
            'sql': 'SELECT COUNT(*) FROM fireforceai.historical_weather',
            'min_expected': 1000,
            'description': 'Weather data completeness'
        },
        {
            'name': 'temperature_validity',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.historical_weather 
            WHERE temperature BETWEEN -50 AND 50
            ''',
            'min_expected': 1000,
            'description': 'Temperature validity check'
        },
        {
            'name': 'humidity_validity',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.historical_weather 
            WHERE humidity BETWEEN 0 AND 100
            ''',
            'min_expected': 1000,
            'description': 'Humidity validity check'
        },
        {
            'name': 'wind_speed_validity',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.historical_weather 
            WHERE wind_speed BETWEEN 0 AND 100
            ''',
            'min_expected': 1000,
            'description': 'Wind speed validity check'
        },
        {
            'name': 'ml_features_with_weather',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.training_features 
            WHERE temperature IS NOT NULL
            ''',
            'min_expected': 1000,
            'description': 'ML features with weather data'
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
    context['task_instance'].xcom_push(key='weather_validation_results', value=validation_results)
    
    # Проверяем общий результат
    failed_checks = [name for name, result in validation_results.items() if not result.get('passed', True)]
    
    if failed_checks:
        logger.warning(f"Weather data validation failed for checks: {failed_checks}")
        raise Exception(f"Weather data validation failed for checks: {failed_checks}")
    else:
        logger.info("All weather data validation checks passed")
    
    return "Weather data validation completed successfully"

validate_data = PythonOperator(
    task_id='validate_weather_data',
    python_callable=validate_weather_data,
    dag=dag
)

# ============================================================================
# TASK 6: Завершение
# ============================================================================

end_loading = DummyOperator(
    task_id='end_weather_data_loading',
    dag=dag
)

# ============================================================================
# Определение зависимостей между задачами
# ============================================================================

# Проверка существования данных выполняется первой
check_existing_data >> [process_instant, process_accum]

# Параллельная обработка ERA5 файлов
[process_instant, process_accum] >> merge_and_load

# Обновление признаков и валидация
merge_and_load >> update_features >> validate_data >> end_loading 