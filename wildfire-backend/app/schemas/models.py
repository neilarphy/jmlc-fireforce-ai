from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ModelMetrics(BaseModel):
    """Метрики модели"""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc: Optional[float] = None

class ModelInfo(BaseModel):
    """Информация о модели"""
    name: str
    version: str
    filename: str
    path: str
    created_at: datetime
    metrics: Dict = {}
    features: List[str] = []
    size_mb: float

class ModelList(BaseModel):
    """Список моделей"""
    models: List[ModelInfo]
    current_model: Optional[ModelInfo] = None
    total_count: int

class ModelUpload(BaseModel):
    """Загрузка модели"""
    model_name: str = "wildfire_prediction"
    version: str = "1.0.0"
    metrics: Optional[Dict] = None
    features: Optional[List[str]] = None 