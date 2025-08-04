"""
ML сервис для прогнозирования пожаров
"""
import numpy as np
import joblib
import logging
from typing import Dict, List, Tuple
from datetime import datetime
import os
from .model_storage_service import ModelStorageService

logger = logging.getLogger(__name__)

class MLService:
    """Сервис для ML прогнозирования пожаров"""
    
    def __init__(self):
        self.model_storage = ModelStorageService()
        self.model = None
        self.feature_names = [
            "latitude", "longitude", "current_temperature", "current_humidity",
            "current_wind_speed", "current_precipitation", "avg_temperature_7d",
            "avg_humidity_7d", "avg_wind_speed_7d", "total_precipitation_7d",
            "temperature_trend", "humidity_trend"
        ]
        self.load_model()
    
    def load_model(self):
        """Загрузить ML модель"""
        try:
            # Пытаемся загрузить модель из хранилища
            self.model = self.model_storage.load_model()
            
            if self.model is None:
                # Если модель не найдена, создаем демо модель
                logger.info("No model found, creating demo model...")
                self.model_storage.create_demo_model()
                self.model = self.model_storage.load_model()
            
            if self.model is not None:
                logger.info("ML model loaded successfully")
            else:
                logger.warning("Failed to load model, using fallback logic")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def prepare_features(self, weather_data: Dict) -> np.ndarray:
        """Подготовить признаки для модели"""
        try:
            features = []
            for feature_name in self.feature_names:
                if feature_name in weather_data:
                    features.append(weather_data[feature_name])
                else:
                    # Дефолтные значения если признак отсутствует
                    if feature_name in ["latitude", "longitude"]:
                        features.append(0.0)
                    elif "temperature" in feature_name:
                        features.append(20.0)
                    elif "humidity" in feature_name:
                        features.append(60.0)
                    elif "wind" in feature_name:
                        features.append(5.0)
                    elif "precipitation" in feature_name:
                        features.append(0.0)
                    elif "trend" in feature_name:
                        features.append(0.0)
                    else:
                        features.append(0.0)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            # Возвращаем дефолтные признаки
            return np.array([0.0] * len(self.feature_names)).reshape(1, -1)
    
    def predict_with_model(self, features: np.ndarray) -> Tuple[float, float]:
        """Предсказание с использованием ML модели"""
        try:
            if self.model is not None:
                print(f"DEBUG: Using real ML model")
                print(f"DEBUG: Input features shape: {features.shape}")
                print(f"DEBUG: Input features: {features[0]}")
                
                # Получаем предсказание от модели
                prediction = self.model.predict_proba(features)[0]
                print(f"DEBUG: Raw prediction probabilities: {prediction}")
                
                risk_probability = prediction[1]  # Вероятность пожара
                
                # Вычисляем confidence на основе качества предсказания
                # Используем расстояние до границы решения как меру уверенности
                confidence = abs(risk_probability - 0.5) * 2  # Нормализуем к 0-1
                
                # Добавляем базовую уверенность и вариацию
                confidence = 0.6 + confidence * 0.3  # 0.6 - 0.9
                
                # Ограничиваем confidence от 0.5 до 1.0
                confidence = max(0.5, min(1.0, confidence))
                
                print(f"DEBUG: Calculated risk: {risk_probability:.3f}")
                print(f"DEBUG: Calculated confidence: {confidence:.3f}")
                
                logger.info(f"Model prediction: risk={risk_probability:.3f}, confidence={confidence:.3f}")
                
                return risk_probability, confidence
            else:
                print(f"DEBUG: Model is None, using fallback")
                # Fallback логика если модель не загружена
                return self.fallback_prediction(features)
                
        except Exception as e:
            logger.error(f"Error in model prediction: {e}")
            print(f"DEBUG: Model prediction error: {e}")
            return self.fallback_prediction(features)
    
    def fallback_prediction(self, features: np.ndarray) -> Tuple[float, float]:
        """Fallback логика для предсказания"""
        try:
            # Извлекаем признаки
            lat = features[0, 0]
            lon = features[0, 1]
            temp = features[0, 2]
            humidity = features[0, 3]
            wind_speed = features[0, 4]
            precipitation = features[0, 5]
            
            # Простая логика на основе правил
            risk_score = 0.3  # Базовый риск
            
            # Увеличиваем риск при высокой температуре
            if temp > 25:
                risk_score += 0.2
            elif temp > 30:
                risk_score += 0.3
            
            # Увеличиваем риск при низкой влажности
            if humidity < 40:
                risk_score += 0.2
            elif humidity < 30:
                risk_score += 0.3
            
            # Увеличиваем риск при сильном ветре
            if wind_speed > 10:
                risk_score += 0.15
            elif wind_speed > 15:
                risk_score += 0.25
            
            # Уменьшаем риск при осадках
            if precipitation > 5:
                risk_score -= 0.2
            
            # Региональные особенности
            if 50 <= lat <= 60 and 90 <= lon <= 110:  # Сибирь
                risk_score += 0.2
            elif 55 <= lat <= 60 and 30 <= lon <= 40:  # Северо-Запад
                risk_score += 0.1
            elif 40 <= lat <= 50 and 130 <= lon <= 140:  # Дальний Восток
                risk_score += 0.15
            
            # Ограничиваем риск от 0 до 1
            risk_score = max(0.0, min(1.0, risk_score))
            
            # Вычисляем confidence на основе качества входных данных
            # Чем больше данных у нас есть, тем выше confidence
            data_quality = 0.0
            data_points = 0
            
            # Проверяем качество каждого признака
            if temp != 0.0:  # Дефолтное значение
                data_quality += 1
                data_points += 1
            if humidity != 60.0:  # Дефолтное значение
                data_quality += 1
                data_points += 1
            if wind_speed != 5.0:  # Дефолтное значение
                data_quality += 1
                data_points += 1
            if precipitation != 0.0:  # Дефолтное значение
                data_quality += 1
                data_points += 1
            
            # Вычисляем confidence на основе качества данных
            if data_points > 0:
                confidence = 0.5 + (data_quality / data_points) * 0.3  # 0.5 - 0.8
            else:
                confidence = 0.5  # Минимальная уверенность
            
            # Добавляем вариацию на основе extremity risk_score
            # Чем ближе к 0 или 1, тем выше уверенность
            extremity_factor = abs(risk_score - 0.5) * 2  # 0-1
            confidence = confidence + extremity_factor * 0.2  # Добавляем до 0.2
            
            # Ограничиваем confidence от 0.5 до 0.9
            confidence = max(0.5, min(0.9, confidence))
            
            logger.info(f"Fallback prediction: risk={risk_score:.3f}, confidence={confidence:.3f}")
            
            return risk_score, confidence
            
        except Exception as e:
            logger.error(f"Error in fallback prediction: {e}")
            return 0.5, 0.5
    
    def get_risk_level(self, risk_probability: float) -> str:
        """Определить уровень риска"""
        if risk_probability < 0.25:
            return "low"
        elif risk_probability < 0.5:
            return "medium"
        elif risk_probability < 0.75:
            return "high"
        else:
            return "critical"
    
    def get_risk_factors(self, weather_data: Dict, risk_probability: float) -> List[str]:
        """Получить факторы риска"""
        factors = []
        
        temp = weather_data.get("current_temperature", 20)
        humidity = weather_data.get("current_humidity", 60)
        wind_speed = weather_data.get("current_wind_speed", 5)
        precipitation = weather_data.get("current_precipitation", 0)
        
        if temp > 25:
            factors.append("Высокая температура воздуха")
        if humidity < 40:
            factors.append("Низкая влажность")
        if wind_speed > 10:
            factors.append("Сильный ветер")
        if precipitation < 1:
            factors.append("Отсутствие осадков")
        if risk_probability > 0.7:
            factors.append("Критическая пожарная опасность")
        
        return factors
    
    def get_recommendations(self, risk_level: str, risk_probability: float) -> List[str]:
        """Получить рекомендации"""
        recommendations = []
        
        if risk_level in ["high", "critical"]:
            recommendations.append("Усилить мониторинг территории")
            recommendations.append("Подготовить силы пожаротушения")
        
        if risk_level == "critical":
            recommendations.append("Ограничить доступ в лесные массивы")
            recommendations.append("Провести профилактические мероприятия")
            recommendations.append("Привести в готовность авиацию")
        
        if risk_probability > 0.8:
            recommendations.append("Объявить режим чрезвычайной ситуации")
        
        return recommendations
    
    def predict_fire_risk(self, weather_data: Dict) -> Dict:
        """Предсказание риска пожара на основе погодных данных"""
        try:
            # Подготавливаем признаки
            features = self.prepare_features(weather_data)
            
            # Получаем предсказание от модели
            risk_probability, confidence = self.predict_with_model(features)
            
            # Определяем уровень риска
            risk_level = self.get_risk_level(risk_probability)
            
            # Получаем факторы риска
            risk_factors = self.get_risk_factors(weather_data, risk_probability)
            
            # Получаем рекомендации
            recommendations = self.get_recommendations(risk_level, risk_probability)
            
            # Конвертируем вероятность в процент и округляем
            risk_percentage = round(risk_probability * 100, 1)
            
            # Конвертируем confidence в процент и округляем
            confidence_percentage = round(confidence * 100, 1)
            
            result = {
                "risk_level": risk_level,
                "risk_percentage": risk_percentage,
                "risk_probability": risk_probability,
                "confidence": confidence_percentage,
                "factors": risk_factors,
                "recommendations": recommendations,
                "weather_data_source": weather_data.get("data_source", "unknown"),
                "model_version": "1.0.0",
                "prediction_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Fire risk prediction completed: {risk_level} ({risk_percentage}%)")
            return result
            
        except Exception as e:
            logger.error(f"Error in fire risk prediction: {e}")
            # Возвращаем дефолтный результат в случае ошибки
            return {
                "risk_level": "low",
                "risk_percentage": 10.0,
                "risk_probability": 0.1,
                "confidence": 50.0,
                "factors": ["Insufficient data"],
                "recommendations": ["Monitor weather conditions"],
                "weather_data_source": "fallback",
                "model_version": "1.0.0",
                "prediction_timestamp": datetime.now().isoformat()
            } 