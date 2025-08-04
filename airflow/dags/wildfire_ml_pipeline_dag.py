"""
Wildfire ML Pipeline DAG
DAG для обучения и валидации ML моделей предсказания лесных пожаров.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация DAG
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'email': ['ml-team@wildfire-prediction.com']
}

# Создание DAG
dag = DAG(
    'wildfire_ml_pipeline',
    default_args=default_args,
    description='Обучение и валидация ML моделей предсказания пожаров',
    schedule_interval='@weekly',  # Еженедельно
    catchup=False,
    max_active_runs=1,
    tags=['wildfire', 'ml', 'training']
)

# ============================================================================
# TASK 1: Проверка готовности данных для обучения
# ============================================================================

def check_training_data_readiness(**context):
    """Проверка готовности данных для обучения ML модели."""
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    check_date = execution_date - timedelta(days=7)  # Проверяем данные за неделю
    
    logger.info(f"Checking training data readiness for date: {check_date}")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем количество данных
    data_checks = [
        {
            'name': 'processed_fire_data_count',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.processed_fire_data 
            WHERE dt >= %s
            """,
            'min_expected': 1000
        },
        {
            'name': 'weather_data_count',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.raw_weather_data 
            WHERE dt >= %s
            """,
            'min_expected': 1000
        },
        {
            'name': 'fire_statistics_count',
            'sql': """
            SELECT COUNT(*) FROM fireforceai.fire_statistics 
            WHERE date >= %s
            """,
            'min_expected': 7
        }
    ]
    
    check_results = {}
    
    for check in data_checks:
        result = pg_hook.get_first(check['sql'], parameters=(check_date,))
        count = result[0] if result else 0
        
        check_results[check['name']] = {
            'count': count,
            'passed': count >= check['min_expected']
        }
        
        logger.info(f"Data check '{check['name']}': {count} records, passed: {count >= check['min_expected']}")
    
    # Сохраняем результаты проверки
    context['task_instance'].xcom_push(key='data_readiness_results', value=check_results)
    
    # Проверяем общий результат
    all_passed = all(check['passed'] for check in check_results.values())
    
    if all_passed:
        logger.info("All data readiness checks passed")
        return 'prepare_training_features'
    else:
        failed_checks = [name for name, result in check_results.items() if not result['passed']]
        logger.warning(f"Data readiness checks failed: {failed_checks}")
        return 'data_not_ready'

check_data_readiness = BranchPythonOperator(
    task_id='check_training_data_readiness',
    python_callable=check_training_data_readiness,
    dag=dag
)

# ============================================================================
# TASK 2: Подготовка признаков для обучения
# ============================================================================

def prepare_training_features(**context):
    """Подготовка признаков для обучения ML модели."""
    from datetime import datetime, timedelta
    
    execution_date = context['execution_date']
    feature_date = execution_date - timedelta(days=30)  # Данные за месяц
    
    logger.info(f"Preparing training features for date: {feature_date}")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Создаем признаки для ML
    feature_sql = """
    INSERT INTO fireforceai.training_features 
    (latitude, longitude, dt, fire_occurred, fire_count, avg_frp, max_frp,
     avg_temperature, avg_humidity, avg_wind_speed, total_precipitation,
     day_of_year, month, weekday, season, created_at)
    SELECT 
        p.latitude,
        p.longitude,
        p.dt,
        CASE WHEN p.fire_count > 0 THEN true ELSE false END as fire_occurred,
        COALESCE(p.fire_count, 0) as fire_count,
        COALESCE(p.avg_frp, 0) as avg_frp,
        COALESCE(p.max_frp, 0) as max_frp,
        COALESCE(p.avg_temperature, 0) as avg_temperature,
        COALESCE(p.avg_humidity, 0) as avg_humidity,
        COALESCE(p.avg_wind_speed, 0) as avg_wind_speed,
        COALESCE(p.total_precipitation, 0) as total_precipitation,
        EXTRACT(DOY FROM p.dt) as day_of_year,
        EXTRACT(MONTH FROM p.dt) as month,
        EXTRACT(DOW FROM p.dt) as weekday,
        CASE 
            WHEN EXTRACT(MONTH FROM p.dt) IN (12, 1, 2) THEN 'winter'
            WHEN EXTRACT(MONTH FROM p.dt) IN (3, 4, 5) THEN 'spring'
            WHEN EXTRACT(MONTH FROM p.dt) IN (6, 7, 8) THEN 'summer'
            ELSE 'autumn'
        END as season,
        NOW() as created_at
    FROM fireforceai.processed_fire_data p
    WHERE p.dt >= %s
    ON CONFLICT (latitude, longitude, dt) DO UPDATE SET
        fire_occurred = EXCLUDED.fire_occurred,
        fire_count = EXCLUDED.fire_count,
        avg_frp = EXCLUDED.avg_frp,
        max_frp = EXCLUDED.max_frp,
        avg_temperature = EXCLUDED.avg_temperature,
        avg_humidity = EXCLUDED.avg_humidity,
        avg_wind_speed = EXCLUDED.avg_wind_speed,
        total_precipitation = EXCLUDED.total_precipitation,
        day_of_year = EXCLUDED.day_of_year,
        month = EXCLUDED.month,
        weekday = EXCLUDED.weekday,
        season = EXCLUDED.season,
        updated_at = NOW();
    """
    
    pg_hook.run(feature_sql, parameters=(feature_date,))
    
    # Получаем статистику подготовленных признаков
    stats_sql = """
    SELECT 
        COUNT(*) as total_samples,
        COUNT(*) FILTER (WHERE fire_occurred = true) as positive_samples,
        COUNT(*) FILTER (WHERE fire_occurred = false) as negative_samples
    FROM fireforceai.training_features 
    WHERE dt >= %s
    """
    
    result = pg_hook.get_first(stats_sql, parameters=(feature_date,))
    
    if result:
        total_samples = result[0]
        positive_samples = result[1]
        negative_samples = result[2]
        
        feature_stats = {
            'total_samples': total_samples,
            'positive_samples': positive_samples,
            'negative_samples': negative_samples,
            'positive_ratio': positive_samples / total_samples if total_samples > 0 else 0
        }
        
        logger.info(f"Prepared features: {feature_stats}")
        context['task_instance'].xcom_push(key='feature_stats', value=feature_stats)
        
        return f"Prepared {total_samples} training samples"
    else:
        logger.warning("No features prepared")
        return "No features prepared"

prepare_features = PythonOperator(
    task_id='prepare_training_features',
    python_callable=prepare_training_features,
    dag=dag
)

# ============================================================================
# TASK 3: Обучение ML модели
# ============================================================================

def train_ml_model(**context):
    """Обучение ML модели предсказания пожаров."""
    import requests
    import json
    
    logger.info("Starting ML model training")
    
    # Получаем статистику признаков
    feature_stats = context['task_instance'].xcom_pull(
        task_ids='prepare_training_features',
        key='feature_stats'
    )
    
    if not feature_stats or feature_stats['total_samples'] < 1000:
        raise Exception("Insufficient training data")
    
    # Вызываем API для обучения модели
    api_url = "http://localhost:8000"  # URL вашего API
    
    training_params = {
        'model_type': 'lightgbm',
        'test_size': 0.2,
        'random_state': 42,
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/v1/mlflow/experiments/wildfire_prediction/train",
            json=training_params,
            timeout=3600  # 1 час таймаут
        )
        
        if response.status_code == 200:
            training_result = response.json()
            run_id = training_result.get('data', {}).get('run_id')
            
            logger.info(f"Model training completed successfully. Run ID: {run_id}")
            
            # Сохраняем информацию о модели в БД
            pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
            
            model_info_sql = """
            INSERT INTO fireforceai.model_versions 
            (run_id, model_type, training_params, metrics, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (run_id) DO UPDATE SET
                model_type = EXCLUDED.model_type,
                training_params = EXCLUDED.training_params,
                metrics = EXCLUDED.metrics,
                updated_at = NOW();
            """
            
            pg_hook.run(model_info_sql, parameters=(
                run_id,
                training_params['model_type'],
                json.dumps(training_params),
                json.dumps(training_result.get('data', {}).get('metrics', {}))
            ))
            
            context['task_instance'].xcom_push(key='training_run_id', value=run_id)
            return f"Model training completed. Run ID: {run_id}"
        else:
            raise Exception(f"Training failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise

train_model = PythonOperator(
    task_id='train_ml_model',
    python_callable=train_ml_model,
    dag=dag
)

# ============================================================================
# TASK 4: Валидация модели
# ============================================================================

def validate_model(**context):
    """Валидация обученной модели."""
    import requests
    import json
    
    run_id = context['task_instance'].xcom_pull(
        task_ids='train_ml_model',
        key='training_run_id'
    )
    
    if not run_id:
        raise Exception("No training run ID found")
    
    logger.info(f"Validating model with run ID: {run_id}")
    
    # Получаем метрики модели
    api_url = "http://localhost:8000"
    
    try:
        response = requests.get(
            f"{api_url}/api/v1/mlflow/experiments/wildfire_prediction/runs/{run_id}/metrics"
        )
        
        if response.status_code == 200:
            metrics = response.json().get('data', {})
            
            # Критерии валидации
            validation_criteria = {
                'test_accuracy': 0.7,
                'test_roc_auc': 0.75,
                'test_f1_score': 0.65
            }
            
            validation_results = {}
            all_passed = True
            
            for metric, threshold in validation_criteria.items():
                metric_value = metrics.get(metric, 0)
                passed = metric_value >= threshold
                validation_results[metric] = {
                    'value': metric_value,
                    'threshold': threshold,
                    'passed': passed
                }
                
                if not passed:
                    all_passed = False
                
                logger.info(f"Metric {metric}: {metric_value} (threshold: {threshold}, passed: {passed})")
            
            # Сохраняем результаты валидации
            context['task_instance'].xcom_push(key='validation_results', value=validation_results)
            
            if all_passed:
                logger.info("Model validation passed")
                return 'deploy_model'
            else:
                logger.warning("Model validation failed")
                return 'model_validation_failed'
        else:
            raise Exception(f"Failed to get model metrics: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Model validation failed: {str(e)}")
        raise

validate_model = BranchPythonOperator(
    task_id='validate_model',
    python_callable=validate_model,
    dag=dag
)

# ============================================================================
# TASK 5: Развертывание модели
# ============================================================================

def deploy_model(**context):
    """Развертывание валидированной модели."""
    import requests
    
    run_id = context['task_instance'].xcom_pull(
        task_ids='train_ml_model',
        key='training_run_id'
    )
    
    logger.info(f"Deploying model with run ID: {run_id}")
    
    api_url = "http://localhost:8000"
    
    try:
        # Активируем модель в продакшене
        response = requests.post(
            f"{api_url}/api/v1/mlflow/experiments/wildfire_prediction/runs/{run_id}/deploy"
        )
        
        if response.status_code == 200:
            deploy_result = response.json()
            
            # Обновляем статус модели в БД
            pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
            
            update_sql = """
            UPDATE fireforceai.model_versions 
            SET is_active = true, deployed_at = NOW()
            WHERE run_id = %s
            """
            
            pg_hook.run(update_sql, parameters=(run_id,))
            
            logger.info(f"Model deployed successfully: {deploy_result}")
            return f"Model deployed successfully. Run ID: {run_id}"
        else:
            raise Exception(f"Model deployment failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Model deployment failed: {str(e)}")
        raise

deploy_model_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag
)

# ============================================================================
# TASK 6: Тестирование развернутой модели
# ============================================================================

def test_deployed_model(**context):
    """Тестирование развернутой модели."""
    import requests
    
    logger.info("Testing deployed model")
    
    # Тестовые данные
    test_data = {
        'latitude': 55.7558,
        'longitude': 37.6176,
        'temperature': 20.5,
        'humidity': 60,
        'wind_speed': 5.0,
        'precipitation': 0.0
    }
    
    api_url = "http://localhost:8000"
    
    try:
        response = requests.post(
            f"{api_url}/api/v1/predictions/single",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            prediction = response.json()
            logger.info(f"Model test successful: {prediction}")
            return "Model test successful"
        else:
            raise Exception(f"Model test failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Model test failed: {str(e)}")
        raise

test_model = PythonOperator(
    task_id='test_deployed_model',
    python_callable=test_deployed_model,
    dag=dag
)

# ============================================================================
# TASK 7: Завершение
# ============================================================================

end_ml_pipeline = DummyOperator(
    task_id='end_ml_pipeline',
    dag=dag
)

data_not_ready = DummyOperator(
    task_id='data_not_ready',
    dag=dag
)

model_validation_failed = DummyOperator(
    task_id='model_validation_failed',
    dag=dag
)

# ============================================================================
# Определение зависимостей между задачами
# ============================================================================

check_data_readiness >> [prepare_features, data_not_ready]
prepare_features >> train_model
train_model >> validate_model
validate_model >> [deploy_model_task, model_validation_failed]
deploy_model_task >> test_model
test_model >> end_ml_pipeline

# Альтернативные пути завершения
data_not_ready >> end_ml_pipeline
model_validation_failed >> end_ml_pipeline 