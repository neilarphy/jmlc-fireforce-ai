"""
Wildfire Monitoring DAG
DAG для мониторинга системы предсказания лесных пожаров.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация DAG
default_args = {
    'owner': 'monitoring-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email': ['monitoring@wildfire-prediction.com']
}

# Создание DAG
dag = DAG(
    'wildfire_monitoring',
    default_args=default_args,
    description='Мониторинг системы предсказания лесных пожаров',
    schedule_interval='@hourly',  # Ежечасно
    catchup=False,
    max_active_runs=1,
    tags=['wildfire', 'monitoring', 'alerts']
)

# ============================================================================
# TASK 1: Проверка состояния базы данных
# ============================================================================

def check_database_health(**context):
    """Проверка состояния базы данных."""
    logger.info("Checking database health")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем подключение
    try:
        result = pg_hook.get_first("SELECT 1")
        if result:
            logger.info("Database connection: OK")
        else:
            raise Exception("Database connection failed")
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise
    
    # Проверяем размер таблиц
    table_sizes_sql = """
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
    FROM pg_tables 
    WHERE schemaname = 'fireforceai'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    """
    
    try:
        table_sizes = pg_hook.get_records(table_sizes_sql)
        logger.info(f"Table sizes: {table_sizes}")
        
        # Проверяем размеры таблиц
        for table in table_sizes:
            table_name = table[1]
            size_str = table[2]
            logger.info(f"Table {table_name}: {size_str}")
            
    except Exception as e:
        logger.error(f"Error getting table sizes: {str(e)}")
    
    return "Database health check completed"

check_db_health = PythonOperator(
    task_id='check_database_health',
    python_callable=check_database_health,
    dag=dag
)

# ============================================================================
# TASK 2: Проверка качества данных
# ============================================================================

def check_data_quality(**context):
    """Проверка качества данных."""
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    check_date = execution_date - timedelta(hours=1)  # Проверяем данные за последний час
    
    logger.info(f"Checking data quality for date: {check_date}")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверки качества данных
    quality_checks = [
        {
            'name': 'recent_fire_data',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.processed_fire_data 
            WHERE created_at >= %s
            """,
            'min_expected': 1,
            'description': 'Recent fire data availability'
        },
        {
            'name': 'recent_weather_data',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.raw_weather_data 
            WHERE created_at >= %s
            """,
            'min_expected': 1,
            'description': 'Recent weather data availability'
        },
        {
            'name': 'data_freshness',
            'sql': """
            SELECT EXTRACT(EPOCH FROM (NOW() - MAX(created_at)))/3600 as hours_old
            FROM fireforceai.processed_fire_data
            """,
            'max_expected': 24,  # Данные не старше 24 часов
            'description': 'Data freshness check'
        },
        {
            'name': 'coordinate_validity',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.processed_fire_data 
            WHERE created_at >= %s 
            AND (latitude < 41.2 OR latitude > 81.9 OR longitude < 19.6 OR longitude > 169.0)
            """,
            'max_expected': 0,
            'description': 'Coordinate validity check'
        }
    ]
    
    quality_results = {}
    
    for check in quality_checks:
        try:
            result = pg_hook.get_first(check['sql'], parameters=(check_date,))
            value = result[0] if result else 0
            
            if 'min_expected' in check:
                passed = value >= check['min_expected']
                threshold = check['min_expected']
            elif 'max_expected' in check:
                passed = value <= check['max_expected']
                threshold = check['max_expected']
            else:
                passed = True
                threshold = None
            
            quality_results[check['name']] = {
                'value': value,
                'threshold': threshold,
                'passed': passed,
                'description': check['description']
            }
            
            logger.info(f"Quality check '{check['name']}': {value} (threshold: {threshold}, passed: {passed})")
            
        except Exception as e:
            logger.error(f"Error in quality check '{check['name']}': {str(e)}")
            quality_results[check['name']] = {
                'error': str(e),
                'passed': False,
                'description': check['description']
            }
    
    # Сохраняем результаты
    context['task_instance'].xcom_push(key='data_quality_results', value=quality_results)
    
    # Проверяем общий результат
    failed_checks = [name for name, result in quality_results.items() if not result.get('passed', True)]
    
    if failed_checks:
        logger.warning(f"Data quality checks failed: {failed_checks}")
        # Здесь можно добавить отправку алерта
    else:
        logger.info("All data quality checks passed")
    
    return f"Data quality check completed. Failed checks: {len(failed_checks)}"

