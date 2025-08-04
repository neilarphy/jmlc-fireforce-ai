"""
Database сервис для работы с базой данных.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..core.database import get_db
from ..models import (
    RawFireData, ProcessedFireData, HistoricalFire,
    RawWeatherData, ProcessedWeatherData,
    FirePrediction, PredictionRequest, User,
    SystemHealth, ErrorLog
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """Сервис для работы с базой данных"""
    
    def __init__(self):
        pass
    
    def test_connection(self) -> Dict[str, Any]:
        """Проверка подключения к базе данных"""
        try:
            db = next(get_db())
            # Простой запрос для проверки
            result = db.execute(func.text("SELECT 1")).scalar()
            db.close()
            
            return {
                "status": "healthy",
                "message": "База данных доступна",
                "test_query": result
            }
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return {
                "status": "critical",
                "message": f"Ошибка подключения: {str(e)}",
                "error": str(e)
            }
    
    def get_table_names(self) -> List[str]:
        """Получение списка таблиц"""
        try:
            db = next(get_db())
            # Получаем список таблиц
            tables = db.execute(func.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            table_names = [row[0] for row in tables]
            db.close()
            return table_names
        except Exception as e:
            logger.error(f"Ошибка получения списка таблиц: {e}")
            return []
    
    def get_fire_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение данных о пожарах"""
        try:
            db = next(get_db())
            fires = db.query(RawFireData).order_by(desc(RawFireData.dt)).offset(offset).limit(limit).all()
            
            result = []
            for fire in fires:
                result.append({
                    "id": fire.id,
                    "dt": fire.dt,
                    "latitude": fire.latitude,
                    "longitude": fire.longitude,
                    "type_name": fire.type_name,
                    "type_id": fire.type_id,
                    "created_at": fire.created_at
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения данных о пожарах: {e}")
            return []
    
    def get_predictions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение предсказаний"""
        try:
            db = next(get_db())
            predictions = db.query(FirePrediction).order_by(desc(FirePrediction.prediction_date)).offset(offset).limit(limit).all()
            
            result = []
            for pred in predictions:
                result.append({
                    "id": pred.id,
                    "latitude": pred.latitude,
                    "longitude": pred.longitude,
                    "prediction_date": pred.prediction_date,
                    "risk_score": pred.risk_score,
                    "probability": pred.probability,
                    "risk_level": pred.risk_level,
                    "model_version": pred.model_version,
                    "created_at": pred.created_at
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения предсказаний: {e}")
            return []
    
    def save_prediction(self, prediction_data: Dict[str, Any]) -> Optional[int]:
        """Сохранение предсказания"""
        try:
            db = next(get_db())
            prediction = FirePrediction(**prediction_data)
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            prediction_id = prediction.id
            db.close()
            return prediction_id
        except Exception as e:
            logger.error(f"Ошибка сохранения предсказания: {e}")
            return None
    
    def get_weather_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение метеоданных"""
        try:
            db = next(get_db())
            weather = db.query(RawWeatherData).order_by(desc(RawWeatherData.timestamp)).offset(offset).limit(limit).all()
            
            result = []
            for w in weather:
                result.append({
                    "id": w.id,
                    "timestamp": w.timestamp,
                    "latitude": w.latitude,
                    "longitude": w.longitude,
                    "temperature_2m": w.temperature_2m,
                    "relative_humidity": w.relative_humidity,
                    "wind_u": w.wind_u,
                    "wind_v": w.wind_v,
                    "precipitation": w.precipitation,
                    "created_at": w.created_at
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения метеоданных: {e}")
            return []
    
    def get_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение пользователей"""
        try:
            db = next(get_db())
            users = db.query(User).offset(offset).limit(limit).all()
            
            result = []
            for user in users:
                result.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        try:
            db = next(get_db())
            
            # Подсчет пожаров
            total_fires = db.query(func.count(RawFireData.id)).scalar()
            
            # Подсчет предсказаний
            total_predictions = db.query(func.count(FirePrediction.id)).scalar()
            
            # Подсчет пользователей
            total_users = db.query(func.count(User.id)).scalar()
            
            # Последние обновления
            last_fire = db.query(RawFireData.dt).order_by(desc(RawFireData.dt)).first()
            last_prediction = db.query(FirePrediction.prediction_date).order_by(desc(FirePrediction.prediction_date)).first()
            
            db.close()
            
            return {
                "total_fires": total_fires or 0,
                "total_predictions": total_predictions or 0,
                "total_users": total_users or 0,
                "last_fire_date": last_fire[0] if last_fire else None,
                "last_prediction_date": last_prediction[0] if last_prediction else None,
                "last_updated": datetime.now()
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {
                "total_fires": 0,
                "total_predictions": 0,
                "total_users": 0,
                "last_fire_date": None,
                "last_prediction_date": None,
                "last_updated": datetime.now()
            }
    
    def get_recent_fires(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение недавних пожаров"""
        try:
            db = next(get_db())
            cutoff_date = datetime.now() - timedelta(days=days)
            
            fires = db.query(RawFireData).filter(
                RawFireData.dt >= cutoff_date
            ).order_by(desc(RawFireData.dt)).limit(limit).all()
            
            result = []
            for fire in fires:
                result.append({
                    "id": fire.id,
                    "dt": fire.dt,
                    "latitude": fire.latitude,
                    "longitude": fire.longitude,
                    "type_name": fire.type_name,
                    "created_at": fire.created_at
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения недавних пожаров: {e}")
            return []
    
    def get_high_risk_predictions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение предсказаний высокого риска"""
        try:
            db = next(get_db())
            predictions = db.query(FirePrediction).filter(
                FirePrediction.risk_level.in_(["high", "extreme"])
            ).order_by(desc(FirePrediction.risk_score)).limit(limit).all()
            
            result = []
            for pred in predictions:
                result.append({
                    "id": pred.id,
                    "latitude": pred.latitude,
                    "longitude": pred.longitude,
                    "prediction_date": pred.prediction_date,
                    "risk_score": pred.risk_score,
                    "probability": pred.probability,
                    "risk_level": pred.risk_level,
                    "model_version": pred.model_version,
                    "created_at": pred.created_at
                })
            
            db.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения предсказаний высокого риска: {e}")
            return [] 