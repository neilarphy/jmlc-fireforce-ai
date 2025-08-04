"""
Health check endpoints.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

from ..core.config import settings
from ..schemas.health import HealthResponse, DetailedHealthResponse, ServiceStatus
from ..services.mlflow_service import MLflowService
from ..services.minio_service import MinIOService
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/health", tags=["health"])

# Инициализация сервисов
mlflow_service = MLflowService()
# minio_service = MinIOService()  # Отключаем MinIO для тестирования
db_service = DatabaseService()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Базовый health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.VERSION
    )

@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Детальный health check всех сервисов"""
    # Проверяем каждый сервис
    db_status = db_service.test_connection()
    mlflow_status = mlflow_service.test_connection()
    minio_status = {"status": "unknown", "error": "MinIO service disabled"}
    
    # Определяем общий статус
    all_healthy = all([
        db_status.get("status") == "healthy",
        mlflow_status.get("status") == "healthy"
    ])
    
    overall_status = "healthy" if all_healthy else "warning"
    
    # Создаем объекты ServiceStatus
    services = [
        ServiceStatus(
            service="database",
            status=db_status.get("status", "unknown"),
            response_time=None,
            last_check=datetime.now(),
            error_message=db_status.get("error")
        ),
        ServiceStatus(
            service="mlflow", 
            status=mlflow_status.get("status", "unknown"),
            response_time=None,
            last_check=datetime.now(),
            error_message=mlflow_status.get("error")
        ),
        ServiceStatus(
            service="minio",
            status=minio_status.get("status", "unknown"), 
            response_time=None,
            last_check=datetime.now(),
            error_message=minio_status.get("error")
        )
    ]
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        version=settings.VERSION,
        services=services,
        database=services[0],
        redis=ServiceStatus(
            service="redis",
            status="unknown",  # TODO: добавить Redis сервис
            response_time=None,
            last_check=datetime.now(),
            error_message="Redis service not implemented"
        ),
        mlflow=services[1],
        minio=services[2]
    )

@router.get("/services")
async def services_status():
    """Статус всех сервисов"""
    services = {
        "database": db_service.test_connection(),
        "mlflow": mlflow_service.test_connection(),
        "minio": {"status": "unknown", "error": "MinIO service disabled"},
        "redis": {
            "status": "unknown",
            "message": "Redis service not implemented",
            "error": "Not implemented"
        }
    }
    
    return {
        "timestamp": datetime.now(),
        "services": services,
        "overall_status": "healthy" if all(
            s.get("status") == "healthy" for s in services.values()
        ) else "warning"
    }

@router.get("/ready")
async def readiness_check():
    """Проверка готовности системы к работе"""
    # Проверяем критически важные сервисы
    db_status = db_service.test_connection()
    
    if db_status.get("status") != "healthy":
        raise HTTPException(
            status_code=503,
            detail=f"Database is not ready: {db_status.get('message', 'Unknown error')}"
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.now(),
        "message": "System is ready to handle requests"
    } 