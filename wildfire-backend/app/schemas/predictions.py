"""
Схемы для prediction endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PredictionRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Широта")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота")
    region: Optional[str] = Field(None, description="Регион")
    additional_data: Optional[dict] = Field(None, description="Дополнительные данные")

class PredictionResult(BaseModel):
    id: str
    latitude: float
    longitude: float
    risk_level: RiskLevel
    risk_percentage: float = Field(..., ge=0, le=100, description="Процент риска")
    confidence: float = Field(..., ge=0, le=100, description="Уверенность прогноза")
    factors: List[str] = Field(..., description="Факторы риска")
    recommendations: List[str] = Field(..., description="Рекомендации")
    created_at: datetime
    status: str = "completed"

class PredictionStatus(BaseModel):
    id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: Optional[float] = Field(None, ge=0, le=100)
    estimated_time: Optional[int] = Field(None, description="Оставшееся время в секундах")
    result: Optional[PredictionResult] = None

class PredictionHistory(BaseModel):
    id: str
    latitude: float
    longitude: float
    risk_level: RiskLevel
    risk_percentage: float
    confidence: float
    created_at: datetime
    region: Optional[str] = None

class PredictionStats(BaseModel):
    total_predictions: int
    average_risk: float
    high_risk_count: int
    critical_risk_count: int
    recent_predictions: List[PredictionHistory] 