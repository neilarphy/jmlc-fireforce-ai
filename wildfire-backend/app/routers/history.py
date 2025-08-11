"""
History endpoints for retrieving historical fire data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

from ..schemas.history import (
    HistoricalFireData, FireStatistics, FireFilter,
    FireSeverity, FireStatus
)
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/history", tags=["history"])

# Инициализация сервиса
db_service = DatabaseService()

@router.get("/fires", response_model=List[HistoricalFireData])
async def get_fire_history(
    year: str = Query("all", description="Фильтр по году"),
    severity: str = Query("all", description="Фильтр по серьезности"),
    region: str = Query("all", description="Фильтр по региону")
):
    """Получение истории пожаров из базы данных"""
    try:
        # Получаем данные из базы
        fires_data = db_service.get_historical_fires(year=year, severity=severity, region=region, limit=10000)
        
        # Преобразуем в формат HistoricalFireData
        fires = []
        for fire_data in fires_data:
            # Определяем серьезность на основе типа пожара
            severity_level = FireSeverity.MEDIUM  # По умолчанию
            if fire_data.get('type_name'):
                type_name = fire_data['type_name'].lower()
                if 'критический' in type_name or 'критично' in type_name:
                    severity_level = FireSeverity.CRITICAL
                elif 'высокий' in type_name or 'высоко' in type_name:
                    severity_level = FireSeverity.HIGH
                elif 'низкий' in type_name or 'низко' in type_name:
                    severity_level = FireSeverity.LOW
            
            # Определяем статус (все исторические пожары считаем потушенными)
            status = FireStatus.EXTINGUISHED
            
            fire = HistoricalFireData(
                id=fire_data['id'],
                dt=fire_data['dt'],
                latitude=fire_data['latitude'],
                longitude=fire_data['longitude'],
                severity=severity_level,
                status=status,
                region="Россия",  # Пока используем общий регион
                area_affected=1.0,  # Примерная площадь
                duration_hours=24,  # Примерная длительность
                created_at=fire_data['created_at']
            )
            fires.append(fire)
        
        # Фильтруем по серьезности (если указана)
        if severity != "all":
            fires = [f for f in fires if f.severity.value == severity]
        
        # Фильтруем по региону (пока не используется, так как у нас общий регион)
        if region != "all":
            # Пока пропускаем фильтр по региону
            pass
        
        # Сортируем по дате (новые сначала)
        fires.sort(key=lambda x: x.dt, reverse=True)
        
        return fires
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get fire history: {str(e)}"
        )

@router.get("/statistics", response_model=FireStatistics)
async def get_fire_statistics(
    year: str = Query("all", description="Фильтр по году")
):
    """Получение статистики пожаров"""
    try:
        # Получаем статистику из базы
        stats = db_service.get_fire_statistics(year=year)
        
        # Преобразуем в формат FireStatistics
        statistics = FireStatistics(
            total_fires=stats['total_fires'],
            active_fires=0,  # Все исторические пожары потушены
            contained_fires=0,
            extinguished_fires=stats['total_fires'],
            total_area_affected=stats['total_fires'] * 1.0,  # Примерная площадь
            average_duration=24.0,  # Примерная длительность
            fires_by_severity={
                'low': stats['fires_by_type'].get('low', 0),
                'medium': stats['fires_by_type'].get('medium', 0),
                'high': stats['fires_by_type'].get('high', 0),
                'critical': stats['fires_by_type'].get('critical', 0)
            },
            fires_by_region={'Россия': stats['total_fires']}
        )
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get fire statistics: {str(e)}"
        )

@router.get("/regions", response_model=List[str])
async def get_regions():
    """Получение списка регионов"""
    try:
        # Пока возвращаем общий регион, так как в данных нет разделения по регионам
        regions = ["Россия"]
        return regions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get regions: {str(e)}"
        )

@router.get("/years", response_model=List[int])
async def get_available_years():
    """Получение списка доступных лет"""
    try:
        # Получаем годы из базы данных
        years = db_service.get_available_years()
        return years
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available years: {str(e)}"
        ) 