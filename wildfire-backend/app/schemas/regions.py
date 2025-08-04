"""
Region schemas for API responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RegionData(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    risk_level: str  # low, medium, high, critical
    active_fires: int
    total_area: float
    population: Optional[int] = None
    last_updated: datetime

class RegionRiskAssessment(BaseModel):
    region_id: int
    region_name: str
    risk_score: float  # 0-100
    risk_level: str
    factors: List[str]  # список факторов риска
    recommendations: List[str]  # рекомендации
    last_assessment: datetime 