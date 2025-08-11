"""
Data endpoints for retrieving fire, weather, and statistics data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.data import (
    FireData, WeatherData, StatisticsData,
    RecentFires, HighRiskPredictions
)
from ..services.database_service import DatabaseService
from ..services.rosleshoz_service import fetch_latest_operational_info
from ..services.region_centroids import regions_to_points

router = APIRouter(prefix="/data", tags=["data"])

# Инициализация сервиса
db_service = DatabaseService()

@router.get("/fires", response_model=List[FireData])
async def get_fire_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Получение данных о пожарах"""
    try:
        fires_data = db_service.get_fire_data(limit=limit, offset=offset)
        
        fires = []
        for fire_data in fires_data:
            fires.append(FireData(
                id=fire_data["id"],
                dt=fire_data["dt"],
                latitude=fire_data["latitude"],
                longitude=fire_data["longitude"],
                type_name=fire_data["type_name"],
                type_id=fire_data["type_id"],
                created_at=fire_data["created_at"]
            ))
        
        return fires
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get fire data: {str(e)}"
        )

@router.get("/weather", response_model=List[WeatherData])
async def get_weather_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Получение метеорологических данных"""
    try:
        weather_data = db_service.get_weather_data(limit=limit, offset=offset)
        
        weather = []
        for w_data in weather_data:
            weather.append(WeatherData(
                id=w_data["id"],
                timestamp=w_data["timestamp"],
                latitude=w_data["latitude"],
                longitude=w_data["longitude"],
                temperature=w_data["temperature_2m"],
                humidity=w_data["relative_humidity"],
                wind_u=w_data["wind_u"],
                wind_v=w_data["wind_v"],
                precipitation=w_data["precipitation"],
                created_at=w_data["created_at"]
            ))
        
        return weather
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get weather data: {str(e)}"
        )

@router.get("/predictions", response_model=List[dict])
async def get_predictions_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Получение данных о предсказаниях"""
    try:
        predictions_data = db_service.get_predictions(limit=limit, offset=offset)
        return predictions_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get predictions data: {str(e)}"
        )

@router.get("/users", response_model=List[dict])
async def get_users_data(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Получение данных о пользователях"""
    try:
        users_data = db_service.get_users(limit=limit, offset=offset)
        return users_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get users data: {str(e)}"
        )

@router.get("/statistics", response_model=StatisticsData)
async def get_statistics():
    """Получение статистических данных"""
    try:
        stats_data = db_service.get_statistics()
        
        return StatisticsData(
            total_fires=stats_data["total_fires"],
            total_predictions=stats_data["total_predictions"],
            active_models=1,  # TODO: получить из MLflow
            system_uptime=99.9,  # TODO: рассчитать реальный uptime
            last_updated=stats_data["last_updated"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )

@router.get("/recent-fires", response_model=RecentFires)
async def get_recent_fires(
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(50, ge=1, le=500)
):
    """Получение недавних пожаров"""
    try:
        fires_data = db_service.get_recent_fires(days=days, limit=limit)
        
        fires = []
        for fire_data in fires_data:
            fires.append(FireData(
                id=fire_data["id"],
                dt=fire_data["dt"],
                latitude=fire_data["latitude"],
                longitude=fire_data["longitude"],
                type_name=fire_data["type_name"],
                type_id=fire_data.get("type_id"),
                created_at=fire_data["created_at"]
            ))
        
        return RecentFires(
            fires=fires,
            total=len(fires),
            page=1,
            per_page=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent fires: {str(e)}"
        )

@router.get("/high-risk-predictions", response_model=HighRiskPredictions)
async def get_high_risk_predictions(
    limit: int = Query(50, ge=1, le=500)
):
    """Получение предсказаний высокого риска"""
    try:
        predictions_data = db_service.get_high_risk_predictions(limit=limit)
        
        return HighRiskPredictions(
            predictions=predictions_data,
            total=len(predictions_data),
            page=1,
            per_page=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get high risk predictions: {str(e)}"
        ) 


@router.get("/rosleshoz/operative")
async def rosleshoz_operative():
    """Оперативная информация Рослесхоза (прокси/парсер)."""
    data = fetch_latest_operational_info()
    # Не падаем 502 — отдаём фолбэк с полями и сообщением
    if data and isinstance(data.get("regions"), list):
        data["region_points"] = regions_to_points(data["regions"])  # add approximate points
    else:
        data["region_points"] = []
    return data