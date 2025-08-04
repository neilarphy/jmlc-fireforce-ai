"""
Wildfire Historical Fire Data Loading DAG
DAG для однократной загрузки исторических данных о пожарах из CSV.
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
    'wildfire_historical_fire_data',
    default_args=default_args,
    description='Однократная загрузка исторических данных о пожарах из CSV',
    schedule_interval=None,  # Запускается только вручную
    catchup=False,
    max_active_runs=1,
    tags=['wildfire', 'historical-data', 'fire-data', 'csv']
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
        import tempfile
        import os
        
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()
        
        s3_hook.download_file(
            key=file_name,
            bucket_name=bucket_name,
            local_path=temp_dir
        )
        
        fire_data_path = os.path.join(temp_dir, file_name)
        
        logger.info(f"Downloaded {file_name} from MinIO to {fire_data_path}")
        
        # Проверяем, существует ли файл по ожидаемому пути
        if not os.path.exists(fire_data_path):
            # Ищем файл в директории
            files_in_dir = os.listdir(temp_dir)
            logger.info(f"Files in temp directory: {files_in_dir}")
            
            # Ищем файл с похожим именем
            for file in files_in_dir:
                if file.endswith('.csv') or 'russia_fires_hist' in file or file.startswith('airflow_tmp_'):
                    fire_data_path = os.path.join(temp_dir, file)
                    logger.info(f"Found file: {fire_data_path}")
                    break
            else:
                # Если не нашли, берем первый файл в директории
                if files_in_dir:
                    fire_data_path = os.path.join(temp_dir, files_in_dir[0])
                    logger.info(f"Using first file found: {fire_data_path}")
                else:
                    raise FileNotFoundError(f"CSV file not found in {temp_dir}")
        
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
        
        # Проверяем права пользователя
        check_permissions_sql = """
        SELECT current_user, current_database(), current_schema();
        """
        user_info = pg_hook.get_first(check_permissions_sql)
        logger.info(f"Current user: {user_info[0]}, Database: {user_info[1]}, Schema: {user_info[2]}")
        
        # Проверяем права на схему fireforceai
        schema_permissions = pg_hook.get_first("""
            SELECT 
                has_schema_privilege(current_user, 'fireforceai', 'USAGE') as has_usage,
                has_schema_privilege(current_user, 'fireforceai', 'CREATE') as has_create
        """)
        logger.info(f"Schema permissions - Usage: {schema_permissions[0]}, Create: {schema_permissions[1]}")
        
        # Проверяем права на таблицу historical_fires
        table_permissions = pg_hook.get_first("""
            SELECT 
                has_table_privilege(current_user, 'fireforceai.historical_fires', 'INSERT') as has_insert,
                has_table_privilege(current_user, 'fireforceai.historical_fires', 'SELECT') as has_select
        """)
        logger.info(f"Table permissions - Insert: {table_permissions[0]}, Select: {table_permissions[1]}")
        
        # Проверяем существование таблицы
        table_exists = pg_hook.get_first("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'fireforceai' 
                AND table_name = 'historical_fires'
            )
        """)
        logger.info(f"Table fireforceai.historical_fires exists: {table_exists[0]}")
        
        # Проверяем, есть ли уже данные в таблице
        existing_data = pg_hook.get_first("SELECT COUNT(*) FROM fireforceai.historical_fires")
        if existing_data and existing_data[0] > 0:
            logger.info(f"Found {existing_data[0]} existing fire records. Skipping data loading.")
            return f"Skipped loading - {existing_data[0]} records already exist"
        
        # Загрузка в таблицу historical_fires батчами
        batch_size = 1000
        total_batches = len(fire_data) // batch_size + 1
        
        # Определяем SQL для вставки
        insert_sql = """
        INSERT INTO fireforceai.historical_fires 
        (latitude, longitude, dt, type_name, type_id, 
         year, month, weekday, lon_cell, lat_cell,
         created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
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
                    row['created_at']
                ))
            
            # Batch insert
            for values in values_list:
                pg_hook.run(insert_sql, parameters=values)
            
            logger.info(f"Processed batch {i+1}/{total_batches} ({len(batch)} records)")
        
        # Очистка временного файла
        os.unlink(fire_data_path)
        
        # Статистика загруженных данных
        stats = {
            'total_records': len(fire_data),
            'date_range': f"{fire_data['dt'].min()} to {fire_data['dt'].max()}",
            'unique_locations': fire_data[['lon_cell', 'lat_cell']].drop_duplicates().shape[0],
            'fire_types': fire_data['type_name'].nunique(),
            'years_covered': fire_data['year'].nunique(),
            'months_covered': fire_data['month'].nunique()
        }
        
        logger.info(f"Fire data loading completed. Stats: {stats}")
        context['task_instance'].xcom_push(key='fire_data_stats', value=stats)
        
        return f"Loaded {len(fire_data)} historical fire records from CSV"
        
    except Exception as e:
        logger.error(f"Error loading fire data from MinIO: {str(e)}")
        raise

load_fire_data = PythonOperator(
    task_id='load_historical_fire_data_from_minio',
    python_callable=load_historical_fire_data_from_minio,
    dag=dag
)

# ============================================================================
# TASK 2: Генерация негативных примеров для сбалансированного датасета
# ============================================================================

def generate_negative_samples(**context):
    """
    Генерация негативных примеров для сбалансированного датасета.
    Основано на логике из ноутбука forestfire.ipynb
    """
    from datetime import datetime
    import random
    
    logger.info("Generating negative samples for balanced dataset")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем, есть ли уже негативы
    check_negatives_sql = "SELECT COUNT(*) FROM fireforceai.training_features WHERE fire_occurred = false"
    existing_negatives = pg_hook.get_first(check_negatives_sql)[0]
    
    if existing_negatives > 0:
        logger.info(f"Found {existing_negatives} existing negative samples. Skipping generation.")
        return f"Skipped generation - {existing_negatives} negatives already exist"
    
    # Получаем позитивные примеры только за 2020-2021 годы
    pos_samples_sql = """
    SELECT 
        lat_cell as latitude,
        lon_cell as longitude,
        dt,
        EXTRACT(YEAR FROM dt) as year,
        EXTRACT(MONTH FROM dt) as month,
        EXTRACT(DOW FROM dt) as weekday
    FROM fireforceai.historical_fires
    WHERE EXTRACT(YEAR FROM dt) IN (2020, 2021)
    """
    
    pos_data = pg_hook.get_pandas_df(pos_samples_sql)
    n_pos = len(pos_data)
    
    logger.info(f"Found {n_pos} positive samples for 2020-2021")
    
    if n_pos == 0:
        logger.warning("No positive samples found for 2020-2021. Skipping negative generation.")
        return "No positive samples found for target years"
    
    # Создаем диапазон дат только для 2020-2021
    all_dates = pd.date_range(
        start='2020-01-01',
        end='2021-12-31',
        freq='D'
    ).to_pydatetime().tolist()
    
    # Считаем частоту каждой ячейки среди позитивов
    cell_freq = pos_data.groupby(['latitude', 'longitude']).size().reset_index(name='count')
    cell_freq['prob'] = cell_freq['count'] / cell_freq['count'].sum()
    
    cells = list(zip(cell_freq['latitude'], cell_freq['longitude']))
    weights = cell_freq['prob'].tolist()
    
    # Генерация негативов большими батчами
    def generate_negative_batch(batch_size=10000):
        rows = []
        for _ in range(batch_size):
            lat, lon = random.choices(cells, weights=weights, k=1)[0]
            dt = random.choice(all_dates)
            rows.append({
                'latitude': lat,
                'longitude': lon,
                'dt': pd.Timestamp(dt),
                'year': dt.year,
                'month': dt.month,
                'weekday': dt.weekday(),
                'fire_occurred': False
            })
        return rows
    
    # Генерируем негативы батчами
    total_negatives = n_pos  # столько же негативов, сколько позитивов
    batch_size = 10000
    total_batches = (total_negatives + batch_size - 1) // batch_size
    
    logger.info(f"Generating {total_negatives} negative samples in {total_batches} batches")
    
    for batch_num in range(total_batches):
        current_batch_size = min(batch_size, total_negatives - batch_num * batch_size)
        neg_batch = generate_negative_batch(current_batch_size)
        
        # Подготавливаем данные для вставки
        neg_values_list = []
        for row in neg_batch:
            neg_values_list.append((
                row['latitude'], row['longitude'], row['dt'],
                row['fire_occurred'], row['year'], row['month'], 
                row['weekday'], row['latitude'], row['longitude'],
                datetime.now()
            ))
        
        # Вставляем батч
        neg_insert_sql = """
        INSERT INTO fireforceai.training_features 
        (latitude, longitude, dt, fire_occurred, 
         year, month, weekday, lat_cell, lon_cell, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Вставляем записи по одной
        for values in neg_values_list:
            pg_hook.run(neg_insert_sql, parameters=values)
        
        logger.info(f"Generated negative batch {batch_num + 1}/{total_batches} ({len(neg_batch)} samples)")
    
    # Статистика
    stats = {
        'positive_samples': n_pos,
        'negative_samples': total_negatives,
        'total_samples': n_pos + total_negatives,
        'balance_ratio': 1.0,
        'years_covered': '2020-2021'
    }
    
    logger.info(f"Generated {total_negatives} negative samples. Total dataset: {n_pos + total_negatives} samples")
    context['task_instance'].xcom_push(key='negative_samples_stats', value=stats)
    
    return f"Generated {total_negatives} negative samples for 2020-2021 dataset"

generate_negatives = PythonOperator(
    task_id='generate_negative_samples',
    python_callable=generate_negative_samples,
    dag=dag
)

# ============================================================================
# TASK 3: Создание базовых признаков для ML (включая негативы)
# ============================================================================

def create_basic_ml_features(**context):
    """
    Создание базовых признаков для ML на основе данных о пожарах.
    Включает позитивы и негативы за 2020-2021 годы.
    """
    from datetime import datetime
    
    logger.info("Creating basic ML features from fire data (including negatives)")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем, есть ли уже данные в training_features
    check_sql = "SELECT COUNT(*) FROM fireforceai.training_features WHERE EXTRACT(YEAR FROM dt) IN (2020, 2021)"
    existing_count = pg_hook.get_first(check_sql)[0]
    
    if existing_count > 0:
        logger.info(f"Found {existing_count} existing training features for 2020-2021. Skipping feature creation.")
        return f"Skipped feature creation - {existing_count} features already exist"
    
    # Создаем базовые признаки для ML (позитивы + негативы за 2020-2021)
    features_sql = """
    INSERT INTO fireforceai.training_features 
    (latitude, longitude, dt, fire_occurred, 
     year, month, weekday, lat_cell, lon_cell, created_at)
    SELECT 
        lat_cell as latitude,
        lon_cell as longitude,
        dt,
        true as fire_occurred,
        EXTRACT(YEAR FROM dt) as year,
        EXTRACT(MONTH FROM dt) as month,
        EXTRACT(DOW FROM dt) as weekday,
        lat_cell,
        lon_cell,
        NOW() as created_at
    FROM fireforceai.historical_fires
    WHERE EXTRACT(YEAR FROM dt) IN (2020, 2021)
    GROUP BY lat_cell, lon_cell, dt;
    """
    
    pg_hook.run(features_sql)
    
    # Получаем статистику созданных признаков
    stats_sql = """
    SELECT 
        COUNT(*) as total_samples,
        COUNT(*) FILTER (WHERE fire_occurred = true) as positive_samples,
        COUNT(*) FILTER (WHERE fire_occurred = false) as negative_samples,
        COUNT(DISTINCT lat_cell || '_' || lon_cell) as unique_cells,
        COUNT(DISTINCT EXTRACT(YEAR FROM dt)) as years_covered
    FROM fireforceai.training_features
    WHERE EXTRACT(YEAR FROM dt) IN (2020, 2021)
    """
    
    result = pg_hook.get_first(stats_sql)
    
    if result:
        total_samples, positive_samples, negative_samples, unique_cells, years_covered = result
        
        feature_stats = {
            'total_samples': total_samples,
            'positive_samples': positive_samples,
            'negative_samples': negative_samples,
            'unique_cells': unique_cells,
            'years_covered': years_covered,
            'balance_ratio': negative_samples / positive_samples if positive_samples > 0 else 0,
            'note': 'Weather data will be added in separate DAG'
        }
        
        logger.info(f"Basic ML features created. Stats: {feature_stats}")
        context['task_instance'].xcom_push(key='basic_feature_stats', value=feature_stats)
        
        return f"Created {total_samples} basic ML training samples (2020-2021)"
    else:
        logger.warning("No basic ML features created")
        return "No basic ML features created"

create_features = PythonOperator(
    task_id='create_basic_ml_features',
    python_callable=create_basic_ml_features,
    dag=dag
)

# ============================================================================
# TASK 4: Создание статистики по пожарам
# ============================================================================

def create_fire_statistics(**context):
    """
    Создание статистики по историческим данным о пожарах.
    """
    from datetime import datetime
    
    logger.info("Creating fire statistics")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Статистика по годам
    yearly_stats_sql = """
    INSERT INTO fireforceai.fire_statistics 
    (region, year, total_fires, data_source, last_updated)
    SELECT 
        'Russia' as region,
        EXTRACT(YEAR FROM dt) as year,
        COUNT(*) as total_fires,
        'historical_fires' as data_source,
        NOW() as last_updated
    FROM fireforceai.historical_fires
    GROUP BY EXTRACT(YEAR FROM dt)
    ON CONFLICT (region, year) DO UPDATE SET
        total_fires = EXCLUDED.total_fires,
        last_updated = NOW();
    """
    
    pg_hook.run(yearly_stats_sql)
    
    # Статистика по месяцам (для каждого года)
    monthly_stats_sql = """
    INSERT INTO fireforceai.fire_statistics 
    (region, year, month, total_fires, data_source, last_updated)
    SELECT 
        'Russia' as region,
        EXTRACT(YEAR FROM dt) as year,
        EXTRACT(MONTH FROM dt) as month,
        COUNT(*) as total_fires,
        'historical_fires' as data_source,
        NOW() as last_updated
    FROM fireforceai.historical_fires
    GROUP BY EXTRACT(YEAR FROM dt), EXTRACT(MONTH FROM dt)
    ON CONFLICT (region, year, month) DO UPDATE SET
        total_fires = EXCLUDED.total_fires,
        last_updated = NOW();
    """
    
    pg_hook.run(monthly_stats_sql)
    
    # Общая статистика
    overall_stats_sql = """
    SELECT 
        COUNT(DISTINCT lat_cell, lon_cell) as unique_locations,
        COUNT(*) as total_fires,
        MIN(dt) as earliest_date,
        MAX(dt) as latest_date,
        COUNT(DISTINCT type_name) as fire_types,
        COUNT(DISTINCT EXTRACT(YEAR FROM dt)) as years_covered
    FROM fireforceai.historical_fires
    """
    
    result = pg_hook.get_first(overall_stats_sql)
    
    if result:
        unique_locations, total_fires, earliest_date, latest_date, fire_types, years_covered = result
        
        overall_stats = {
            'unique_locations': unique_locations,
            'total_fires': total_fires,
            'date_range': f"{earliest_date} to {latest_date}",
            'fire_types': fire_types,
            'years_covered': years_covered
        }
        
        logger.info(f"Fire statistics created. Overall stats: {overall_stats}")
        context['task_instance'].xcom_push(key='fire_overall_stats', value=overall_stats)
        
        return f"Created statistics for {total_fires} fires across {unique_locations} locations"
    else:
        logger.warning("No fire statistics created")
        return "No fire statistics created"

create_stats = PythonOperator(
    task_id='create_fire_statistics',
    python_callable=create_fire_statistics,
    dag=dag
)

# ============================================================================
# TASK 5: Валидация данных о пожарах
# ============================================================================

def validate_fire_data(**context):
    """
    Валидация загруженных данных о пожарах.
    """
    logger.info("Validating fire data")
    
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
            'name': 'coordinate_validity',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.historical_fires 
            WHERE lat_cell BETWEEN 41.2 AND 81.9 
            AND lon_cell BETWEEN 19.6 AND 169.0
            ''',
            'min_expected': 1000,
            'description': 'Coordinate validity check'
        },
        {
            'name': 'date_range_validity',
            'sql': '''
            SELECT COUNT(*) FROM fireforceai.historical_fires 
            WHERE dt BETWEEN '2010-01-01' AND '2024-12-31'
            ''',
            'min_expected': 1000,
            'description': 'Date range validity check'
        },
        {
            'name': 'ml_features_completeness',
            'sql': 'SELECT COUNT(*) FROM fireforceai.training_features',
            'min_expected': 1000,
            'description': 'ML features completeness'
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
    context['task_instance'].xcom_push(key='fire_validation_results', value=validation_results)
    
    # Проверяем общий результат
    failed_checks = [name for name, result in validation_results.items() if not result.get('passed', True)]
    
    if failed_checks:
        logger.warning(f"Fire data validation failed for checks: {failed_checks}")
        raise Exception(f"Fire data validation failed for checks: {failed_checks}")
    else:
        logger.info("All fire data validation checks passed")
    
    return "Fire data validation completed successfully"

validate_data = PythonOperator(
    task_id='validate_fire_data',
    python_callable=validate_fire_data,
    dag=dag
)

# ============================================================================
# TASK 6: Завершение
# ============================================================================

end_loading = DummyOperator(
    task_id='end_fire_data_loading',
    dag=dag
)

# ============================================================================
# Определение зависимостей между задачами
# ============================================================================

# Последовательное выполнение
load_fire_data >> generate_negatives >> create_features >> create_stats >> validate_data >> end_loading 