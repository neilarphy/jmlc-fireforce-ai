"""
Region endpoints for managing high-risk regions and assessments.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import random

from ..schemas.regions import RegionData, RegionRiskAssessment
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/regions", tags=["regions"])

# Инициализация сервиса
db_service = DatabaseService()

def generate_mock_regions():
    """Генерирует тестовые данные для регионов"""
    regions_data = [
        {
            "name": "Красноярский край",
            "lat": 56.0184,
            "lon": 92.8672,
            "risk_level": "high",
            "active_fires": 5,
            "total_area": 2366797.0,
            "population": 2877000
        },
        {
            "name": "Иркутская область",
            "lat": 52.2864,
            "lon": 104.3050,
            "risk_level": "critical",
            "active_fires": 8,
            "total_area": 774846.0,
            "population": 2402000
        },
        {
            "name": "Республика Саха",
            "lat": 66.2654,
            "lon": 129.6755,
            "risk_level": "medium",
            "active_fires": 3,
            "total_area": 3083523.0,
            "population": 964000
        },
        {
            "name": "Амурская область",
            "lat": 50.2904,
            "lon": 127.5272,
            "risk_level": "high",
            "active_fires": 4,
            "total_area": 361908.0,
            "population": 801000
        },
        {
            "name": "Хабаровский край",
            "lat": 48.4802,
            "lon": 135.0719,
            "risk_level": "medium",
            "active_fires": 2,
            "total_area": 787633.0,
            "population": 1328000
        }
    ]
    
    regions = []
    for i, region_data in enumerate(regions_data, 1):
        region = RegionData(
            id=i,
            name=region_data["name"],
            latitude=region_data["lat"],
            longitude=region_data["lon"],
            risk_level=region_data["risk_level"],
            active_fires=region_data["active_fires"],
            total_area=region_data["total_area"],
            population=region_data["population"],
            last_updated=datetime.now() - timedelta(hours=random.randint(1, 24))
        )
        regions.append(region)
    
    return regions

@router.get("/high-risk", response_model=List[RegionData])
async def get_high_risk_regions():
    """Получение регионов с высоким риском"""
    try:
        regions = generate_mock_regions()
        
        # Фильтруем только регионы с высоким и критическим риском
        high_risk_regions = [r for r in regions if r.risk_level in ["high", "critical"]]
        
        # Сортируем по количеству активных пожаров (больше сначала)
        high_risk_regions.sort(key=lambda x: x.active_fires, reverse=True)
        
        return high_risk_regions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get high-risk regions: {str(e)}"
        )

@router.get("/all", response_model=List[RegionData])
async def get_all_regions():
    """Получение всех регионов"""
    try:
        regions = generate_mock_regions()
        return regions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get all regions: {str(e)}"
        )

@router.get("/{region_id}/assessment", response_model=RegionRiskAssessment)
async def get_region_assessment(region_id: int):
    """Получение оценки риска для конкретного региона"""
    try:
        regions = generate_mock_regions()
        
        if region_id < 1 or region_id > len(regions):
            raise HTTPException(status_code=404, detail="Region not found")
        
        region = regions[region_id - 1]
        
        # Генерируем факторы риска в зависимости от уровня риска
        risk_factors = []
        if region.risk_level == "critical":
            risk_factors = [
                "Высокая температура воздуха",
                "Низкая влажность",
                "Сильные ветры",
                "Сухая растительность",
                "Человеческий фактор"
            ]
        elif region.risk_level == "high":
            risk_factors = [
                "Повышенная температура",
                "Средняя влажность",
                "Умеренные ветры",
                "Сухая растительность"
            ]
        else:
            risk_factors = [
                "Нормальная температура",
                "Адекватная влажность",
                "Слабые ветры"
            ]
        
        # Генерируем рекомендации
        recommendations = [
            "Усилить мониторинг лесных массивов",
            "Подготовить силы пожаротушения",
            "Провести профилактические мероприятия",
            "Установить дополнительные датчики"
        ]
        
        # Рассчитываем риск-скор
        risk_score_map = {"low": 25, "medium": 50, "high": 75, "critical": 90}
        risk_score = risk_score_map.get(region.risk_level, 50)
        
        assessment = RegionRiskAssessment(
            region_id=region.id,
            region_name=region.name,
            risk_score=risk_score,
            risk_level=region.risk_level,
            factors=risk_factors,
            recommendations=recommendations,
            last_assessment=datetime.now() - timedelta(hours=random.randint(1, 12))
        )
        
        return assessment
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get region assessment: {str(e)}"
        )

@router.get("/statistics", response_model=dict)
async def get_regions_statistics():
    """Получение статистики по регионам"""
    try:
        regions = generate_mock_regions()
        
        total_regions = len(regions)
        critical_regions = len([r for r in regions if r.risk_level == "critical"])
        high_risk_regions = len([r for r in regions if r.risk_level == "high"])
        medium_risk_regions = len([r for r in regions if r.risk_level == "medium"])
        low_risk_regions = len([r for r in regions if r.risk_level == "low"])
        
        total_active_fires = sum(r.active_fires for r in regions)
        total_population = sum(r.population or 0 for r in regions)
        
        statistics = {
            "total_regions": total_regions,
            "critical_regions": critical_regions,
            "high_risk_regions": high_risk_regions,
            "medium_risk_regions": medium_risk_regions,
            "low_risk_regions": low_risk_regions,
            "total_active_fires": total_active_fires,
            "total_population": total_population,
            "average_risk_score": sum(25 if r.risk_level == "low" else 50 if r.risk_level == "medium" else 75 if r.risk_level == "high" else 90 for r in regions) / total_regions
        }
        
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get regions statistics: {str(e)}"
        ) 