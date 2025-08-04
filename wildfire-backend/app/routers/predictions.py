"""
Prediction endpoints.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List
import uuid
import asyncio
from datetime import datetime
import random
import time
from sqlalchemy.orm import Session
from ..schemas.predictions import (
    PredictionRequest, 
    PredictionResult, 
    PredictionStatus, 
    PredictionHistory,
    PredictionStats,
    RiskLevel
)
from ..services.weather_service import WeatherService
from ..services.ml_service import MLService
from ..core.database import get_db
from ..models.prediction import FirePrediction
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

# Инициализация сервисов
weather_service = WeatherService()
ml_service = MLService()

# Кэш для активных задач (в памяти)
predictions_db = {}

# Добавляем счетчики для мониторинга ERA5
era5_stats = {
    "request_count": 0,
    "success_count": 0,
    "failure_count": 0,
    "total_duration": 0.0
}

def update_era5_stats(success: bool, duration: float = 0.0):
    """Обновить статистику ERA5 запросов"""
    era5_stats["request_count"] += 1
    if success:
        era5_stats["success_count"] += 1
        era5_stats["total_duration"] += duration
    else:
        era5_stats["failure_count"] += 1

async def process_prediction(prediction_id: str, request: PredictionRequest, db: Session):
    """Фоновая задача для обработки прогноза"""
    print(f"DEBUG: Starting prediction for {prediction_id}")
    print(f"DEBUG: Coordinates: {request.latitude}, {request.longitude}")
    
    try:
        logger.info(f"Starting prediction for {prediction_id}")
        logger.info(f"Coordinates: {request.latitude}, {request.longitude}")
        
        # Имитируем время обработки ML модели
        await asyncio.sleep(random.uniform(2, 5))
        
        # Получаем погодные данные
        print(f"DEBUG: Getting weather data for {request.latitude}, {request.longitude}")
        logger.info(f"Getting weather data for {request.latitude}, {request.longitude}")
        weather_data = weather_service.get_weather_features(
            request.latitude, 
            request.longitude
        )
        
        print(f"DEBUG: Weather data source: {weather_data.get('data_source', 'unknown')}")
        logger.info(f"Weather data source: {weather_data.get('data_source', 'unknown')}")
        logger.info(f"Current temperature: {weather_data.get('current_temperature', 'N/A')}°C")
        logger.info(f"Current humidity: {weather_data.get('current_humidity', 'N/A')}%")
        
        # Выполняем прогноз с помощью ML модели
        logger.info(f"Running ML prediction...")
        prediction_result = ml_service.predict_fire_risk(weather_data)
        
        logger.info(f"Prediction result: {prediction_result.get('risk_level', 'N/A')} ({prediction_result.get('risk_percentage', 0)}%)")
        
        # Создаем результат прогноза
        result = PredictionResult(
            id=str(uuid.uuid4()),
            latitude=request.latitude,
            longitude=request.longitude,
            risk_level=RiskLevel(prediction_result["risk_level"]),
            risk_percentage=prediction_result["risk_percentage"],
            confidence=prediction_result["confidence"],
            factors=prediction_result["factors"],
            recommendations=prediction_result["recommendations"],
            created_at=datetime.now(),
            status="completed"
        )
        
        # Сохраняем в базу данных
        db_prediction = FirePrediction(
            latitude=request.latitude,
            longitude=request.longitude,
            prediction_date=datetime.now(),
            risk_score=prediction_result["risk_percentage"] / 100.0,  # Конвертируем в 0-1
            probability=prediction_result["risk_probability"],
            risk_level=prediction_result["risk_level"],
            model_version="1.0.0",
            model_name="wildfire_prediction",
            prediction_type="single",
            confidence=prediction_result["confidence"] / 100.0  # Конвертируем в 0-1
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        # Обновляем результат с ID из базы
        result.id = str(db_prediction.id)
        
        # Сохраняем результат в кэш
        predictions_db[prediction_id] = PredictionStatus(
            id=prediction_id,
            status="completed",
            progress=100,
            estimated_time=0,
            result=result
        )
        
        print(f"DEBUG: Prediction {prediction_id} completed successfully")
        logger.info(f"Prediction {prediction_id} completed successfully")
        
    except Exception as e:
        print(f"DEBUG: Error in prediction {prediction_id}: {str(e)}")
        logger.error(f"Error in prediction {prediction_id}: {str(e)}")
        predictions_db[prediction_id] = PredictionStatus(
            id=prediction_id,
            status="failed",
            progress=0,
            estimated_time=0
        )

@router.post("/request", response_model=PredictionStatus)
async def create_prediction(request: PredictionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Создать новый прогноз"""
    prediction_id = str(uuid.uuid4())
    
    # Создаем задачу в статусе "pending"
    predictions_db[prediction_id] = PredictionStatus(
        id=prediction_id,
        status="pending",
        progress=0,
        estimated_time=30
    )
    
    # Запускаем фоновую обработку
    background_tasks.add_task(process_prediction, prediction_id, request, db)
    
    return predictions_db[prediction_id]

