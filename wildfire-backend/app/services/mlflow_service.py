"""
MLflow сервис для работы с моделями.
"""
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class MLflowService:
    """Сервис для работы с MLflow"""
    
    def __init__(self):
        self.tracking_uri = settings.MLFLOW_TRACKING_URI
        self.model_name = settings.MLFLOW_MODEL_NAME
        self.experiment_name = settings.MLFLOW_EXPERIMENT_NAME
        mlflow.set_tracking_uri(self.tracking_uri)
        
    def test_connection(self) -> Dict[str, any]:
        """Проверка подключения к MLflow"""
        try:
            # Проверяем доступность MLflow
            experiments = mlflow.search_experiments()
            return {
                "status": "healthy",
                "message": "MLflow доступен",
                "experiments_count": len(experiments)
            }
        except Exception as e:
            logger.error(f"Ошибка подключения к MLflow: {e}")
            return {
                "status": "critical",
                "message": f"Ошибка подключения: {str(e)}",
                "error": str(e)
            }
    
    def get_latest_model(self) -> Optional[mlflow.pyfunc.PyFuncModel]:
        """Получение последней версии модели"""
        try:
            model_uri = f"models:/{self.model_name}/latest"
            model = mlflow.pyfunc.load_model(model_uri)
            return model
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, any]:
        """Получение информации о модели"""
        try:
            client = mlflow.tracking.MlflowClient()
            latest_version = client.get_latest_versions(self.model_name, stages=["Production"])
            
            if not latest_version:
                return {"error": "Модель не найдена"}
            
            model_info = latest_version[0]
            return {
                "model_name": model_info.name,
                "version": model_info.version,
                "run_id": model_info.run_id,
                "status": model_info.status,
                "created_at": model_info.creation_timestamp
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о модели: {e}")
            return {"error": str(e)}
    
    def predict(self, features: Dict[str, float]) -> Dict[str, any]:
        """Предсказание для одной точки"""
        try:
            model = self.get_latest_model()
            if not model:
                return {"error": "Модель недоступна"}
            
            # Подготовка данных
            input_data = pd.DataFrame([features])
            prediction = model.predict(input_data)
            
            # Обработка результата
            risk_score = float(prediction[0])
            probability = self._sigmoid(risk_score)
            risk_level = self._get_risk_level(probability)
            
            return {
                "risk_score": risk_score,
                "probability": probability,
                "risk_level": risk_level,
                "confidence": self._calculate_confidence(probability),
                "model_version": self._get_model_version()
            }
        except Exception as e:
            logger.error(f"Ошибка предсказания: {e}")
            return {"error": str(e)}
    
    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[Dict[str, any]]:
        """Пакетное предсказание"""
        try:
            model = self.get_latest_model()
            if not model:
                return [{"error": "Модель недоступна"} for _ in features_list]
            
            # Подготовка данных
            input_data = pd.DataFrame(features_list)
            predictions = model.predict(input_data)
            
            results = []
            for i, pred in enumerate(predictions):
                risk_score = float(pred)
                probability = self._sigmoid(risk_score)
                risk_level = self._get_risk_level(probability)
                
                results.append({
                    "risk_score": risk_score,
                    "probability": probability,
                    "risk_level": risk_level,
                    "confidence": self._calculate_confidence(probability),
                    "model_version": self._get_model_version()
                })
            
            return results
        except Exception as e:
            logger.error(f"Ошибка пакетного предсказания: {e}")
            return [{"error": str(e)} for _ in features_list]
    
    def get_available_models(self) -> List[Dict[str, any]]:
        """Получение списка доступных моделей"""
        try:
            client = mlflow.tracking.MlflowClient()
            models = client.search_model_versions(f"name='{self.model_name}'")
            
            return [
                {
                    "name": model.name,
                    "version": model.version,
                    "status": model.status,
                    "run_id": model.run_id,
                    "created_at": model.creation_timestamp
                }
                for model in models
            ]
        except Exception as e:
            logger.error(f"Ошибка получения списка моделей: {e}")
            return []
    
    def _sigmoid(self, x: float) -> float:
        """Сигмоидная функция для преобразования в вероятность"""
        return 1 / (1 + np.exp(-x))
    
    def _get_risk_level(self, probability: float) -> str:
        """Определение уровня риска по вероятности"""
        if probability < 0.25:
            return "low"
        elif probability < 0.5:
            return "medium"
        elif probability < 0.75:
            return "high"
        else:
            return "extreme"
    
    def _calculate_confidence(self, probability: float) -> float:
        """Расчет уверенности предсказания"""
        # Простая эвристика: чем дальше от 0.5, тем выше уверенность
        return abs(probability - 0.5) * 2
    
    def _get_model_version(self) -> str:
        """Получение версии модели"""
        try:
            model_info = self.get_model_info()
            return f"{model_info.get('model_name', 'unknown')}-v{model_info.get('version', 'unknown')}"
        except:
            return "unknown" 