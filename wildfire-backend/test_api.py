#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API
"""
import requests
import json

def test_prediction_api():
    """Тестирование API предсказаний"""
    
    # URL API
    url = "http://localhost:8000/api/v1/predictions/request"
    
    # Тестовые данные
    data = {
        "latitude": 55.7558,
        "longitude": 60.6173,
        "prediction_type": "fire_risk"
    }
    
    print("Testing prediction API...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        # Отправляем запрос
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Prediction ID: {result.get('prediction_id')}")
            print(f"Status: {result.get('status')}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_prediction_api() 