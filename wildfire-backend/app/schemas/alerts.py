"""
Alert schemas for API responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"

class AlertData(BaseModel):
    id: int
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

class AlertSummary(BaseModel):
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    resolved_today: int

class NotificationSettings(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    critical_alerts_only: bool = False
    notification_frequency: str = "immediate"  # immediate, hourly, daily

class AlertFilter(BaseModel):
    severity: Optional[str] = "all"
    region: Optional[str] = "all"
    status: Optional[str] = "active" 