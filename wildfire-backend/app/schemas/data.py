"""
Схемы для data endpoints.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FireData(BaseModel):
    """Данные о пожарах"""
    id: int
    dt: datetime
    latitude: float
    longitude: float
    type_name: Optional[str] = None
    type_id: Optional[int] = None
    created_at: datetime

class WeatherData(BaseModel):
    """Метеорологические данные"""
    id: int
    timestamp: datetime
    latitude: float
    longitude: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_u: Optional[float] = None
    wind_v: Optional[float] = None
    precipitation: Optional[float] = None
    created_at: datetime

class StatisticsData(BaseModel):
    """Статистические данные"""
    total_fires: int
    total_predictions: int
    active_models: int
    system_uptime: float
    last_updated: datetime

class RecentFires(BaseModel):
    """Недавние пожары"""
    fires: List[FireData]
    total: int
    page: int
    per_page: int

class HighRiskPredictions(BaseModel):
    """Предсказания высокого риска"""
    predictions: List[dict]  # LocationPrediction
    total: int
    page: int
    per_page: int 