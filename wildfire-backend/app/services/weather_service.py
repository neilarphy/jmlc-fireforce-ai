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
import numpy as np
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
        
        # Используем 8-10 дней назад, если дата не указана (ERA5 имеет задержку ~6-7 дней)
        if date is None:
            date = datetime.now() - timedelta(days=8)
        
        # Проверяем, что дата не слишком свежая (ERA5 имеет задержку)
        max_fresh_date = datetime.now() - timedelta(days=6)
        if date > max_fresh_date:
            date = max_fresh_date
            print(f"DEBUG: Adjusted date to {date.strftime('%Y-%m-%d')} due to ERA5 delay")
        
        # Форматируем дату для ERA5 API
        date_str = date.strftime("%Y-%m-%d")
        
        print(f"DEBUG: Making ERA5 API call for {date_str} at {latitude}, {longitude}")
        
        try:
            start_time = time.time()
            
            # Полный запрос к ERA5 API со всеми нужными переменными
            result = self.cds_client.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'variable': [
                        '2m_temperature',
                        '2m_relative_humidity', 
                        '10m_u_component_of_wind',
                        '10m_v_component_of_wind',
                        'total_precipitation'
                    ],
                    'year': date.year,
                    'month': date.month,
                    'day': date.day,
                    'time': [
                        '00:00', '06:00', '12:00', '18:00'
                    ],
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
            
            # В реальности нужно читать NetCDF файл и извлекать данные
            # Пока что возвращаем ошибку - пусть система использует Open-Meteo
            print(f"DEBUG: ERA5 data received with all variables, but parsing not implemented yet")
            print(f"DEBUG: NOTE: When implementing ERA5 parsing, remember to convert temperatures from Kelvin to Celsius")
            print(f"DEBUG: Example: temperature_celsius = temperature_kelvin - 273.15")
            logger.info(f"ERA5 weather data retrieved for {latitude}, {longitude}")
            raise Exception("ERA5 data received with all variables but parsing not implemented yet - using Open-Meteo fallback")
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            print(f"DEBUG: ERA5 REQUEST FAILED: {e}")
            
            # Обновляем статистику
            from app.routers.predictions import update_era5_stats
            update_era5_stats(False, duration)
            
            logger.error(f"ERA5 API request failed: {e}")
            
            # Если ошибка связана с недоступностью данных, пробуем более старую дату
            if "not available yet" in str(e) or "latest date available" in str(e):
                print(f"DEBUG: Trying older date due to data availability")
                older_date = date - timedelta(days=3)
                return self.get_era5_weather(latitude, longitude, older_date)
            
            # Не возвращаем fallback - пусть система покажет ошибку
            raise Exception(f"ERA5 API failed: {e}")
    
    def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """Получить текущую погоду для координат"""
        try:
            print(f"DEBUG: Making Open-Meteo API call for {latitude}, {longitude}")
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation"],
                "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "precipitation"],
                "timezone": "auto"
            }
            
            start_time = time.time()
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            duration = time.time() - start_time
            
            print(f"DEBUG: Open-Meteo API call successful, duration: {duration:.2f}s")
            
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
                "longitude": longitude,
                "data_source": "open_meteo"
            }
            
            logger.info(f"Open-Meteo weather data retrieved for {latitude}, {longitude}")
            print(f"DEBUG: Open-Meteo data: {weather_data}")
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting Open-Meteo weather data: {e}")
            print(f"DEBUG: Open-Meteo API failed: {e}")
            # Не возвращаем дефолтные данные - пусть система покажет ошибку
            raise Exception(f"Failed to get weather data from Open-Meteo: {e}")
    
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
            # Пробуем получить данные из ERA5 (8-10 дней назад)
            try:
                weather_data = self.get_era5_weather(latitude, longitude)
                print(f"DEBUG: ERA5 data received successfully")
            except Exception as era5_error:
                print(f"DEBUG: ERA5 failed, trying Open-Meteo: {era5_error}")
                # Если ERA5 недоступен, используем Open-Meteo
                weather_data = self.get_current_weather(latitude, longitude)
                
                # Конвертируем wind_speed в wind_u и wind_v
                wind_speed = weather_data.get("wind_speed", 5.0)
                wind_direction = weather_data.get("wind_direction", 180.0)
                wind_direction_rad = np.radians(wind_direction)
                wind_u = wind_speed * np.cos(wind_direction_rad)
                wind_v = wind_speed * np.sin(wind_direction_rad)
                
                weather_data["wind_u"] = wind_u
                weather_data["wind_v"] = wind_v
            
            # Формируем признаки для ML модели (соответствуют DAG)
            features = {
                "latitude": latitude,
                "longitude": longitude,
                "temperature": weather_data.get("temperature", 20.0),
                "humidity": weather_data.get("humidity", 60.0),
                "wind_u": weather_data.get("wind_u", 0.0),
                "wind_v": weather_data.get("wind_v", 0.0),
                "precipitation": weather_data.get("precipitation", 0.0),
                "data_source": weather_data.get("data_source", "open_meteo")
            }
            
            logger.info(f"Weather features prepared for {latitude}, {longitude}")
            return features
            
        except Exception as e:
            logger.error(f"Error preparing weather features: {e}")
            print(f"DEBUG: Weather features preparation failed: {e}")
            # Не возвращаем дефолтные признаки - пусть система покажет ошибку
            raise Exception(f"Failed to prepare weather features: {e}") 