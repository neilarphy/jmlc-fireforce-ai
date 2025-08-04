
"""
Модели для пользователей и сессий.
Следует дизайну из документации.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Index, Text, Float
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    """Пользователи системы"""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
        {"schema": "fireforceai"}
    )
    
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Профиль
    full_name = Column(String(100))
    role = Column(String(20), default='user')  # 'user', 'admin', 'analyst'
    is_active = Column(Boolean, default=True)
    
    # Настройки
    preferences = Column(Text)  # JSON с настройками
    api_key = Column(String(100), unique=True)
    
    # Связи
    sessions = relationship("UserSession", back_populates="user")
    # prediction_requests = relationship("PredictionRequest", back_populates="user")  # Временно отключаем
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

class UserSession(BaseModel):
    """Сессии пользователей"""
    __tablename__ = "user_sessions"
    __table_args__ = (
        Index('idx_user_session_token', 'session_token'),
        Index('idx_user_session_user', 'user_id'),
        {"schema": "fireforceai"}
    )
    
    user_id = Column(Integer, ForeignKey('fireforceai.users.id'))
    session_token = Column(String(255), unique=True, nullable=False)
    
    # Метаданные сессии
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    expires_at = Column(DateTime, nullable=False)
    
    # Статус
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime)
    
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

class LocationCache(BaseModel):
    """Кэш локаций для быстрого поиска"""
    __tablename__ = "location_cache"
    __table_args__ = (
        Index('idx_location_cache_coords', 'latitude', 'longitude'),
        Index('idx_location_cache_name', 'location_name'),
        {"schema": "fireforceai"}
    )
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Геокодинг
    location_name = Column(String(200))
    region = Column(String(100))
    country = Column(String(100))
    
    # Кэш
    last_updated = Column(DateTime)
    usage_count = Column(Integer, default=0)
    

    
    def __repr__(self):
        return f"<LocationCache(id={self.id}, lat={self.latitude}, lon={self.longitude})>"

class PopularLocation(BaseModel):
    """Популярные локации для предсказаний"""
    __tablename__ = "popular_locations"
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(200))
    
    # Статистика использования
    request_count = Column(Integer, default=0)
    last_requested = Column(DateTime)
    
    # Метаданные
    region = Column(String(100))
    risk_level = Column(String(20))  # 'low', 'medium', 'high', 'extreme'
    
    __table_args__ = (
        Index('idx_popular_location_coords', 'latitude', 'longitude'),
        Index('idx_popular_location_usage', 'request_count'),
    )
    
    def __repr__(self):
        return f"<PopularLocation(id={self.id}, name={self.location_name}, requests={self.request_count})>"

class FireStatistics(BaseModel):
    """Статистика пожаров по регионам"""
    __tablename__ = "fire_statistics"
    
    region = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer)
    
    # Статистика
    total_fires = Column(Integer, default=0)
    area_burned = Column(Float)  # в гектарах
    damage_estimate = Column(Float)  # в рублях
    
    # Метаданные
    data_source = Column(String(50))
    last_updated = Column(DateTime)
    
    __table_args__ = (
        Index('idx_fire_statistics_region', 'region'),
        Index('idx_fire_statistics_year', 'year'),
    )
    
    def __repr__(self):
        return f"<FireStatistics(id={self.id}, region={self.region}, year={self.year})>"

class AuditLog(BaseModel):
    """Логи аудита действий пользователей"""
    __tablename__ = "audit_logs"
    __table_args__ = (
        {"schema": "fireforceai"}
    )
    
    user_id = Column(Integer, ForeignKey('fireforceai.users.id'))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    
    # Детали действия
    details = Column(Text)  # JSON с деталями
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Результат
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_log_user', 'user_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>" 