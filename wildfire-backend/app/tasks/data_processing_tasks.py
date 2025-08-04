"""
Celery tasks for data processing.
"""
from celery import current_task
from typing import Dict, Any, List
import logging
import pandas as pd
from datetime import datetime, timedelta

from ..core.celery_app import celery_app
from ..services.database_service import DatabaseService
from ..services.minio_service import MinIOService

logger = logging.getLogger(__name__)

db_service = DatabaseService()
minio_service = MinIOService()

@celery_app.task(bind=True)
def process_weather_data_task(self, data_file: str) -> Dict[str, Any]:
    """Обработка метеорологических данных"""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Downloading weather data..."}
        )
        
        # Скачиваем данные из MinIO
        weather_data = minio_service.download_weather_data(data_file)
        
        if not weather_data:
            return {
                "status": "failed",
                "error": "Failed to download weather data"
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Processing weather data..."}
        )
        
        # Обрабатываем данные
        processed_records = 0
        total_records = len(weather_data.get("records", []))
        
        for i, record in enumerate(weather_data.get("records", [])):
            # Обрабатываем каждую запись
            processed_record = process_weather_record(record)
            
            # TODO: Сохранить в БД
            # db_service.save_weather_data(processed_record)
            
            processed_records += 1
            
            # Обновляем прогресс
            progress = 30 + int((i / total_records) * 60)
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "status": f"Processing record {i+1}/{total_records}"
                }
            )
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Saving results..."}
        )
        
        # Сохраняем результаты обработки
        result_data = {
            "file": data_file,
            "processed_records": processed_records,
            "total_records": total_records,
            "processing_date": datetime.now().isoformat()
        }
        
        minio_service.upload_json(f"processed_weather/{data_file}_result.json", result_data)
        
        return {
            "status": "completed",
            "processed_records": processed_records,
            "total_records": total_records,
            "result_file": f"processed_weather/{data_file}_result.json"
        }
        
    except Exception as e:
        logger.error(f"Error in weather data processing task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

@celery_app.task(bind=True)
def process_fire_data_task(self, data_file: str) -> Dict[str, Any]:
    """Обработка данных о пожарах"""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Downloading fire data..."}
        )
        
        # Скачиваем данные из MinIO
        fire_data = minio_service.download_json(f"fire_data/{data_file}")
        
        if not fire_data:
            return {
                "status": "failed",
                "error": "Failed to download fire data"
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Processing fire data..."}
        )
        
        # Обрабатываем данные
        processed_records = 0
        total_records = len(fire_data.get("records", []))
        
        for i, record in enumerate(fire_data.get("records", [])):
            # Обрабатываем каждую запись
            processed_record = process_fire_record(record)
            
            # TODO: Сохранить в БД
            # db_service.save_fire_data(processed_record)
            
            processed_records += 1
            
            # Обновляем прогресс
            progress = 30 + int((i / total_records) * 60)
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "status": f"Processing record {i+1}/{total_records}"
                }
            )
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Saving results..."}
        )
        
        # Сохраняем результаты обработки
        result_data = {
            "file": data_file,
            "processed_records": processed_records,
            "total_records": total_records,
            "processing_date": datetime.now().isoformat()
        }
        
        minio_service.upload_json(f"processed_fire/{data_file}_result.json", result_data)
        
        return {
            "status": "completed",
            "processed_records": processed_records,
            "total_records": total_records,
            "result_file": f"processed_fire/{data_file}_result.json"
        }
        
    except Exception as e:
        logger.error(f"Error in fire data processing task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

def process_weather_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка одной записи метеоданных"""
    # Нормализация координат до сетки 0.5°
    lat = round(record.get("latitude", 0) * 2) / 2
    lon = round(record.get("longitude", 0) * 2) / 2
    
    return {
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "timestamp": record.get("timestamp"),
        "temperature": record.get("temperature_2m"),
        "humidity": record.get("relative_humidity"),
        "wind_u": record.get("wind_u"),
        "wind_v": record.get("wind_v"),
        "precipitation": record.get("precipitation"),
        "lat_cell": lat,
        "lon_cell": lon,
        "processed": True
    }

def process_fire_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка одной записи о пожаре"""
    # Нормализация координат до сетки 0.5°
    lat = round(record.get("latitude", 0) * 2) / 2
    lon = round(record.get("longitude", 0) * 2) / 2
    
    # Извлечение временных признаков
    dt = record.get("dt")
    if dt:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        year = dt.year
        month = dt.month
        weekday = dt.weekday()
    else:
        year = month = weekday = 0
    
    return {
        "dt": record.get("dt"),
        "type_name": record.get("type_name"),
        "type_id": record.get("type_id"),
        "latitude": record.get("latitude"),
        "longitude": record.get("longitude"),
        "year": year,
        "month": month,
        "weekday": weekday,
        "lat_cell": lat,
        "lon_cell": lon,
        "processed": True
    } 