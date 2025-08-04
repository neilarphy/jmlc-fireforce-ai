"""
Worker endpoints for managing background tasks and workers.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

from ..schemas.workers import WorkerTask, WorkerStatus, TaskStatus, TaskType
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/v1/workers", tags=["workers"])

# Инициализация сервиса
db_service = DatabaseService()

def generate_mock_tasks():
    """Генерирует тестовые данные для задач"""
    task_types = [
        (TaskType.DATA_PROCESSING, "Обработка данных о пожарах", "Обработка новых данных о пожарах из различных источников"),
        (TaskType.MODEL_TRAINING, "Обучение модели", "Обучение модели предсказания пожаров на новых данных"),
        (TaskType.PREDICTION, "Создание прогноза", "Генерация прогноза риска пожаров для регионов"),
        (TaskType.ALERT_GENERATION, "Генерация алертов", "Анализ данных и создание алертов"),
        (TaskType.REPORT_GENERATION, "Создание отчета", "Генерация еженедельного отчета по пожарам")
    ]
    
    tasks = []
    for i in range(1, 21):
        task_type, title, description = random.choice(task_types)
        status = random.choice(list(TaskStatus))
        
        # Генерируем время создания
        hours_ago = random.randint(1, 72)
        created_at = datetime.now() - timedelta(hours=hours_ago)
        
        # Генерируем прогресс в зависимости от статуса
        if status == TaskStatus.COMPLETED:
            progress = 100.0
            started_at = created_at + timedelta(minutes=random.randint(1, 30))
            completed_at = started_at + timedelta(minutes=random.randint(10, 120))
        elif status == TaskStatus.RUNNING:
            progress = random.uniform(10.0, 90.0)
            started_at = created_at + timedelta(minutes=random.randint(1, 30))
            completed_at = None
        elif status == TaskStatus.FAILED:
            progress = random.uniform(10.0, 80.0)
            started_at = created_at + timedelta(minutes=random.randint(1, 30))
            completed_at = started_at + timedelta(minutes=random.randint(5, 60))
        else:
            progress = 0.0
            started_at = None
            completed_at = None
        
        task = WorkerTask(
            id=f"task_{i:03d}",
            task_type=task_type,
            status=status,
            title=f"{title} #{i}",
            description=description,
            progress=progress,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            error_message="Ошибка обработки данных" if status == TaskStatus.FAILED else None,
            result={"processed_records": random.randint(100, 10000)} if status == TaskStatus.COMPLETED else None
        )
        tasks.append(task)
    
    return tasks

@router.get("/tasks/active", response_model=List[WorkerTask])
async def get_active_tasks():
    """Получение активных задач"""
    try:
        tasks = generate_mock_tasks()
        
        # Фильтруем только активные задачи (pending, running)
        active_tasks = [t for t in tasks if t.status in [TaskStatus.PENDING, TaskStatus.RUNNING]]
        
        # Сортируем по времени создания (новые сначала)
        active_tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        return active_tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active tasks: {str(e)}"
        )

@router.get("/tasks/completed", response_model=List[WorkerTask])
async def get_completed_tasks(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Получение завершенных задач"""
    try:
        tasks = generate_mock_tasks()
        
        # Фильтруем только завершенные задачи
        completed_tasks = [t for t in tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]]
        
        # Сортируем по времени завершения (новые сначала)
        completed_tasks.sort(key=lambda x: x.completed_at or x.created_at, reverse=True)
        
        # Применяем пагинацию
        completed_tasks = completed_tasks[offset:offset + limit]
        
        return completed_tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get completed tasks: {str(e)}"
        )

@router.get("/tasks/{task_id}", response_model=WorkerTask)
async def get_task_details(task_id: str):
    """Получение деталей конкретной задачи"""
    try:
        tasks = generate_mock_tasks()
        
        # Ищем задачу по ID
        task = next((t for t in tasks if t.id == task_id), None)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task details: {str(e)}"
        )

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Отмена задачи"""
    try:
        # В реальном приложении здесь была бы логика отмены задачи
        return {
            "message": f"Task {task_id} cancelled successfully",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )

@router.get("/status", response_model=List[WorkerStatus])
async def get_workers_status():
    """Получение статуса воркеров"""
    try:
        # Генерируем тестовые данные о статусе воркеров
        workers = []
        for i in range(1, 4):
            status = random.choice(["online", "offline", "busy"])
            worker = WorkerStatus(
                worker_id=f"worker_{i:02d}",
                status=status,
                active_tasks=random.randint(0, 5) if status != "offline" else 0,
                completed_tasks=random.randint(10, 100),
                failed_tasks=random.randint(0, 10),
                last_heartbeat=datetime.now() - timedelta(minutes=random.randint(1, 30))
            )
            workers.append(worker)
        
        return workers
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workers status: {str(e)}"
        )

@router.get("/statistics", response_model=dict)
async def get_workers_statistics():
    """Получение статистики воркеров"""
    try:
        tasks = generate_mock_tasks()
        
        # Подсчитываем статистику
        total_tasks = len(tasks)
        pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
        running_tasks = len([t for t in tasks if t.status == TaskStatus.RUNNING])
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in tasks if t.status == TaskStatus.FAILED])
        
        # Статистика по типам задач
        tasks_by_type = {}
        for task_type in TaskType:
            tasks_by_type[task_type.value] = len([t for t in tasks if t.task_type == task_type])
        
        statistics = {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "tasks_by_type": tasks_by_type
        }
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workers statistics: {str(e)}"
        ) 