check_data_quality_task = PythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    dag=dag
)

# ============================================================================
# TASK 3: Проверка производительности API
# ============================================================================

def check_api_performance(**context):
    """Проверка производительности API."""
    import requests
    import time
    
    logger.info("Checking API performance")
    
    api_url = "http://localhost:8000"
    
    # Тестовые запросы
    test_endpoints = [
        {
            'name': 'health_check',
            'url': f"{api_url}/health",
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': 'predictions_endpoint',
            'url': f"{api_url}/api/v1/predictions/single",
            'method': 'POST',
            'data': {
                'latitude': 55.7558,
                'longitude': 37.6176,
                'temperature': 20.5,
                'humidity': 60,
                'wind_speed': 5.0,
                'precipitation': 0.0
            },
            'expected_status': 200
        }
    ]
    
    performance_results = {}
    
    for endpoint in test_endpoints:
        try:
            start_time = time.time()
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=30)
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}), timeout=30)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response.status_code == endpoint['expected_status']
            
            performance_results[endpoint['name']] = {
                'response_time': response_time,
                'status_code': response.status_code,
                'success': success,
                'expected_status': endpoint['expected_status']
            }
            
            logger.info(f"API test '{endpoint['name']}': {response_time:.2f}s, status: {response.status_code}, success: {success}")
            
        except Exception as e:
            logger.error(f"API test '{endpoint['name']}' failed: {str(e)}")
            performance_results[endpoint['name']] = {
                'error': str(e),
                'success': False
            }
    
    # Сохраняем результаты
    context['task_instance'].xcom_push(key='api_performance_results', value=performance_results)
    
    # Проверяем общий результат
    failed_tests = [name for name, result in performance_results.items() if not result.get('success', True)]
    
    if failed_tests:
        logger.warning(f"API performance tests failed: {failed_tests}")
    else:
        logger.info("All API performance tests passed")
    
    return f"API performance check completed. Failed tests: {len(failed_tests)}"

check_api_performance_task = PythonOperator(
    task_id='check_api_performance',
    python_callable=check_api_performance,
    dag=dag
)

# ============================================================================
# TASK 4: Проверка ML моделей
# ============================================================================

def check_ml_models(**context):
    """Проверка состояния ML моделей."""
    logger.info("Checking ML models")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем активные модели
    active_models_sql = """
    SELECT 
        run_id,
        model_type,
        created_at,
        is_active,
        deployed_at
    FROM fireforceai.model_versions 
    WHERE is_active = true
    ORDER BY deployed_at DESC
    LIMIT 5;
    """
    
    try:
        active_models = pg_hook.get_records(active_models_sql)
        
        if active_models:
            logger.info(f"Found {len(active_models)} active models")
            for model in active_models:
                logger.info(f"Active model: {model[0]} ({model[1]}) deployed at {model[4]}")
        else:
            logger.warning("No active models found")
        
    except Exception as e:
        logger.error(f"Error checking ML models: {str(e)}")
    
    # Проверяем метрики моделей
    model_metrics_sql = """
    SELECT 
        run_id,
        model_type,
        metrics->>'test_accuracy' as accuracy,
        metrics->>'test_roc_auc' as roc_auc,
        created_at
    FROM fireforceai.model_versions 
    WHERE is_active = true
    ORDER BY created_at DESC
    LIMIT 1;
    """
    
    try:
        model_metrics = pg_hook.get_first(model_metrics_sql)
        
        if model_metrics:
            run_id, model_type, accuracy, roc_auc, created_at = model_metrics
            logger.info(f"Latest model metrics - Run ID: {run_id}, Accuracy: {accuracy}, ROC AUC: {roc_auc}")
            
            # Проверяем качество модели
            if accuracy and roc_auc:
                accuracy_val = float(accuracy)
                roc_auc_val = float(roc_auc)
                
                quality_checks = {
                    'accuracy_good': accuracy_val >= 0.7,
                    'roc_auc_good': roc_auc_val >= 0.75
                }
                
                failed_checks = [name for name, passed in quality_checks.items() if not passed]
                
                if failed_checks:
                    logger.warning(f"Model quality checks failed: {failed_checks}")
                else:
                    logger.info("Model quality checks passed")
        
    except Exception as e:
        logger.error(f"Error checking model metrics: {str(e)}")
    
    return "ML models check completed"