@router.get("/status/{prediction_id}", response_model=PredictionStatus)
async def get_prediction_status(prediction_id: str):
    """Получить статус прогноза"""
    if prediction_id not in predictions_db:
        raise HTTPException(status_code=404, detail="Прогноз не найден")
    
    return predictions_db[prediction_id]

@router.get("/history", response_model=List[PredictionHistory])
async def get_prediction_history(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Получить историю прогнозов из базы данных"""
    predictions = db.query(FirePrediction).order_by(FirePrediction.prediction_date.desc()).offset(offset).limit(limit).all()
    
    history = []
    for pred in predictions:
        history_item = PredictionHistory(
            id=str(pred.id),
            latitude=pred.latitude,
            longitude=pred.longitude,
            risk_level=RiskLevel(pred.risk_level),
            risk_percentage=pred.risk_score * 100,  # Конвертируем обратно в проценты
            confidence=pred.confidence * 100,  # Конвертируем обратно в проценты
            created_at=pred.prediction_date,
            region=None
        )
        history.append(history_item)
    
    return history

@router.get("/stats", response_model=PredictionStats)
async def get_prediction_stats(db: Session = Depends(get_db)):
    """Получить статистику прогнозов из базы данных"""
    total_predictions = db.query(FirePrediction).count()
    
    if total_predictions == 0:
        return PredictionStats(
            total_predictions=0,
            average_risk=0,
            high_risk_count=0,
            critical_risk_count=0,
            recent_predictions=[]
        )
    
    # Вычисляем средний риск
    avg_risk = db.query(FirePrediction.risk_score).all()
    average_risk = sum([r[0] for r in avg_risk]) / len(avg_risk) * 100
    
    # Подсчитываем высокий и критический риск
    high_risk_count = db.query(FirePrediction).filter(FirePrediction.risk_level.in_(['high', 'critical'])).count()
    critical_risk_count = db.query(FirePrediction).filter(FirePrediction.risk_level == 'critical').count()
    
    # Получаем последние прогнозы
    recent_predictions = db.query(FirePrediction).order_by(FirePrediction.prediction_date.desc()).limit(10).all()
    
    recent_history = []
    for pred in recent_predictions:
        history_item = PredictionHistory(
            id=str(pred.id),
            latitude=pred.latitude,
            longitude=pred.longitude,
            risk_level=RiskLevel(pred.risk_level),
            risk_percentage=pred.risk_score * 100,
            confidence=pred.confidence * 100,
            created_at=pred.prediction_date,
            region=None
        )
        recent_history.append(history_item)
    
    return PredictionStats(
        total_predictions=total_predictions,
        average_risk=round(average_risk, 1),
        high_risk_count=high_risk_count,
        critical_risk_count=critical_risk_count,
        recent_predictions=recent_history
    )

@router.delete("/{prediction_id}")
async def delete_prediction(prediction_id: str, db: Session = Depends(get_db)):
    """Удалить прогноз"""
    # Удаляем из кэша
    if prediction_id in predictions_db:
        del predictions_db[prediction_id]
    
    # Удаляем из базы данных
    prediction = db.query(FirePrediction).filter(FirePrediction.id == prediction_id).first()
    if prediction:
        db.delete(prediction)
        db.commit()
        return {"message": f"Прогноз {prediction_id} удален"}
    else:
        raise HTTPException(status_code=404, detail="Прогноз не найден") 

@router.get("/era5-stats")
async def get_era5_stats():
    """Получить статистику запросов к ERA5 API"""
    total_requests = era5_stats["request_count"]
    successful_requests = era5_stats["success_count"]
    failed_requests = era5_stats["failure_count"]
    total_duration = era5_stats["total_duration"]
    
    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        "average_duration": (total_duration / successful_requests) if successful_requests > 0 else 0,
        "api_available": weather_service.cds_client is not None
    } 