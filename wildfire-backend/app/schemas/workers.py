"""
Worker schemas for API responses.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    DATA_PROCESSING = "data_processing"
    MODEL_TRAINING = "model_training"
    PREDICTION = "prediction"
    ALERT_GENERATION = "alert_generation"
    REPORT_GENERATION = "report_generation"

class WorkerTask(BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    title: str
    description: str
    progress: float  # 0-100
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[dict] = None

class WorkerStatus(BaseModel):
    worker_id: str
    status: str  # online, offline, busy
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    last_heartbeat: datetime 