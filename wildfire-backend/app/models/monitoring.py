"""
Модели для мониторинга системы.
Следует дизайну из документации.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class SystemHealth(BaseModel):
    """Мониторинг здоровья системы"""
    __tablename__ = "system_health"
    
    service_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # 'healthy', 'warning', 'critical'
    
    # Метрики
    response_time = Column(Float)  # в миллисекундах
    error_rate = Column(Float)  # процент ошибок
    uptime = Column(Float)  # в процентах
    
    # Детали
    last_check = Column(DateTime)
    error_message = Column(Text)
    configuration = Column(JSON)  # конфигурация сервиса
    
    __table_args__ = (
        Index('idx_system_health_service', 'service_name'),
        Index('idx_system_health_status', 'status'),
    )
    
    def __repr__(self):
        return f"<SystemHealth(id={self.id}, service={self.service_name}, status={self.status})>"

class ErrorLog(BaseModel):
    """Логи ошибок системы"""
    __tablename__ = "error_logs"
    
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    
    # Контекст ошибки
    module = Column(String(100))
    function = Column(String(100))
    line_number = Column(Integer)
    
    # Детали
    stack_trace = Column(Text)
    request_data = Column(JSON)
    user_id = Column(Integer)
    
    # Статус обработки
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    
    __table_args__ = (
        Index('idx_error_log_type', 'error_type'),
        Index('idx_error_log_created', 'created_at'),
        Index('idx_error_log_resolved', 'is_resolved'),
    )
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type={self.error_type}, resolved={self.is_resolved})>"

class SystemSettings(BaseModel):
    """Настройки системы"""
    __tablename__ = "system_settings"
    
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    
    # Метаданные
    description = Column(Text)
    category = Column(String(50))  # 'api', 'ml', 'database', 'monitoring'
    is_public = Column(Boolean, default=False)  # доступно ли через API
    
    # Валидация
    value_type = Column(String(20))  # 'string', 'integer', 'float', 'boolean', 'json'
    validation_rules = Column(JSON)
    
    __table_args__ = (
        Index('idx_system_settings_key', 'setting_key'),
        Index('idx_system_settings_category', 'category'),
    )
    
    def __repr__(self):
        return f"<SystemSettings(id={self.id}, key={self.setting_key})>" 