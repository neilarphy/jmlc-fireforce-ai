"""
Wildfire Data Pipeline DAG
Основной DAG для загрузки и обработки данных о лесных пожарах.
Работает с базой данных wildfire и схемой fireforceai.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import pandas as pd
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация DAG
default_args = {
    'owner': 'wildfire-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['admin@wildfire-prediction.com']
}

# Создание DAG
dag = DAG(
    'wildfire_data_pipeline',
    default_args=default_args,
    description='Загрузка и обработка данных о лесных пожарах',
    schedule_interval='@daily',  # Ежедневно
    catchup=False,
    max_active_runs=1,
    tags=['wildfire', 'data-processing', 'etl']
)

# ============================================================================
# TASK 1: Проверка подключения к базе данных
# ============================================================================

test_connection = PostgresOperator(
    task_id="test_pg_connection",
    postgres_conn_id="wildfire_db",
    sql="SELECT 1;",
    dag=dag
)

# ============================================================================
# TASK 2: Проверка структуры таблиц
# ============================================================================

check_tables_structure = PostgresOperator(
    task_id="check_tables_structure",
    postgres_conn_id="wildfire_db",
    sql="""
    SELECT 
        table_name,
        column_name,
        data_type,
        is_nullable
    FROM information_schema.columns 
    WHERE table_schema = 'fireforceai' 
    ORDER BY table_name, ordinal_position;
    """,
    dag=dag
)

# ============================================================================
# TASK 3: Загрузка исторических данных о пожарах
# ============================================================================

def load_historical_fire_data(**context):
    """Загрузка исторических данных о пожарах."""
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Получаем дату для загрузки (вчерашний день)
    execution_date = context['execution_date']
    load_date = execution_date - timedelta(days=1)
    
    logger.info(f"Loading fire data for date: {load_date}")
    
    # Здесь должна быть логика загрузки данных
    # Пока создаем тестовые данные
    test_data = pd.DataFrame({
        'latitude': [55.7558, 59.9311, 55.7558],
        'longitude': [37.6176, 30.3609, 37.6176],
        'dt': [load_date, load_date, load_date],
        'confidence': [0.8, 0.9, 0.7],
        'frp': [10.5, 15.2, 8.3],
        'created_at': [datetime.now()] * 3
    })
    
    # Подключаемся к базе данных
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Загружаем данные в таблицу historical_fires
    for _, row in test_data.iterrows():
        insert_sql = """
        INSERT INTO fireforceai.historical_fires 
        (latitude, longitude, dt, confidence, frp, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (latitude, longitude, dt) DO NOTHING;
        """
        
        pg_hook.run(insert_sql, parameters=(
            row['latitude'], row['longitude'], row['dt'],
            row['confidence'], row['frp'], row['created_at']
        ))
    
    logger.info(f"Loaded {len(test_data)} fire records")
    return f"Loaded {len(test_data)} fire records"

load_fire_data = PythonOperator(
    task_id='load_historical_fire_data',
    python_callable=load_historical_fire_data,
    dag=dag
)

# ============================================================================
# TASK 4: Загрузка метеорологических данных
# ============================================================================

def load_weather_data(**context):
    """Загрузка метеорологических данных."""
    import pandas as pd
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    load_date = execution_date - timedelta(days=1)
    
    logger.info(f"Loading weather data for date: {load_date}")
    
    # Тестовые метеоданные
    weather_data = pd.DataFrame({
        'latitude': [55.7558, 59.9311, 55.7558],
        'longitude': [37.6176, 30.3609, 37.6176],
        'dt': [load_date, load_date, load_date],
        'temperature': [15.5, 12.3, 18.7],
        'humidity': [65, 70, 55],
        'wind_speed': [5.2, 3.8, 7.1],
        'precipitation': [0.0, 2.5, 0.0],
        'created_at': [datetime.now()] * 3
    })
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    for _, row in weather_data.iterrows():
        insert_sql = """
        INSERT INTO fireforceai.raw_weather_data 
        (latitude, longitude, dt, temperature, humidity, wind_speed, precipitation, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (latitude, longitude, dt) DO NOTHING;
        """
        
        pg_hook.run(insert_sql, parameters=(
            row['latitude'], row['longitude'], row['dt'],
            row['temperature'], row['humidity'], row['wind_speed'],
            row['precipitation'], row['created_at']
        ))
    
    logger.info(f"Loaded {len(weather_data)} weather records")
    return f"Loaded {len(weather_data)} weather records"

load_weather = PythonOperator(
    task_id='load_weather_data',
    python_callable=load_weather_data,
    dag=dag
)

# ============================================================================
# TASK 5: Обработка и агрегация данных
# ============================================================================

def process_and_aggregate_data(**context):
    """Обработка и агрегация данных для ML."""
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    process_date = execution_date - timedelta(days=1)
    
    logger.info(f"Processing data for date: {process_date}")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Создаем агрегированные данные для ML
    aggregation_sql = """
    INSERT INTO fireforceai.processed_fire_data 
    (latitude, longitude, dt, fire_count, avg_frp, max_frp, 
     avg_temperature, avg_humidity, avg_wind_speed, total_precipitation,
     created_at)
    SELECT 
        f.latitude,
        f.longitude,
        f.dt,
        COUNT(f.id) as fire_count,
        AVG(f.frp) as avg_frp,
        MAX(f.frp) as max_frp,
        AVG(w.temperature) as avg_temperature,
        AVG(w.humidity) as avg_humidity,
        AVG(w.wind_speed) as avg_wind_speed,
        SUM(w.precipitation) as total_precipitation,
        NOW() as created_at
    FROM fireforceai.historical_fires f
    LEFT JOIN fireforceai.raw_weather_data w 
        ON f.latitude = w.latitude 
        AND f.longitude = w.longitude 
        AND f.dt = w.dt
    WHERE f.dt = %s
    GROUP BY f.latitude, f.longitude, f.dt
    ON CONFLICT (latitude, longitude, dt) DO UPDATE SET
        fire_count = EXCLUDED.fire_count,
        avg_frp = EXCLUDED.avg_frp,
        max_frp = EXCLUDED.max_frp,
        avg_temperature = EXCLUDED.avg_temperature,
        avg_humidity = EXCLUDED.avg_humidity,
        avg_wind_speed = EXCLUDED.avg_wind_speed,
        total_precipitation = EXCLUDED.total_precipitation,
        updated_at = NOW();
    """
    
    pg_hook.run(aggregation_sql, parameters=(process_date,))
    
    # Получаем статистику обработанных данных
    stats_sql = """
    SELECT COUNT(*) FROM fireforceai.processed_fire_data 
    WHERE dt = %s
    """
    
    result = pg_hook.get_first(stats_sql, parameters=(process_date,))
    processed_count = result[0] if result else 0
    
    logger.info(f"Processed {processed_count} aggregated records")
    return f"Processed {processed_count} aggregated records"

process_data = PythonOperator(
    task_id='process_and_aggregate_data',
    python_callable=process_and_aggregate_data,
    dag=dag
)

# ============================================================================
# TASK 6: Проверка качества данных
# ============================================================================

def validate_data_quality(**context):
    """Проверка качества обработанных данных."""
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    check_date = execution_date - timedelta(days=1)
    
    logger.info(f"Validating data quality for date: {check_date}")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверки качества данных
    quality_checks = [
        {
            'name': 'data_completeness',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.processed_fire_data 
            WHERE dt = %s AND fire_count IS NOT NULL
            """,
            'min_expected': 1
        },
        {
            'name': 'coordinate_validity',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.processed_fire_data 
            WHERE dt = %s AND latitude BETWEEN 41.2 AND 81.9 
            AND longitude BETWEEN 19.6 AND 169.0
            """,
            'min_expected': 1
        },
        {
            'name': 'weather_data_completeness',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.processed_fire_data 
            WHERE dt = %s AND avg_temperature IS NOT NULL 
            AND avg_humidity IS NOT NULL
            """,
            'min_expected': 1
        }
    ]
    
    validation_results = {}
    
    for check in quality_checks:
        result = pg_hook.get_first(check['sql'], parameters=(check_date,))
        count = result[0] if result else 0
        
        validation_results[check['name']] = {
            'count': count,
            'passed': count >= check['min_expected']
        }
        
        logger.info(f"Quality check '{check['name']}': {count} records, passed: {count >= check['min_expected']}")
    
    # Сохраняем результаты валидации
    context['task_instance'].xcom_push(key='data_quality_results', value=validation_results)
    
    # Проверяем общий результат
    all_passed = all(check['passed'] for check in validation_results.values())
    
    if not all_passed:
        failed_checks = [name for name, result in validation_results.items() if not result['passed']]
        raise Exception(f"Data quality validation failed for checks: {failed_checks}")
    
    logger.info("All data quality checks passed")
    return "Data quality validation passed"

