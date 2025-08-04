"""
Celery configuration for background tasks.
"""
from celery import Celery
from .config import settings

# Создание Celery приложения
celery_app = Celery(
    "wildfire_prediction",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.prediction_tasks",
        "app.tasks.data_processing_tasks",
        "app.tasks.model_training_tasks"
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start() 