"""
Health check endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..schemas.health import HealthResponse, DetailedHealthResponse, ServiceStatus
from ..services.mlflow_service import MLflowService
from ..services.minio_service import MinIOService
from ..services.database_service import DatabaseService
from ..models.prediction import FirePrediction
from ..models.fire import HistoricalFire

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

@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Получение статистики для дашборда"""
    try:
        # Получаем статистику за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Активные пожары (за последние 24 часа) - используем исторические данные
        active_fires = db.query(HistoricalFire).filter(
            HistoricalFire.dt >= datetime.now().date() - timedelta(days=1)
        ).count()
        
        # Зоны высокого риска за 7 дней по трешхолду вероятности (>= 70%)
        # Поддерживаем два варианта хранения risk_percentage: [0..1] и [0..100]
        seven_days_ago = datetime.now() - timedelta(days=7)
        threshold_low_scale = 0.50
        threshold_high_scale = 50.0

        # считаем как объединение записей, где либо доли >= 0.70, либо проценты >= 70
        from sqlalchemy import or_
        high_risk_zones = db.query(FirePrediction).filter(
            and_(
                FirePrediction.prediction_date >= seven_days_ago,
                or_(
                    FirePrediction.risk_score >= threshold_low_scale,           # 0..1
                    FirePrediction.probability >= threshold_low_scale,          # 0..1
                    FirePrediction.risk_level.in_(['high', 'critical'])
                )
            )
        ).count()

        # Fallback: если за 7 дней нет, считаем по всем записям
        if high_risk_zones == 0:
            high_risk_zones = db.query(FirePrediction).filter(
                or_(
                    FirePrediction.risk_score >= threshold_low_scale,
                    FirePrediction.probability >= threshold_low_scale,
                    FirePrediction.risk_level.in_(['high', 'critical'])
                )
            ).count()
        
        # Средняя точность прогноза (среднее значение confidence за последние 30 дней)
        avg_confidence = db.query(func.avg(FirePrediction.confidence)).filter(
            FirePrediction.prediction_date >= thirty_days_ago
        ).scalar()
        
        # Если нет данных, используем значение по умолчанию
        if avg_confidence is None:
            avg_confidence = 0.85  # дефолт в долях
        
        # Активные команды (пока используем фиксированное значение)
        active_teams = 12
        
        # Общее количество пожаров за месяц
        total_fires_month = db.query(HistoricalFire).filter(
            HistoricalFire.dt >= thirty_days_ago.date()
        ).count()
        
        return {
            "key_metrics": {
                "active_fires": active_fires,
                "high_risk_zones": high_risk_zones,
                # Переводим к процентам, поддерживая оба формата хранения (0-1 или 0-100)
                "prediction_accuracy": (round(float(avg_confidence) * 100.0, 1)
                                         if float(avg_confidence) <= 1.0
                                         else round(float(avg_confidence), 1)),
                "active_teams": active_teams
            },
            "fire_stats": {
                "total_fires_month": total_fires_month
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dashboard stats: {str(e)}"
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