validate_quality = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag
)

# ============================================================================
# TASK 7: Создание статистики
# ============================================================================

def create_daily_statistics(**context):
    """Создание ежедневной статистики."""
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    stats_date = execution_date - timedelta(days=1)
    
    logger.info(f"Creating statistics for date: {stats_date}")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Создаем статистику
    stats_sql = """
    INSERT INTO fireforceai.fire_statistics 
    (date, total_fires, total_frp, avg_frp, max_frp, 
     avg_temperature, avg_humidity, created_at)
    SELECT 
        %s as date,
        SUM(fire_count) as total_fires,
        SUM(avg_frp * fire_count) as total_frp,
        AVG(avg_frp) as avg_frp,
        MAX(max_frp) as max_frp,
        AVG(avg_temperature) as avg_temperature,
        AVG(avg_humidity) as avg_humidity,
        NOW() as created_at
    FROM fireforceai.processed_fire_data 
    WHERE dt = %s
    ON CONFLICT (date) DO UPDATE SET
        total_fires = EXCLUDED.total_fires,
        total_frp = EXCLUDED.total_frp,
        avg_frp = EXCLUDED.avg_frp,
        max_frp = EXCLUDED.max_frp,
        avg_temperature = EXCLUDED.avg_temperature,
        avg_humidity = EXCLUDED.avg_humidity,
        updated_at = NOW();
    """
    
    pg_hook.run(stats_sql, parameters=(stats_date, stats_date))
    
    # Получаем созданную статистику
    get_stats_sql = """
    SELECT total_fires, total_frp, avg_frp, max_frp 
    FROM fireforceai.fire_statistics 
    WHERE date = %s
    """
    
    result = pg_hook.get_first(get_stats_sql, parameters=(stats_date,))
    
    if result:
        stats = {
            'total_fires': result[0],
            'total_frp': result[1],
            'avg_frp': result[2],
            'max_frp': result[3]
        }
        logger.info(f"Created statistics: {stats}")
        return f"Created statistics for {stats_date}: {stats['total_fires']} fires"
    else:
        logger.warning("No statistics created")
        return "No statistics created"

create_stats = PythonOperator(
    task_id='create_daily_statistics',
    python_callable=create_daily_statistics,
    dag=dag
)

# ============================================================================
# TASK 8: Завершение
# ============================================================================

end_pipeline = DummyOperator(
    task_id='end_pipeline',
    dag=dag
)

# ============================================================================
# Определение зависимостей между задачами
# ============================================================================

test_connection >> check_tables_structure

# Параллельная загрузка данных
check_tables_structure >> [load_fire_data, load_weather]

# Обработка после загрузки
[load_fire_data, load_weather] >> process_data

# Валидация и статистика после обработки
process_data >> validate_quality
process_data >> create_stats

# Завершение после валидации и статистики
[validate_quality, create_stats] >> end_pipeline 