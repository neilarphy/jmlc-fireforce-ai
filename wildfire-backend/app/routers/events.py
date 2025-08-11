"""
Event endpoints for managing fire events and timeline.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from ..schemas.events import FireEvent, EventType, EventSeverity
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/fire-events", tags=["events"])

# Инициализация сервиса
db_service = DatabaseService()

def convert_raw_fire_to_event(raw_fire) -> FireEvent:
    """Конвертирует сырые данные о пожаре в событие для API"""
    # Определяем тип события на основе даты
    event_type = EventType.FIRE_STARTED
    
    # Определяем серьезность на основе типа пожара
    severity_map = {
        "forest": EventSeverity.HIGH,
        "grass": EventSeverity.MEDIUM,
        "brush": EventSeverity.MEDIUM,
        "crop": EventSeverity.LOW,
        "other": EventSeverity.LOW
    }
    
    severity = severity_map.get(raw_fire.get("type_name", "").lower(), EventSeverity.MEDIUM)
    
    # Определяем регион (можно улучшить с геокодингом)
    region = "Россия"  # По умолчанию
    
    return FireEvent(
        id=raw_fire["id"],
        event_type=event_type,
        severity=severity,
        title=f"Пожар {raw_fire['type_name']}",
        description=f"Пожар типа {raw_fire['type_name']} в координатах {raw_fire['latitude']:.4f}, {raw_fire['longitude']:.4f}",
        region=region,
        latitude=raw_fire["latitude"],
        longitude=raw_fire["longitude"],
        timestamp=raw_fire["dt"],
        duration_minutes=60,  # Примерная длительность
        affected_area=1.0,  # Примерная площадь в км²
        created_at=raw_fire["created_at"]
    )

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
        # Получаем реальные данные о пожарах из базы
        raw_fires = db_service.get_fire_data(limit=limit, offset=offset)
        
        # Конвертируем в события
        events = []
        for raw_fire in raw_fires:
            event = convert_raw_fire_to_event(raw_fire)
            
            # Применяем фильтры
            if event_type and event.event_type.value != event_type:
                continue
            if severity and event.severity.value != severity:
                continue
            if region and region.lower() not in event.region.lower():
                continue
                
            events.append(event)
        
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
        # Получаем данные за последние N часов
        cutoff_date = datetime.now() - timedelta(hours=hours)
        
        # Получаем все данные и фильтруем по дате
        raw_fires = db_service.get_fire_data(limit=1000, offset=0)
        
        events = []
        for raw_fire in raw_fires:
            if raw_fire["dt"] >= cutoff_date.date():
                event = convert_raw_fire_to_event(raw_fire)
                events.append(event)
        
        return events
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent events: {str(e)}"
        )

@router.get("/critical", response_model=List[FireEvent])
async def get_critical_events():
    """Получение критических событий"""
    try:
        # Получаем все данные и фильтруем по серьезности
        raw_fires = db_service.get_fire_data(limit=1000, offset=0)
        
        events = []
        for raw_fire in raw_fires:
            event = convert_raw_fire_to_event(raw_fire)
            if event.severity in [EventSeverity.HIGH, EventSeverity.CRITICAL]:
                events.append(event)
        
        return events
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get critical events: {str(e)}"
        )

@router.get("/statistics", response_model=dict)
async def get_events_statistics():
    """Получение статистики событий"""
    try:
        # Получаем все данные для статистики
        raw_fires = db_service.get_fire_data(limit=10000, offset=0)
        
        # Подсчитываем статистику
        total_events = len(raw_fires)
        events_by_type = {}
        events_by_severity = {}
        
        for raw_fire in raw_fires:
            event = convert_raw_fire_to_event(raw_fire)
            
            # Статистика по типам
            type_name = raw_fire["type_name"]
            events_by_type[type_name] = events_by_type.get(type_name, 0) + 1
            
            # Статистика по серьезности
            severity = event.severity.value
            events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
        
        # События за последние 24 часа
        cutoff_date = datetime.now() - timedelta(hours=24)
        events_last_24h = sum(1 for raw_fire in raw_fires if raw_fire["dt"] >= cutoff_date.date())
        
        statistics = {
            "total_events": total_events,
            "events_last_24h": events_last_24h,
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "events_by_region": {"Россия": total_events}  # Пока все в России
        }
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get events statistics: {str(e)}"
        ) 