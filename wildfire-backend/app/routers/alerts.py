"""
Alert endpoints for managing fire alerts and notifications.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

from ..schemas.alerts import (
    AlertData, AlertSummary, NotificationSettings, AlertFilter,
    AlertSeverity, AlertStatus
)
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/alerts", tags=["alerts"])

# Инициализация сервиса
db_service = DatabaseService()

def generate_mock_alerts():
    """Генерирует тестовые данные для алертов"""
    regions = ["Красноярский край", "Иркутская область", "Республика Саха", "Амурская область", "Хабаровский край"]
    alert_types = [
        "Пожар в лесной зоне",
        "Возгорание в населенном пункте",
        "Лесной пожар высокой интенсивности",
        "Угроза распространения огня",
        "Критическая ситуация с пожаром"
    ]
    
    alerts = []
    for i in range(1, 21):
        severity = random.choice(list(AlertSeverity))
        status = random.choice(list(AlertStatus))
        region = random.choice(regions)
        alert_type = random.choice(alert_types)
        
        alert = AlertData(
            id=i,
            title=f"Алерт #{i}: {alert_type}",
            description=f"Обнаружен {alert_type.lower()} в регионе {region}. Требуется немедленное реагирование.",
            severity=severity,
            status=status,
            region=region,
            latitude=random.uniform(50, 70),
            longitude=random.uniform(80, 140),
            created_at=datetime.now() - timedelta(hours=random.randint(1, 72)),
            updated_at=datetime.now() - timedelta(hours=random.randint(0, 24)),
            expires_at=datetime.now() + timedelta(hours=random.randint(1, 48)) if status == AlertStatus.ACTIVE else None
        )
        alerts.append(alert)
    
    return alerts

@router.get("/summary", response_model=AlertSummary)
async def get_alerts_summary():
    """Получение сводки по алертам"""
    try:
        # Генерируем тестовые данные
        alerts = generate_mock_alerts()
        
        summary = AlertSummary(
            total_alerts=len(alerts),
            active_alerts=len([a for a in alerts if a.status == AlertStatus.ACTIVE]),
            critical_alerts=len([a for a in alerts if a.severity == AlertSeverity.CRITICAL and a.status == AlertStatus.ACTIVE]),
            high_alerts=len([a for a in alerts if a.severity == AlertSeverity.HIGH and a.status == AlertStatus.ACTIVE]),
            medium_alerts=len([a for a in alerts if a.severity == AlertSeverity.MEDIUM and a.status == AlertStatus.ACTIVE]),
            low_alerts=len([a for a in alerts if a.severity == AlertSeverity.LOW and a.status == AlertStatus.ACTIVE]),
            resolved_today=len([a for a in alerts if a.status == AlertStatus.RESOLVED and a.updated_at.date() == datetime.now().date()])
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alerts summary: {str(e)}"
        )

@router.get("/active", response_model=List[AlertData])
async def get_active_alerts(
    severity: str = Query("all", description="Фильтр по серьезности"),
    region: str = Query("all", description="Фильтр по региону")
):
    """Получение активных алертов"""
    try:
        alerts = generate_mock_alerts()
        
        # Фильтруем по статусу
        active_alerts = [a for a in alerts if a.status == AlertStatus.ACTIVE]
        
        # Фильтруем по серьезности
        if severity != "all":
            active_alerts = [a for a in active_alerts if a.severity.value == severity]
        
        # Фильтруем по региону
        if region != "all":
            active_alerts = [a for a in active_alerts if a.region == region]
        
        return active_alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active alerts: {str(e)}"
        )

@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings():
    """Получение настроек уведомлений"""
    try:
        # Возвращаем настройки по умолчанию
        settings = NotificationSettings()
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification settings: {str(e)}"
        )

@router.put("/settings")
async def update_notification_settings(settings: NotificationSettings):
    """Обновление настроек уведомлений"""
    try:
        # В реальном приложении здесь была бы логика сохранения в БД
        return {"message": "Notification settings updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update notification settings: {str(e)}"
        )

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int):
    """Подтверждение получения алерта"""
    try:
        # В реальном приложении здесь была бы логика обновления статуса в БД
        return {"message": f"Alert {alert_id} acknowledged successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    """Разрешение алерта"""
    try:
        # В реальном приложении здесь была бы логика обновления статуса в БД
        return {"message": f"Alert {alert_id} resolved successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve alert: {str(e)}"
        ) 