check_ml_models_task = PythonOperator(
    task_id='check_ml_models',
    python_callable=check_ml_models,
    dag=dag
)

# ============================================================================
# TASK 5: Создание отчета мониторинга
# ============================================================================

def create_monitoring_report(**context):
    """Создание отчета мониторинга."""
    from datetime import datetime
    
    logger.info("Creating monitoring report")
    
    # Получаем результаты всех проверок
    data_quality_results = context['task_instance'].xcom_pull(
        task_ids='check_data_quality',
        key='data_quality_results'
    )
    
    api_performance_results = context['task_instance'].xcom_pull(
        task_ids='check_api_performance',
        key='api_performance_results'
    )
    
    # Создаем отчет
    report = {
        'timestamp': datetime.now().isoformat(),
        'data_quality': {
            'total_checks': len(data_quality_results) if data_quality_results else 0,
            'passed_checks': len([r for r in data_quality_results.values() if r.get('passed', False)]) if data_quality_results else 0,
            'failed_checks': len([r for r in data_quality_results.values() if not r.get('passed', True)]) if data_quality_results else 0
        },
        'api_performance': {
            'total_tests': len(api_performance_results) if api_performance_results else 0,
            'passed_tests': len([r for r in api_performance_results.values() if r.get('success', False)]) if api_performance_results else 0,
            'failed_tests': len([r for r in api_performance_results.values() if not r.get('success', True)]) if api_performance_results else 0
        }
    }
    
    # Сохраняем отчет в БД
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    insert_report_sql = """
    INSERT INTO fireforceai.system_health 
    (check_type, check_results, created_at)
    VALUES (%s, %s, NOW())
    """
    
    try:
        import json
        pg_hook.run(insert_report_sql, parameters=(
            'monitoring_report',
            json.dumps(report)
        ))
        logger.info("Monitoring report saved to database")
    except Exception as e:
        logger.error(f"Error saving monitoring report: {str(e)}")
    
    # Логируем общий статус
    total_issues = report['data_quality']['failed_checks'] + report['api_performance']['failed_tests']
    
    if total_issues == 0:
        logger.info("All monitoring checks passed")
        return "Monitoring report: All systems operational"
    else:
        logger.warning(f"Monitoring report: {total_issues} issues detected")
        return f"Monitoring report: {total_issues} issues detected"

create_report = PythonOperator(
    task_id='create_monitoring_report',
    python_callable=create_monitoring_report,
    dag=dag
)

# ============================================================================
# TASK 6: Завершение
# ============================================================================

end_monitoring = DummyOperator(
    task_id='end_monitoring',
    dag=dag
)

# ============================================================================
# Определение зависимостей между задачами
# ============================================================================

check_db_health >> check_data_quality_task
check_data_quality_task >> check_api_performance_task
check_api_performance_task >> check_ml_models_task
check_ml_models_task >> create_report
create_report >> end_monitoring 