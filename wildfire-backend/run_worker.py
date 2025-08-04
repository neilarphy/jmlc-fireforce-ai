#!/usr/bin/env python3
"""
Запуск Celery worker для фоновых задач
"""
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # Запускаем worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--hostname=wildfire-worker@%h"
    ]) 