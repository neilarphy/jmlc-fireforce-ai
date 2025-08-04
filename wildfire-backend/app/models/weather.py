"""
Модели для метеорологических данных.
Следует дизайну из документации.
"""
from sqlalchemy import Column, Float, DateTime, String, Integer, ForeignKey, Index, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class RawWeatherData(BaseModel):
    """Сырые метеорологические данные из NetCDF файлов ERA5"""
    __tablename__ = "raw_weather_data"
    
    latitude = Column(Float, nullable=False, index=True, comment="Широта")
    longitude = Column(Float, nullable=False, index=True, comment="Долгота")
    timestamp = Column(DateTime, nullable=False, index=True, comment="Дата/время измерения")
    
    temperature_2m = Column(Float, comment="Температура на высоте 2м (°C)")
    relative_humidity = Column(Float, comment="Относительная влажность (%)")
    wind_u = Column(Float, comment="U-компонента ветра (м/с)")
    wind_v = Column(Float, comment="V-компонента ветра (м/с)")
    precipitation = Column(Float, comment="Осадки (мм)")
    
    data_source = Column(String(20), default='ERA5', comment="Источник данных")
    processed = Column(Boolean, default=False, comment="Обработана ли запись")
    
    processed_data = relationship("ProcessedWeatherData", back_populates="raw_weather")
    
    __table_args__ = (
        Index('idx_raw_weather_coords_time', 'latitude', 'longitude', 'timestamp'),
        Index('idx_raw_weather_coords', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f"<RawWeatherData(id={self.id}, timestamp={self.timestamp}, lat={self.latitude}, lon={self.longitude})>"

class ProcessedWeatherData(BaseModel):
    """Обработанные метеоданные на сетке 0.5°"""
    __tablename__ = "processed_weather_data"
    
    raw_weather_id = Column(Integer, ForeignKey('raw_weather_data.id'))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Нормализованные параметры
    temperature = Column(Float)
    humidity = Column(Float)
    wind_u = Column(Float)
    wind_v = Column(Float)
    precipitation = Column(Float)
    
    # Сетка координат
    lat_cell = Column(Float)
    lon_cell = Column(Float)
    
    raw_weather = relationship("RawWeatherData", back_populates="processed_data")
    
    __table_args__ = (
        Index('idx_processed_weather_coords_time', 'latitude', 'longitude', 'timestamp'),
        Index('idx_processed_weather_coords', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f"<ProcessedWeatherData(id={self.id}, timestamp={self.timestamp}, lat={self.latitude}, lon={self.longitude})>"

class DataProcessingLog(BaseModel):
    """Логи обработки данных"""
    __tablename__ = "data_processing_logs"
    
    process_type = Column(String(50))  # 'weather', 'fire', 'training'
    status = Column(String(20))        # 'started', 'completed', 'failed'
    records_processed = Column(Integer)
    error_message = Column(Text)
    processing_time_seconds = Column(Float)
    
    def __repr__(self):
        return f"<DataProcessingLog(id={self.id}, process_type={self.process_type}, status={self.status})>" 