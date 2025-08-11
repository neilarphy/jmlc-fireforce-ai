#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки модели
"""
from app.services.ml_service import MLService

def test_model():
    """Тестирование модели"""
    print("Testing ML model...")
    
    # Создаем ML сервис
    ml = MLService()
    
    print(f"Model loaded: {ml.model is not None}")
    if ml.model is not None:
        print(f"Model type: {type(ml.model).__name__}")
        print(f"Expected features: {len(ml.feature_names)}")
        print(f"Feature names: {ml.feature_names}")
    
    # Тестовые данные
    test_data = {
        'latitude': 55.7558,
        'longitude': 60.6173,
        'temperature': 20.0,
        'humidity': 60.0,
        'wind_u': 0.0,
        'wind_v': 0.0,
        'precipitation': 0.0
    }
    
    print(f"\nTest data: {test_data}")
    
    # Подготавливаем признаки
    features = ml.prepare_features(test_data)
    print(f"Features shape: {features.shape}")
    print(f"Features: {features[0]}")
    
    # Делаем предсказание
    try:
        risk, confidence = ml.predict_with_model(features)
        print(f"Prediction: risk={risk:.3f}, confidence={confidence:.3f}")
    except Exception as e:
        print(f"Prediction error: {e}")

if __name__ == "__main__":
    test_model() 