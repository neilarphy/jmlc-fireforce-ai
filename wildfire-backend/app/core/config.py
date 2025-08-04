"""
Конфигурация приложения.
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # База данных
    DATABASE_URL: str = "postgresql://wildfire_user:wildfire_pass@your-server.com:5432/wildfire_db"
    
    # Redis
    REDIS_URL: str = "redis://your-server.com:6379/0"
    
    # MLflow
    MLFLOW_TRACKING_URI: str = "http://your-server.com:5000"
    MLFLOW_MODEL_NAME: str = "wildfire-prediction"
    MLFLOW_MODEL_VERSION: str = "latest"
    MLFLOW_EXPERIMENT_NAME: str = "wildfire-prediction"
    
    # MinIO
    MINIO_ENDPOINT: str = "your-server.com:9000"
    MINIO_ACCESS_KEY: str = "your-access-key"
    MINIO_SECRET_KEY: str = "your-secret-key"
    MINIO_BUCKET: str = "wildfire-data"
    MINIO_SECURE: bool = True  # True для HTTPS
    
    # API настройки
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Wildfire Prediction System"
    VERSION: str = "1.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Разрешаем все origins для разработки
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ERA5 API
    ERA5_API_KEY: str = ""
    ERA5_API_URL: str = "https://cds.climate.copernicus.eu/api/v2"
    
    class Config:
        # Ищем .env файл в корне проекта (на 2 уровня выше от app/core/)
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = True
        protected_namespaces = ()  # Отключаем защищенные пространства имен
    
    @property
    def postgres_url(self) -> str:
        """URL для PostgreSQL"""
        return self.DATABASE_URL
    
    @property
    def redis_url(self) -> str:
        """URL для Redis"""
        return self.REDIS_URL
    
    def validate_mlflow_config(self) -> bool:
        """Проверка конфигурации MLflow"""
        return all([
            self.MLFLOW_TRACKING_URI,
            self.MLFLOW_MODEL_NAME,
            self.MLFLOW_EXPERIMENT_NAME
        ])
    
    def validate_minio_config(self) -> bool:
        """Проверка конфигурации MinIO"""
        return all([
            self.MINIO_ENDPOINT,
            self.MINIO_ACCESS_KEY,
            self.MINIO_SECRET_KEY,
            self.MINIO_BUCKET
        ])
    
    def get_service_status(self) -> dict:
        """Получение статуса сервисов"""
        return {
            "database": {
                "url": self.postgres_url,
                "configured": bool(self.postgres_url)
            },
            "redis": {
                "url": self.redis_url,
                "configured": bool(self.redis_url)
            },
            "mlflow": {
                "tracking_uri": self.MLFLOW_TRACKING_URI,
                "model_name": self.MLFLOW_MODEL_NAME,
                "configured": self.validate_mlflow_config()
            },
            "minio": {
                "endpoint": self.MINIO_ENDPOINT,
                "bucket": self.MINIO_BUCKET,
                "configured": self.validate_minio_config()
            }
        }

# Создаем экземпляр настроек
settings = Settings()

# Отладочная информация
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(f"DEBUG: Looking for .env file at: {env_file_path}")
print(f"DEBUG: .env file exists: {env_file_path.exists()}")
print(f"DEBUG: ERA5_API_KEY loaded: {'SET' if settings.ERA5_API_KEY else 'NOT SET'}")
print(f"DEBUG: ERA5_API_URL loaded: {settings.ERA5_API_URL}") 