"""
Модели для данных о пожарах.
Следует дизайну из документации.
"""
from sqlalchemy import Column, Float, Date, String, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class RawFireData(BaseModel):
    """Сырые данные о пожарах из CSV файла russia_fires_hist.csv"""
    __tablename__ = "raw_fire_data"
    
    dt = Column(Date, nullable=False, index=True, comment="Дата пожара")
    type_name = Column(String(50), comment="Тип пожара")
    type_id = Column(Integer, comment="ID типа пожара")
    longitude = Column(Float, nullable=False, index=True, comment="Долгота")
    latitude = Column(Float, nullable=False, index=True, comment="Широта")
    
    processed = Column(Boolean, default=False, comment="Обработана ли запись")
    
    processed_data = relationship("ProcessedFireData", back_populates="raw_fire")
    
    __table_args__ = (
        Index('idx_raw_fire_coords', 'latitude', 'longitude'),
        Index('idx_raw_fire_date_coords', 'dt', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f"<RawFireData(id={self.id}, dt={self.dt}, lat={self.latitude}, lon={self.longitude})>"

class ProcessedFireData(BaseModel):
    """Обработанные данные о пожарах"""
    __tablename__ = "processed_fire_data"
    
    raw_fire_id = Column(Integer, ForeignKey('raw_fire_data.id'))
    dt = Column(Date, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    
    # Временные признаки
    year = Column(Integer)
    month = Column(Integer)
    weekday = Column(Integer)
    
    # Сетка координат 0.5°
    lon_cell = Column(Float)
    lat_cell = Column(Float)
    
    raw_fire = relationship("RawFireData", back_populates="processed_data")
    
    __table_args__ = (
        Index('idx_processed_fire_coords', 'latitude', 'longitude'),
        Index('idx_processed_fire_date', 'dt'),
    )
    
    def __repr__(self):
        return f"<ProcessedFireData(id={self.id}, dt={self.dt}, lat={self.latitude}, lon={self.longitude})>"

class HistoricalFire(BaseModel):
    """Исторические пожары для обучения"""
    __tablename__ = "historical_fires"
    
    dt = Column(Date, nullable=False)
    type_name = Column(String(50))
    type_id = Column(Integer)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    year = Column(Integer)
    month = Column(Integer)
    weekday = Column(Integer)
    lon_cell = Column(Float)
    lat_cell = Column(Float)
    
    __table_args__ = (
        Index('idx_historical_fire_coords', 'latitude', 'longitude'),
        Index('idx_historical_fire_date', 'dt'),
    )
    
    def __repr__(self):
        return f"<HistoricalFire(id={self.id}, dt={self.dt}, lat={self.latitude}, lon={self.longitude})>" 