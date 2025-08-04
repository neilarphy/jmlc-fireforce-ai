"""
Кастомные Airflow операторы для системы предсказания лесных пожаров.
Следует принципам качества кода из steering документов.
"""
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.exceptions import AirflowException
import structlog

logger = structlog.get_logger()


class CeleryTaskOperator(BaseOperator):
    """
    Оператор для запуска Celery задач из Airflow.
    
    Интегрируется с нашими существующими Celery задачами
    через HTTP API или прямые вызовы.
    """
    
    template_fields = ['task_name', 'task_kwargs']
    
    @apply_defaults
    def __init__(self,
                 task_name: str,
                 task_kwargs: Optional[Dict[str, Any]] = None,
                 api_conn_id: str = 'wildfire_api',
                 timeout: int = 3600,
                 check_interval: int = 30,
                 *args, **kwargs):
        """
        Инициализация оператора.
        
        Args:
            task_name: Название Celery задачи
            task_kwargs: Аргументы для задачи
            api_conn_id: ID подключения к API
            timeout: Таймаут выполнения в секундах
            check_interval: Интервал проверки статуса в секундах
        """
        super().__init__(*args, **kwargs)
        self.task_name = task_name
        self.task_kwargs = task_kwargs or {}
        self.api_conn_id = api_conn_id
        self.timeout = timeout
        self.check_interval = check_interval
    
    def execute(self, context):
        """Выполнение Celery задачи."""
        logger.info("Starting Celery task execution",
                   task_name=self.task_name,
                   kwargs=self.task_kwargs)
        
        # Получаем HTTP hook для API вызовов
        http_hook = HttpHook(http_conn_id=self.api_conn_id, method='POST')
        
        # Определяем endpoint на основе типа задачи
        endpoint_map = {
            'train_model_with_mlflow': '/api/v1/mlflow/experiments/wildfire_prediction/train',
            'process_weather_data': '/api/v1/data/upload/weather',
            'load_fire_data': '/api/v1/data/upload/fires',
            'generate_prediction': '/api/v1/predictions/single',
            'generate_batch_predictions': '/api/v1/predictions/batch'
        }
        
        endpoint = endpoint_map.get(self.task_name)
        if not endpoint:
            raise AirflowException(f"Unknown task name: {self.task_name}")
        
        # Запускаем задачу через API
        try:
            response = http_hook.run(
                endpoint=endpoint,
                data=json.dumps(self.task_kwargs),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code not in [200, 201, 202]:
                raise AirflowException(f"API call failed: {response.status_code} - {response.text}")
            
            result = response.json()
            task_id = result.get('data', {}).get('task_id')
            
            if not task_id:
                raise AirflowException("No task_id returned from API")
            
            logger.info("Celery task started", task_id=task_id)
            
            # Ждем завершения задачи
            return self._wait_for_completion(task_id, http_hook)
            
        except Exception as e:
            logger.error("Failed to execute Celery task", error=str(e))
            raise AirflowException(f"Celery task execution failed: {e}")
    
    def _wait_for_completion(self, task_id: str, http_hook: HttpHook) -> Dict[str, Any]:
        """Ожидание завершения задачи."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < self.timeout:
            try:
                # Проверяем статус задачи
                response = http_hook.run(
                    endpoint=f'/api/v1/tasks/{task_id}/status',
                    method='GET'
                )
                
                if response.status_code != 200:
                    logger.warning("Failed to get task status", 
                                 task_id=task_id, 
                                 status_code=response.status_code)
                    continue
                
                result = response.json()
                task_data = result.get('data', {})
                state = task_data.get('state', 'UNKNOWN')
                
                logger.info("Task status check", task_id=task_id, state=state)
                
                if state == 'SUCCESS':
                    logger.info("Celery task completed successfully", task_id=task_id)
                    return task_data.get('result', {})
                
                elif state in ['FAILURE', 'REVOKED']:
                    error_msg = task_data.get('error', 'Unknown error')
                    raise AirflowException(f"Celery task failed: {error_msg}")
                
                elif state in ['PENDING', 'PROGRESS', 'RETRY']:
                    # Задача еще выполняется
                    import time
                    time.sleep(self.check_interval)
                    continue
                
                else:
                    logger.warning("Unknown task state", task_id=task_id, state=state)
                    import time
                    time.sleep(self.check_interval)
                    continue
                    
            except Exception as e:
                logger.error("Error checking task status", task_id=task_id, error=str(e))
                import time
                time.sleep(self.check_interval)
                continue
        
        # Таймаут
        raise AirflowException(f"Task {task_id} timed out after {self.timeout} seconds")


class DataQualityCheckOperator(BaseOperator):
    """
    Оператор для проверки качества данных.
    
    Выполняет различные проверки качества данных
    в PostgreSQL базе данных.
    """
    
    template_fields = ['sql_query', 'table_name']
    
    @apply_defaults
    def __init__(self,
                 table_name: str,
                 quality_checks: List[Dict[str, Any]],
                 postgres_conn_id: str = 'wildfire_postgres',
                 fail_on_error: bool = True,
                 *args, **kwargs):
        """
        Инициализация оператора проверки качества.
        
        Args:
            table_name: Название таблицы для проверки
            quality_checks: Список проверок качества
            postgres_conn_id: ID подключения к PostgreSQL
            fail_on_error: Прерывать выполнение при ошибке
        """
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.quality_checks = quality_checks
        self.postgres_conn_id = postgres_conn_id
        self.fail_on_error = fail_on_error
    
    def execute(self, context):
        """Выполнение проверок качества данных."""
        logger.info("Starting data quality checks", 
                   table=self.table_name,
                   checks_count=len(self.quality_checks))
        
        postgres_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        
        results = []
        failed_checks = []
        
        for check in self.quality_checks:
            check_name = check.get('name', 'unnamed_check')
            check_sql = check.get('sql')
            expected_result = check.get('expected_result')
            tolerance = check.get('tolerance', 0)
            
            try:
                logger.info("Running quality check", check_name=check_name)
                
                # Выполняем SQL запрос
                result = postgres_hook.get_first(check_sql)
                actual_value = result[0] if result else None
                
                # Проверяем результат
                check_passed = self._evaluate_check(actual_value, expected_result, tolerance)
                
                check_result = {
                    'check_name': check_name,
                    'actual_value': actual_value,
                    'expected_result': expected_result,
                    'tolerance': tolerance,
                    'passed': check_passed,
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(check_result)
                
                if not check_passed:
                    failed_checks.append(check_result)
                    logger.warning("Quality check failed", 
                                 check_name=check_name,
                                 actual=actual_value,
                                 expected=expected_result)
                else:
                    logger.info("Quality check passed", check_name=check_name)
                
            except Exception as e:
                error_result = {
                    'check_name': check_name,
                    'error': str(e),
                    'passed': False,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(error_result)
                failed_checks.append(error_result)
                logger.error("Quality check error", check_name=check_name, error=str(e))
        
        # Сохраняем результаты в XCom
        context['task_instance'].xcom_push(key='quality_check_results', value=results)
        
        # Проверяем результаты
        if failed_checks:
            error_msg = f"Data quality checks failed: {len(failed_checks)} out of {len(self.quality_checks)} checks failed"
            logger.error("Data quality validation failed", 
                        failed_count=len(failed_checks),
                        total_count=len(self.quality_checks))
            
            if self.fail_on_error:
                raise AirflowException(error_msg)
            else:
                logger.warning(error_msg)
        
        logger.info("Data quality checks completed", 
                   passed_count=len(self.quality_checks) - len(failed_checks),
                   failed_count=len(failed_checks))
        
        return results
    
    def _evaluate_check(self, actual: Any, expected: Any, tolerance: float) -> bool:
        """Оценка результата проверки."""
        if expected is None:
            return actual is not None
        
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # Числовое сравнение с допуском
            if tolerance > 0:
                return abs(actual - expected) <= tolerance
            else:
                return actual == expected
        
        # Строковое или точное сравнение
        return actual == expected


class MLModelValidationOperator(BaseOperator):
    """
    Оператор для валидации ML моделей.
    
    Проверяет качество и готовность модели
    перед развертыванием в продакшн.
    """
    
    @apply_defaults
    def __init__(self,
                 model_version: str,
                 min_accuracy: float = 0.8,
                 min_roc_auc: float = 0.85,
                 api_conn_id: str = 'wildfire_api',
                 *args, **kwargs):
        """
        Инициализация оператора валидации модели.
        
        Args:
            model_version: Версия модели для валидации
            min_accuracy: Минимальная точность
            min_roc_auc: Минимальный ROC-AUC
            api_conn_id: ID подключения к API
        """
        super().__init__(*args, **kwargs)
        self.model_version = model_version
        self.min_accuracy = min_accuracy
        self.min_roc_auc = min_roc_auc
        self.api_conn_id = api_conn_id
    
    def execute(self, context):
        """Выполнение валидации модели."""
        logger.info("Starting model validation", 
                   model_version=self.model_version,
                   min_accuracy=self.min_accuracy,
                   min_roc_auc=self.min_roc_auc)
        
        http_hook = HttpHook(http_conn_id=self.api_conn_id, method='GET')
        
        try:
            # Получаем информацию о модели
            response = http_hook.run(
                endpoint=f'/api/v1/models/{self.model_version}'
            )
            
            if response.status_code != 200:
                raise AirflowException(f"Failed to get model info: {response.status_code}")
            
            model_data = response.json().get('data', {})
            
            # Извлекаем метрики
            accuracy = model_data.get('accuracy', 0)
            roc_auc = model_data.get('roc_auc', 0)
            
            # Валидация метрик
            validation_results = {
                'model_version': self.model_version,
                'accuracy': accuracy,
                'roc_auc': roc_auc,
                'min_accuracy': self.min_accuracy,
                'min_roc_auc': self.min_roc_auc,
                'accuracy_passed': accuracy >= self.min_accuracy,
                'roc_auc_passed': roc_auc >= self.min_roc_auc,
                'timestamp': datetime.now().isoformat()
            }
            
            validation_results['overall_passed'] = (
                validation_results['accuracy_passed'] and 
                validation_results['roc_auc_passed']
            )
            
            # Сохраняем результаты
            context['task_instance'].xcom_push(key='validation_results', value=validation_results)
            
            if not validation_results['overall_passed']:
                error_msg = f"Model validation failed: accuracy={accuracy:.3f} (min={self.min_accuracy}), roc_auc={roc_auc:.3f} (min={self.min_roc_auc})"
                logger.error("Model validation failed", **validation_results)
                raise AirflowException(error_msg)
            
            logger.info("Model validation passed", **validation_results)
            return validation_results
            
        except Exception as e:
            logger.error("Model validation error", error=str(e))
            raise AirflowException(f"Model validation failed: {e}")


class SlackNotificationOperator(BaseOperator):
    """
    Оператор для отправки уведомлений в Slack.
    
    Отправляет уведомления о статусе выполнения DAGs
    и критических событиях.
    """
    
    template_fields = ['message', 'channel']
    
    @apply_defaults
    def __init__(self,
                 message: str,
                 channel: str = '#airflow-alerts',
                 slack_conn_id: str = 'slack_default',
                 username: str = 'Airflow',
                 icon_emoji: str = ':robot_face:',
                 *args, **kwargs):
        """
        Инициализация Slack оператора.
        
        Args:
            message: Сообщение для отправки
            channel: Slack канал
            slack_conn_id: ID подключения к Slack
            username: Имя бота
            icon_emoji: Эмодзи иконка
        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.channel = channel
        self.slack_conn_id = slack_conn_id
        self.username = username
        self.icon_emoji = icon_emoji
    
    def execute(self, context):
        """Отправка Slack уведомления."""
        try:
            from slack_sdk import WebClient
            from airflow.hooks.base_hook import BaseHook
            
            # Получаем Slack токен из подключения
            slack_conn = BaseHook.get_connection(self.slack_conn_id)
            slack_token = slack_conn.password
            
            if not slack_token:
                raise AirflowException("Slack token not found in connection")
            
            # Инициализируем Slack клиент
            client = WebClient(token=slack_token)
            
            # Форматируем сообщение с контекстом
            formatted_message = self._format_message(context)
            
            # Отправляем сообщение
            response = client.chat_postMessage(
                channel=self.channel,
                text=formatted_message,
                username=self.username,
                icon_emoji=self.icon_emoji
            )
            
            if response['ok']:
                logger.info("Slack notification sent successfully", 
                           channel=self.channel,
                           message_ts=response['ts'])
            else:
                raise AirflowException(f"Slack API error: {response['error']}")
            
        except Exception as e:
            logger.error("Failed to send Slack notification", error=str(e))
            # Не прерываем выполнение DAG из-за ошибки уведомления
            logger.warning("Continuing DAG execution despite notification failure")
    
    def _format_message(self, context) -> str:
        """Форматирование сообщения с контекстом DAG."""
        dag_id = context['dag'].dag_id
        task_id = context['task'].task_id
        execution_date = context['execution_date']
        
        formatted_message = f"""
*DAG*: {dag_id}
*Task*: {task_id}
*Execution Date*: {execution_date}

{self.message}
        """.strip()
        
        return formatted_message


# Регистрация плагинов
class WildfirePredictionPlugin:
    """Плагин с кастомными операторами."""
    
    name = "wildfire_prediction_plugin"
    operators = [
        CeleryTaskOperator,
        DataQualityCheckOperator,
        MLModelValidationOperator,
        SlackNotificationOperator
    ]
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []