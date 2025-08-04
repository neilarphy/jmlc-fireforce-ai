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

def generate_mock_fire_history():
    """Генерирует тестовые данные для истории пожаров"""
    regions = ["Красноярский край", "Иркутская область", "Республика Саха", "Амурская область", "Хабаровский край"]
    
    fires = []
    for i in range(1, 101):
        severity = random.choice(list(FireSeverity))
        status = random.choice(list(FireStatus))
        region = random.choice(regions)
        
        # Генерируем случайную дату в последние 2 года
        days_ago = random.randint(1, 730)
        fire_date = datetime.now() - timedelta(days=days_ago)
        
        fire = HistoricalFireData(
            id=i,
            dt=fire_date,
            latitude=random.uniform(50, 70),
            longitude=random.uniform(80, 140),
            severity=severity,
            status=status,
            region=region,
            area_affected=random.uniform(0.1, 1000.0),
            duration_hours=random.randint(1, 168),
            created_at=fire_date
        )
        fires.append(fire)
    
    return fires

@router.get("/fires", response_model=List[HistoricalFireData])
async def get_fire_history(
    year: str = Query("all", description="Фильтр по году"),
    severity: str = Query("all", description="Фильтр по серьезности"),
    region: str = Query("all", description="Фильтр по региону")
):
    """Получение истории пожаров"""
    try:
        fires = generate_mock_fire_history()
        
        # Фильтруем по году
        if year != "all":
            target_year = int(year)
            fires = [f for f in fires if f.dt.year == target_year]
        
        # Фильтруем по серьезности
        if severity != "all":
            fires = [f for f in fires if f.severity.value == severity]
        
        # Фильтруем по региону
        if region != "all":
            fires = [f for f in fires if f.region == region]
        
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
        fires = generate_mock_fire_history()
        
        # Фильтруем по году
        if year != "all":
            target_year = int(year)
            fires = [f for f in fires if f.dt.year == target_year]
        
        # Подсчитываем статистику
        total_fires = len(fires)
        active_fires = len([f for f in fires if f.status == FireStatus.ACTIVE])
        contained_fires = len([f for f in fires if f.status == FireStatus.CONTAINED])
        extinguished_fires = len([f for f in fires if f.status == FireStatus.EXTINGUISHED])
        
        total_area = sum(f.area_affected or 0 for f in fires)
        avg_duration = sum(f.duration_hours or 0 for f in fires) / len(fires) if fires else 0
        
        # Статистика по серьезности
        fires_by_severity = {}
        for severity in FireSeverity:
            fires_by_severity[severity.value] = len([f for f in fires if f.severity == severity])
        
        # Статистика по регионам
        fires_by_region = {}
        regions = set(f.region for f in fires)
        for region in regions:
            fires_by_region[region] = len([f for f in fires if f.region == region])
        
        statistics = FireStatistics(
            total_fires=total_fires,
            active_fires=active_fires,
            contained_fires=contained_fires,
            extinguished_fires=extinguished_fires,
            total_area_affected=total_area,
            average_duration=avg_duration,
            fires_by_severity=fires_by_severity,
            fires_by_region=fires_by_region
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
        regions = ["Красноярский край", "Иркутская область", "Республика Саха", "Амурская область", "Хабаровский край"]
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
        current_year = datetime.now().year
        years = list(range(current_year - 2, current_year + 1))
        return years
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available years: {str(e)}"
        ) 