"""
History schemas for API responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class FireSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FireStatus(str, Enum):
    ACTIVE = "active"
    CONTAINED = "contained"
    EXTINGUISHED = "extinguished"

class HistoricalFireData(BaseModel):
    id: int
    dt: datetime
    latitude: float
    longitude: float
    severity: FireSeverity
    status: FireStatus
    region: str
    area_affected: Optional[float] = None
    duration_hours: Optional[int] = None
    created_at: datetime

class FireStatistics(BaseModel):
    total_fires: int
    active_fires: int
    contained_fires: int
    extinguished_fires: int
    total_area_affected: float
    average_duration: float
    fires_by_severity: dict
    fires_by_region: dict

class FireFilter(BaseModel):
    year: Optional[str] = "all"
    severity: Optional[str] = "all"
    region: Optional[str] = "all"
    status: Optional[str] = "all" 