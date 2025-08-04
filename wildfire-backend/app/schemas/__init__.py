# Schemas package
from .health import HealthResponse, ServiceStatus, DetailedHealthResponse
from .predictions import (
    PredictionRequest, PredictionResult, PredictionStatus, 
    PredictionHistory, PredictionStats, RiskLevel
)
from .data import (
    FireData, WeatherData, StatisticsData, 
    RecentFires, HighRiskPredictions
)
from .common import ErrorResponse, SuccessResponse

__all__ = [
    "HealthResponse", "ServiceStatus", "DetailedHealthResponse",
    "PredictionRequest", "PredictionResult", "PredictionStatus",
    "PredictionHistory", "PredictionStats", "RiskLevel",
    "FireData", "WeatherData", "StatisticsData",
    "RecentFires", "HighRiskPredictions",
    "ErrorResponse", "SuccessResponse",
] 