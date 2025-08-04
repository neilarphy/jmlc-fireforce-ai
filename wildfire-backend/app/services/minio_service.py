"""
MinIO сервис для работы с объектным хранилищем.
"""
from minio import Minio
from minio.error import S3Error
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..core.config import settings

logger = logging.getLogger(__name__)

class MinIOService:
    """Сервис для работы с MinIO"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        
    def test_connection(self) -> Dict[str, Any]:
        """Проверка подключения к MinIO"""
        try:
            # Проверяем доступность MinIO
            buckets = self.client.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            return {
                "status": "healthy",
                "message": "MinIO доступен",
                "buckets": bucket_names,
                "bucket_exists": self.bucket_name in bucket_names
            }
        except Exception as e:
            logger.error(f"Ошибка подключения к MinIO: {e}")
            return {
                "status": "critical",
                "message": f"Ошибка подключения: {str(e)}",
                "error": str(e)
            }
    
    def ensure_bucket_exists(self) -> bool:
        """Создание бакета если не существует"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Создан бакет: {self.bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания бакета: {e}")
            return False
    
    def upload_file(self, object_name: str, file_path: str, content_type: str = "application/octet-stream") -> bool:
        """Загрузка файла в MinIO"""
        try:
            self.ensure_bucket_exists()
            self.client.fput_object(
                self.bucket_name, object_name, file_path, content_type=content_type
            )
            logger.info(f"Файл загружен: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки файла {object_name}: {e}")
            return False
    
    def upload_json(self, object_name: str, data: Dict[str, Any]) -> bool:
        """Загрузка JSON данных в MinIO"""
        try:
            self.ensure_bucket_exists()
            json_data = json.dumps(data, default=str)
            self.client.put_object(
                self.bucket_name, object_name, 
                json_data.encode('utf-8'), 
                length=len(json_data.encode('utf-8')),
                content_type="application/json"
            )
            logger.info(f"JSON загружен: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки JSON {object_name}: {e}")
            return False
    
    def download_file(self, object_name: str, file_path: str) -> bool:
        """Скачивание файла из MinIO"""
        try:
            self.client.fget_object(self.bucket_name, object_name, file_path)
            logger.info(f"Файл скачан: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка скачивания файла {object_name}: {e}")
            return False
    
    def download_json(self, object_name: str) -> Optional[Dict[str, Any]]:
        """Скачивание JSON данных из MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = json.loads(response.read().decode('utf-8'))
            logger.info(f"JSON скачан: {object_name}")
            return data
        except Exception as e:
            logger.error(f"Ошибка скачивания JSON {object_name}: {e}")
            return None
    
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """Список файлов в бакете"""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified
                }
                for obj in objects
            ]
        except Exception as e:
            logger.error(f"Ошибка получения списка файлов: {e}")
            return []
    
    def delete_file(self, object_name: str) -> bool:
        """Удаление файла из MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Файл удален: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка удаления файла {object_name}: {e}")
            return False
    
    def file_exists(self, object_name: str) -> bool:
        """Проверка существования файла"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            raise e
        except Exception as e:
            logger.error(f"Ошибка проверки файла {object_name}: {e}")
            return False
    
    def get_file_info(self, object_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о файле"""
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                "name": object_name,
                "size": stat.size,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
                "etag": stat.etag
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о файле {object_name}: {e}")
            return None
    
    def generate_presigned_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """Генерация presigned URL для доступа к файлу"""
        try:
            url = self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(seconds=expires)
            )
            return url
        except Exception as e:
            logger.error(f"Ошибка генерации presigned URL для {object_name}: {e}")
            return None
    
    # Специфичные методы для wildfire prediction
    def upload_weather_data(self, data: Dict[str, Any], filename: str) -> bool:
        """Загрузка метеоданных"""
        object_name = f"weather_data/{filename}"
        return self.upload_json(object_name, data)
    
    def download_weather_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Скачивание метеоданных"""
        object_name = f"weather_data/{filename}"
        return self.download_json(object_name)
    
    def upload_model_artifact(self, artifact_data: Dict[str, Any], model_version: str) -> bool:
        """Загрузка артефакта модели"""
        object_name = f"models/{model_version}/artifact.json"
        return self.upload_json(object_name, artifact_data)
    
    def download_model_artifact(self, model_version: str) -> Optional[Dict[str, Any]]:
        """Скачивание артефакта модели"""
        object_name = f"models/{model_version}/artifact.json"
        return self.download_json(object_name)
    
    def upload_prediction_result(self, prediction_data: Dict[str, Any], prediction_id: str) -> bool:
        """Загрузка результата предсказания"""
        object_name = f"predictions/{prediction_id}/result.json"
        return self.upload_json(object_name, prediction_data)
    
    def download_prediction_result(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Скачивание результата предсказания"""
        object_name = f"predictions/{prediction_id}/result.json"
        return self.download_json(object_name) 