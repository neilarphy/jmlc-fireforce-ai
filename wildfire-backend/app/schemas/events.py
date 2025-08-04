"""
Event schemas for API responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    FIRE_STARTED = "fire_started"
    FIRE_CONTAINED = "fire_contained"
    FIRE_EXTINGUISHED = "fire_extinguished"
    ALERT_RAISED = "alert_raised"
    ALERT_RESOLVED = "alert_resolved"
    PREDICTION_MADE = "prediction_made"
    WEATHER_WARNING = "weather_warning"

class EventSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FireEvent(BaseModel):
    id: int
    event_type: EventType
    severity: EventSeverity
    title: str
    description: str
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: datetime
    duration_minutes: Optional[int] = None
    affected_area: Optional[float] = None
    created_at: datetime 