"""
Схемы для health endpoints.
"""
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ServiceStatus(BaseModel):
    """Статус отдельного сервиса"""
    service: str
    status: str  # 'healthy', 'warning', 'critical'
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None

class HealthResponse(BaseModel):
    """Базовый ответ health check"""
    status: str
    timestamp: datetime
    version: str

class DetailedHealthResponse(BaseModel):
    """Детальный ответ health check"""
    status: str
    timestamp: datetime
    version: str
    services: List[ServiceStatus]
    database: ServiceStatus
    redis: ServiceStatus
    mlflow: ServiceStatus
    minio: ServiceStatus 