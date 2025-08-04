"""
Celery tasks for predictions.
"""
from celery import current_task
from typing import Dict, Any, List
import logging

from ..core.celery_app import celery_app
from ..services.mlflow_service import MLflowService
from ..services.database_service import DatabaseService

logger = logging.getLogger(__name__)

mlflow_service = MLflowService()
db_service = DatabaseService()

@celery_app.task(bind=True)
def process_prediction_task(self, prediction_request: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка предсказания в фоне"""
    try:
        # Обновляем статус задачи
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Preparing features..."}
        )
        
        # Подготавливаем признаки
        features = prepare_features(prediction_request)
        
        self.update_state(
            state="PROGRESS", 
            meta={"current": 30, "total": 100, "status": "Making prediction..."}
        )
        
        # Получаем предсказание
        prediction_result = mlflow_service.predict(features)
        
        if "error" in prediction_result:
            return {
                "status": "failed",
                "error": prediction_result["error"]
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Saving result..."}
        )
        
        # Сохраняем в БД
        prediction_data = {
            "latitude": prediction_request["latitude"],
            "longitude": prediction_request["longitude"],
            "prediction_date": prediction_request.get("prediction_date"),
            "risk_score": prediction_result["risk_score"],
            "probability": prediction_result["probability"],
            "risk_level": prediction_result["risk_level"],
            "model_version": prediction_result["model_version"],
            "prediction_type": "background",
            "confidence": prediction_result["confidence"]
        }
        
        prediction_id = db_service.save_prediction(prediction_data)
        
        self.update_state(
            state="SUCCESS",
            meta={"current": 100, "total": 100, "status": "Completed"}
        )
        
        return {
            "status": "completed",
            "prediction_id": prediction_id,
            "result": prediction_result
        }
        
    except Exception as e:
        logger.error(f"Error in prediction task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

@celery_app.task(bind=True)
def process_batch_prediction_task(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка пакетного предсказания"""
    try:
        locations = batch_data["locations"]
        total_locations = len(locations)
        completed = 0
        results = []
        
        for i, location in enumerate(locations):
            # Обновляем прогресс
            progress = int((i / total_locations) * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "status": f"Processing location {i+1}/{total_locations}"
                }
            )
            
            # Подготавливаем признаки
            features = prepare_features(location)
            
            # Получаем предсказание
            prediction_result = mlflow_service.predict(features)
            
            if "error" not in prediction_result:
                # Сохраняем в БД
                prediction_data = {
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "prediction_date": location.get("prediction_date"),
                    "risk_score": prediction_result["risk_score"],
                    "probability": prediction_result["probability"],
                    "risk_level": prediction_result["risk_level"],
                    "model_version": prediction_result["model_version"],
                    "prediction_type": "batch",
                    "confidence": prediction_result["confidence"]
                }
                
                prediction_id = db_service.save_prediction(prediction_data)
                results.append({
                    "location": location,
                    "prediction": prediction_result,
                    "prediction_id": prediction_id
                })
                completed += 1
            else:
                results.append({
                    "location": location,
                    "error": prediction_result["error"]
                })
        
        return {
            "status": "completed",
            "total_locations": total_locations,
            "completed": completed,
            "failed": total_locations - completed,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch prediction task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

def prepare_features(prediction_request: Dict[str, Any]) -> Dict[str, float]:
    """Подготовка признаков для модели"""
    from datetime import datetime
    
    # Базовые признаки из запроса
    features = {
        "latitude": prediction_request["latitude"],
        "longitude": prediction_request["longitude"],
    }
    
    # Добавляем временные признаки
    prediction_date = prediction_request.get("prediction_date")
    if not prediction_date:
        prediction_date = datetime.now()
    
    features.update({
        "year": prediction_date.year,
        "month": prediction_date.month,
        "weekday": prediction_date.weekday(),
    })
    
    # TODO: Добавить метеопризнаки из БД или внешнего API
    # Пока используем заглушки
    features.update({
        "temperature": 20.0,  # TODO: получить из БД
        "humidity": 60.0,     # TODO: получить из БД
        "wind_u": 2.0,       # TODO: получить из БД
        "wind_v": 1.0,       # TODO: получить из БД
        "precipitation": 0.0  # TODO: получить из БД
    })
    
    return features 