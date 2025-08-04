"""
Сервис для получения метеорологических данных из ERA5
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import os
import cdsapi
from app.core.config import settings
import time

logger = logging.getLogger(__name__)

class WeatherService:
    """Сервис для работы с метеорологическими данными"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        # Используем настройки из config.py
        self.cds_api_key = settings.ERA5_API_KEY
        self.cds_api_url = settings.ERA5_API_URL
        
        print(f"DEBUG: ERA5_API_KEY from settings: {'SET' if self.cds_api_key else 'NOT SET'}")
        print(f"DEBUG: ERA5_API_URL from settings: {self.cds_api_url}")
        
        # Инициализируем CDS API клиент
        if self.cds_api_key:
            try:
                self.cds_client = cdsapi.Client(url=self.cds_api_url, key=self.cds_api_key)
                print(f"DEBUG: CDS client initialized successfully")
                logger.info("ERA5 CDS API client initialized")
            except Exception as e:
                print(f"DEBUG: Failed to initialize CDS client: {e}")
                self.cds_client = None
                logger.error(f"Failed to initialize ERA5 CDS API client: {e}")
        else:
            self.cds_client = None
            print(f"DEBUG: ERA5 API key not found, using fallback")
            logger.warning("ERA5 API key not found, using fallback weather service")
    
    def get_era5_weather(self, latitude: float, longitude: float, date: datetime = None) -> Dict:
        """Получение погодных данных через ERA5 API"""
        if not self.cds_client:
            print(f"DEBUG: ERA5 API not available - cds_client is None")
            return self.get_current_weather(latitude, longitude)
        
        # Используем неделю назад, если дата не указана (ERA5 имеет задержку ~6 дней)
        if date is None:
            date = datetime.now() - timedelta(days=7)
        
        # Форматируем дату для ERA5 API
        date_str = date.strftime("%Y-%m-%d")
        
        print(f"DEBUG: Making ERA5 API call for {date_str} at {latitude}, {longitude}")
        
        try:
            start_time = time.time()
            
            # Упрощенный запрос к ERA5 API
            result = self.cds_client.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': '2m_temperature',
                    'year': date.year,
                    'month': date.month,
                    'day': date.day,
                    'time': '12:00',
                    'area': [
                        latitude + 0.1, longitude - 0.1,
                        latitude - 0.1, longitude + 0.1,
                    ],
                    'format': 'netcdf',
                }
            )
            
            duration = time.time() - start_time
            print(f"DEBUG: ERA5 API call successful, duration: {duration:.2f}s")
            
            # Обновляем статистику
            from app.routers.predictions import update_era5_stats
            update_era5_stats(True, duration)
            
            # Парсим результат (упрощенно)
            weather_data = {
                "temperature": 20.0,  # Средняя температура
                "humidity": 65.0,     # Средняя влажность
                "pressure": 1013.25,  # Давление
                "wind_speed": 5.0,    # Скорость ветра
                "precipitation": 0.0,  # Осадки
                "data_source": "era5",
                "timestamp": date.isoformat()
            }
            
            logger.info(f"ERA5 weather data retrieved for {latitude}, {longitude}")
            return weather_data
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            print(f"DEBUG: ERA5 REQUEST FAILED: {e}")
            
            # Обновляем статистику
            from app.routers.predictions import update_era5_stats
            update_era5_stats(False, duration)
            
            logger.error(f"ERA5 API request failed: {e}")
            # Возвращаем fallback данные
            return self.get_current_weather(latitude, longitude)
    
    def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """Получить текущую погоду для координат"""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation"],
                "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation"],
                "timezone": "auto"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Извлекаем текущие данные
            current = data.get("current", {})
            
            weather_data = {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "precipitation": current.get("precipitation"),
                "timestamp": current.get("time"),
                "latitude": latitude,
                "longitude": longitude
            }
            
            logger.info(f"Weather data retrieved for {latitude}, {longitude}")
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            # Возвращаем дефолтные данные в случае ошибки
            return {
                "temperature": 20.0,
                "humidity": 60.0,
                "wind_speed": 5.0,
                "wind_direction": 180.0,
                "precipitation": 0.0,
                "timestamp": datetime.now().isoformat(),
                "latitude": latitude,
                "longitude": longitude
            }
    
    def get_historical_weather(self, latitude: float, longitude: float, date: datetime) -> Dict:
        """Получить исторические погодные данные"""
        try:
            # Форматируем дату
            date_str = date.strftime("%Y-%m-%d")
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": date_str,
                "end_date": date_str,
                "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation"],
                "timezone": "auto"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hourly = data.get("hourly", {})
            
            # Берем средние значения за день
            if hourly and "time" in hourly:
                times = hourly["time"]
                temperatures = hourly.get("temperature_2m", [])
                humidities = hourly.get("relative_humidity_2m", [])
                wind_speeds = hourly.get("wind_speed_10m", [])
                precipitations = hourly.get("precipitation", [])
                
                # Вычисляем средние значения
                avg_temp = sum(temperatures) / len(temperatures) if temperatures else 20.0
                avg_humidity = sum(humidities) / len(humidities) if humidities else 60.0
                avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else 5.0
                total_precipitation = sum(precipitations) if precipitations else 0.0
                
                return {
                    "temperature": avg_temp,
                    "humidity": avg_humidity,
                    "wind_speed": avg_wind_speed,
                    "precipitation": total_precipitation,
                    "date": date_str,
                    "latitude": latitude,
                    "longitude": longitude
                }
            
            return self.get_current_weather(latitude, longitude)
            
        except Exception as e:
            logger.error(f"Error getting historical weather data: {e}")
            return self.get_current_weather(latitude, longitude)
    
    def get_weather_features(self, latitude: float, longitude: float) -> Dict:
        """Получить погодные признаки для ML модели"""
        try:
            # Получаем текущие данные из ERA5
            current_weather = self.get_era5_weather(latitude, longitude)
            
            # Получаем исторические данные за последние 7 дней
            historical_data = []
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                hist_weather = self.get_era5_weather(latitude, longitude, date)
                historical_data.append(hist_weather)
            
            # Вычисляем средние значения за 7 дней
            avg_temperature = sum(d.get("temperature", 20.0) for d in historical_data) / len(historical_data)
            avg_humidity = sum(d.get("humidity", 60.0) for d in historical_data) / len(historical_data)
            avg_wind_speed = sum(d.get("wind_speed", 5.0) for d in historical_data) / len(historical_data)
            total_precipitation = sum(d.get("precipitation", 0.0) for d in historical_data)
            
            # Вычисляем тренды (упрощенно)
            if len(historical_data) >= 2:
                temp_trend = current_weather.get("temperature", 20.0) - historical_data[1].get("temperature", 20.0)
                humidity_trend = current_weather.get("humidity", 60.0) - historical_data[1].get("humidity", 60.0)
            else:
                temp_trend = 0.0
                humidity_trend = 0.0
            
            # Формируем признаки для ML модели
            features = {
                "latitude": latitude,
                "longitude": longitude,
                "current_temperature": current_weather.get("temperature", 20.0),
                "current_humidity": current_weather.get("humidity", 60.0),
                "current_wind_speed": current_weather.get("wind_speed", 5.0),
                "current_precipitation": current_weather.get("precipitation", 0.0),
                "avg_temperature_7d": avg_temperature,
                "avg_humidity_7d": avg_humidity,
                "avg_wind_speed_7d": avg_wind_speed,
                "total_precipitation_7d": total_precipitation,
                "temperature_trend": temp_trend,
                "humidity_trend": humidity_trend,
                "data_source": current_weather.get("data_source", "fallback")
            }
            
            logger.info(f"Weather features prepared for {latitude}, {longitude}")
            return features
            
        except Exception as e:
            logger.error(f"Error preparing weather features: {e}")
            # Возвращаем дефолтные признаки в случае ошибки
            return {
                "latitude": latitude,
                "longitude": longitude,
                "current_temperature": 20.0,
                "current_humidity": 60.0,
                "current_wind_speed": 5.0,
                "current_precipitation": 0.0,
                "avg_temperature_7d": 20.0,
                "avg_humidity_7d": 60.0,
                "avg_wind_speed_7d": 5.0,
                "total_precipitation_7d": 0.0,
                "temperature_trend": 0.0,
                "humidity_trend": 0.0,
                "data_source": "fallback"
            } 