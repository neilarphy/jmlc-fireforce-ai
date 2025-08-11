import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_service import MLService

# Создаем тестовые данные
weather_data = {
    'latitude': 55.0171,
    'longitude': 61.2276,
    'temperature': 20.0,
    'humidity': 65.0,
    'wind_u': 5.0,
    'wind_v': 0.0,
    'precipitation': 0.0
}

# Тестируем MLService
ml_service = MLService()

print("Feature names:")
print(ml_service.feature_names)
print(f"Total features: {len(ml_service.feature_names)}")

# Подготавливаем фичи
features = ml_service.prepare_features(weather_data)
print(f"\nPrepared features shape: {features.shape}")
print(f"Features: {features[0]}")

# Делаем предсказание
risk, confidence = ml_service.predict_with_model(features)
print(f"\nPrediction: risk={risk}, confidence={confidence}") 