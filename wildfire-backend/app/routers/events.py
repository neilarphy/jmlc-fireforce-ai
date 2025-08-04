"""
Event endpoints for managing fire events and timeline.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

from ..schemas.events import FireEvent, EventType, EventSeverity
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/fire-events", tags=["events"])

# Инициализация сервиса
db_service = DatabaseService()

def generate_mock_events():
    """Генерирует тестовые данные для событий пожаров"""
    regions = ["Красноярский край", "Иркутская область", "Республика Саха", "Амурская область", "Хабаровский край"]
    event_types = [
        (EventType.FIRE_STARTED, "Начало пожара", EventSeverity.HIGH),
        (EventType.FIRE_CONTAINED, "Пожар локализован", EventSeverity.MEDIUM),
        (EventType.FIRE_EXTINGUISHED, "Пожар потушен", EventSeverity.LOW),
        (EventType.ALERT_RAISED, "Поднят алерт", EventSeverity.CRITICAL),
        (EventType.ALERT_RESOLVED, "Алерт снят", EventSeverity.LOW),
        (EventType.PREDICTION_MADE, "Создан прогноз", EventSeverity.MEDIUM),
        (EventType.WEATHER_WARNING, "Погодное предупреждение", EventSeverity.HIGH)
    ]
    
    events = []
    for i in range(1, 51):
        event_type, title, severity = random.choice(event_types)
        region = random.choice(regions)
        
        # Генерируем случайное время в последние 7 дней
        hours_ago = random.randint(1, 168)
        event_time = datetime.now() - timedelta(hours=hours_ago)
        
        event = FireEvent(
            id=i,
            event_type=event_type,
            severity=severity,
            title=f"{title} #{i}",
            description=f"Событие {title.lower()} в регионе {region}. Требуется внимание.",
            region=region,
            latitude=random.uniform(50, 70) if random.choice([True, False]) else None,
            longitude=random.uniform(80, 140) if random.choice([True, False]) else None,
            timestamp=event_time,
            duration_minutes=random.randint(30, 480) if event_type in [EventType.FIRE_STARTED, EventType.FIRE_CONTAINED] else None,
            affected_area=random.uniform(0.1, 100.0) if event_type in [EventType.FIRE_STARTED, EventType.FIRE_CONTAINED] else None,
            created_at=event_time
        )
        events.append(event)
    
    return events

@router.get("", response_model=List[FireEvent])
async def get_fire_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = Query(None, description="Фильтр по типу события"),
    severity: Optional[str] = Query(None, description="Фильтр по серьезности"),
    region: Optional[str] = Query(None, description="Фильтр по региону")
):
    """Получение событий пожаров"""
    try:
        events = generate_mock_events()
        
        # Фильтруем по типу события
        if event_type:
            events = [e for e in events if e.event_type.value == event_type]
        
        # Фильтруем по серьезности
        if severity:
            events = [e for e in events if e.severity.value == severity]
        
        # Фильтруем по региону
        if region:
            events = [e for e in events if e.region == region]
        
        # Сортируем по времени (новые сначала)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Применяем пагинацию
        events = events[offset:offset + limit]
        
        return events
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get fire events: {str(e)}"
        )

@router.get("/recent", response_model=List[FireEvent])
async def get_recent_events(
    hours: int = Query(24, ge=1, le=168, description="Количество часов для фильтрации")
):
    """Получение недавних событий"""
    try:
        events = generate_mock_events()
        
        # Фильтруем по времени
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in events if e.timestamp >= cutoff_time]
        
        # Сортируем по времени (новые сначала)
        recent_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return recent_events[:20]  # Ограничиваем 20 последними событиями
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent events: {str(e)}"
        )

@router.get("/critical", response_model=List[FireEvent])
async def get_critical_events():
    """Получение критических событий"""
    try:
        events = generate_mock_events()
        
        # Фильтруем только критические события
        critical_events = [e for e in events if e.severity == EventSeverity.CRITICAL]
        
        # Сортируем по времени (новые сначала)
        critical_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return critical_events[:10]  # Ограничиваем 10 критическими событиями
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get critical events: {str(e)}"
        )

@router.get("/statistics", response_model=dict)
async def get_events_statistics():
    """Получение статистики событий"""
    try:
        events = generate_mock_events()
        
        # Подсчитываем статистику по типам событий
        events_by_type = {}
        for event_type in EventType:
            events_by_type[event_type.value] = len([e for e in events if e.event_type == event_type])
        
        # Подсчитываем статистику по серьезности
        events_by_severity = {}
        for severity in EventSeverity:
            events_by_severity[severity.value] = len([e for e in events if e.severity == severity])
        
        # Подсчитываем статистику по регионам
        events_by_region = {}
        regions = set(e.region for e in events)
        for region in regions:
            events_by_region[region] = len([e for e in events if e.region == region])
        
        # События за последние 24 часа
        recent_24h = len([e for e in events if e.timestamp >= datetime.now() - timedelta(hours=24)])
        
        statistics = {
            "total_events": len(events),
            "events_last_24h": recent_24h,
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "events_by_region": events_by_region
        }
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get events statistics: {str(e)}"
        ) 