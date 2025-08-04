"""
Общие схемы для API.
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict

class ErrorResponse(BaseModel):
    """Схема для ошибок API"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseModel):
    """Схема для успешных ответов"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None 