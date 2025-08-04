"""
Модели для предсказаний и ML.
Следует дизайну из документации.
"""
from sqlalchemy import Column, Float, DateTime, String, Integer, ForeignKey, Index, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class TrainingFeatures(BaseModel):
    """Признаки для обучения модели"""
    __tablename__ = "training_features"
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    dt = Column(DateTime, nullable=False)
    
    # Метеопризнаки
    temperature = Column(Float)
    humidity = Column(Float)
    wind_u = Column(Float)
    wind_v = Column(Float)
    precipitation = Column(Float)
    
    # Временные признаки
    year = Column(Integer)
    month = Column(Integer)
    weekday = Column(Integer)
    
    # Сетка координат
    lat_cell = Column(Float)
    lon_cell = Column(Float)
    
    # Целевая переменная
    fire_occurred = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_training_features_coords', 'latitude', 'longitude'),
        Index('idx_training_features_date', 'dt'),
        {"schema": "fireforceai"}
    )
    
    def __repr__(self):
        return f"<TrainingFeatures(id={self.id}, dt={self.dt}, lat={self.latitude}, lon={self.longitude})>"

class FirePrediction(BaseModel):
    """Предсказания пожаров"""
    __tablename__ = "fire_predictions"
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    
    # Результаты предсказания
    risk_score = Column(Float)
    probability = Column(Float)
    risk_level = Column(String(20))  # 'low', 'medium', 'high', 'extreme'
    
    # Модель
    model_version = Column(String(50))
    model_name = Column(String(100))
    
    # Метаданные
    prediction_type = Column(String(20))  # 'single', 'batch', 'scheduled'
    confidence = Column(Float)
    
    __table_args__ = (
        Index('idx_fire_prediction_coords', 'latitude', 'longitude'),
        Index('idx_fire_prediction_date', 'prediction_date'),
        {"schema": "fireforceai"}
    )
    
    def __repr__(self):
        return f"<FirePrediction(id={self.id}, date={self.prediction_date}, lat={self.latitude}, lon={self.longitude})>"

class PredictionRequest(BaseModel):
    """Запросы на предсказания"""
    __tablename__ = "prediction_requests"
    __table_args__ = (
        Index('idx_prediction_request_user', 'user_id'),
        Index('idx_prediction_request_status', 'status'),
        {"schema": "fireforceai"}
    )
    
    user_id = Column(Integer, ForeignKey('fireforceai.users.id'))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    prediction_date = Column(DateTime, nullable=False)
    
    # Статус запроса
    status = Column(String(20))  # 'pending', 'processing', 'completed', 'failed'
    task_id = Column(String(100))  # Celery task ID
    
    # Результат
    prediction_id = Column(Integer, ForeignKey('fireforceai.fire_predictions.id'))
    
    # Метаданные
    request_type = Column(String(20))  # 'immediate', 'scheduled'
    priority = Column(String(20))  # 'low', 'normal', 'high'
    
    # user = relationship("User", back_populates="prediction_requests")  # Временно отключаем
    # prediction = relationship("FirePrediction")  # Временно отключаем
    
    def __repr__(self):
        return f"<PredictionRequest(id={self.id}, user_id={self.user_id}, status={self.status})>"

class ModelVersion(BaseModel):
    """Версии моделей"""
    __tablename__ = "model_versions"
    __table_args__ = (
        Index('idx_model_version_name', 'model_name'),
        Index('idx_model_version_active', 'is_active'),
        {"schema": "fireforceai"}
    )
    
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    
    # Метаданные модели
    mlflow_run_id = Column(String(100))
    model_path = Column(String(500))
    
    # Метрики
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # Статус
    status = Column(String(20))  # 'training', 'active', 'deprecated'
    is_active = Column(Boolean, default=False)
    
    # Конфигурация
    hyperparameters = Column(Text)  # JSON
    feature_columns = Column(Text)  # JSON
    

    
    def __repr__(self):
        return f"<ModelVersion(id={self.id}, model_name={self.model_name}, version={self.version})>"

class BatchPrediction(BaseModel):
    """Пакетные предсказания"""
    __tablename__ = "batch_predictions"
    __table_args__ = (
        Index('idx_batch_prediction_id', 'batch_id'),
        Index('idx_batch_prediction_status', 'status'),
        {"schema": "fireforceai"}
    )
    
    batch_id = Column(String(100), nullable=False)
    model_version = Column(String(50))
    
    # Параметры батча
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    region_bounds = Column(Text)  # JSON с границами региона
    
    # Статус
    status = Column(String(20))  # 'pending', 'processing', 'completed', 'failed'
    progress = Column(Float)  # 0-100%
    
    # Результаты
    total_predictions = Column(Integer)
    completed_predictions = Column(Integer)
    failed_predictions = Column(Integer)
    
    # Метаданные
    created_by = Column(String(100))
    priority = Column(String(20))
    

    
    def __repr__(self):
        return f"<BatchPrediction(id={self.id}, batch_id={self.batch_id}, status={self.status})>" 