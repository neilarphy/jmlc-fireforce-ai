"""
MinIO операторы для Airflow
Операторы для работы с MinIO объектным хранилищем.
"""
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class MinIODownloadOperator(BaseOperator):
    """
    Оператор для скачивания файлов из MinIO.
    """
    
    template_fields = ['bucket_name', 'object_name', 'local_path']
    
    @apply_defaults
    def __init__(self,
                 bucket_name: str,
                 object_name: str,
                 local_path: str,
                 minio_conn_id: str = 'minio_default',
                 *args, **kwargs):
        """
        Инициализация оператора скачивания.
        
        Args:
            bucket_name: Название бакета в MinIO
            object_name: Название объекта в бакете
            local_path: Локальный путь для сохранения файла
            minio_conn_id: ID подключения к MinIO
        """
        super().__init__(*args, **kwargs)
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.local_path = local_path
        self.minio_conn_id = minio_conn_id
    
    def execute(self, context):
        """Скачивание файла из MinIO."""
        logger.info(f"Downloading {self.object_name} from bucket {self.bucket_name}")
        
        # Получаем подключение к MinIO
        minio_client = self._get_minio_client()
        
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
            
            # Скачиваем файл
            minio_client.fget_object(self.bucket_name, self.object_name, self.local_path)
            
            logger.info(f"Successfully downloaded {self.object_name} to {self.local_path}")
            return self.local_path
            
        except S3Error as e:
            logger.error(f"Error downloading from MinIO: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _get_minio_client(self):
        """Получение клиента MinIO."""
        # В реальности здесь должна быть логика получения подключения из Airflow
        # Пока используем хардкод для примера
        return Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )


class MinIOUploadOperator(BaseOperator):
    """
    Оператор для загрузки файлов в MinIO.
    """
    
    template_fields = ['bucket_name', 'object_name', 'local_path']
    
    @apply_defaults
    def __init__(self,
                 bucket_name: str,
                 object_name: str,
                 local_path: str,
                 minio_conn_id: str = 'minio_default',
                 *args, **kwargs):
        """
        Инициализация оператора загрузки.
        
        Args:
            bucket_name: Название бакета в MinIO
            object_name: Название объекта в бакете
            local_path: Локальный путь к файлу
            minio_conn_id: ID подключения к MinIO
        """
        super().__init__(*args, **kwargs)
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.local_path = local_path
        self.minio_conn_id = minio_conn_id
    
    def execute(self, context):
        """Загрузка файла в MinIO."""
        logger.info(f"Uploading {self.local_path} to bucket {self.bucket_name} as {self.object_name}")
        
        # Получаем подключение к MinIO
        minio_client = self._get_minio_client()
        
        try:
            # Проверяем существование файла
            if not os.path.exists(self.local_path):
                raise FileNotFoundError(f"File {self.local_path} not found")
            
            # Создаем бакет если не существует
            if not minio_client.bucket_exists(self.bucket_name):
                minio_client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket {self.bucket_name}")
            
            # Загружаем файл
            minio_client.fput_object(self.bucket_name, self.object_name, self.local_path)
            
            logger.info(f"Successfully uploaded {self.local_path} to {self.object_name}")
            return f"s3://{self.bucket_name}/{self.object_name}"
            
        except S3Error as e:
            logger.error(f"Error uploading to MinIO: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _get_minio_client(self):
        """Получение клиента MinIO."""
        return Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )


class MinIOListOperator(BaseOperator):
    """
    Оператор для получения списка объектов в MinIO.
    """
    
    template_fields = ['bucket_name', 'prefix']
    
    @apply_defaults
    def __init__(self,
                 bucket_name: str,
                 prefix: str = "",
                 minio_conn_id: str = 'minio_default',
                 *args, **kwargs):
        """
        Инициализация оператора списка.
        
        Args:
            bucket_name: Название бакета в MinIO
            prefix: Префикс для фильтрации объектов
            minio_conn_id: ID подключения к MinIO
        """
        super().__init__(*args, **kwargs)
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.minio_conn_id = minio_conn_id
    
    def execute(self, context):
        """Получение списка объектов."""
        logger.info(f"Listing objects in bucket {self.bucket_name} with prefix {self.prefix}")
        
        # Получаем подключение к MinIO
        minio_client = self._get_minio_client()
        
        try:
            # Получаем список объектов
            objects = minio_client.list_objects(self.bucket_name, prefix=self.prefix)
            
            object_list = []
            for obj in objects:
                object_list.append({
                    'name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified
                })
            
            logger.info(f"Found {len(object_list)} objects in bucket {self.bucket_name}")
            
            # Сохраняем результат в XCom
            context['task_instance'].xcom_push(key='minio_objects', value=object_list)
            
            return object_list
            
        except S3Error as e:
            logger.error(f"Error listing MinIO objects: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _get_minio_client(self):
        """Получение клиента MinIO."""
        return Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )


class MinIODataValidationOperator(BaseOperator):
    """
    Оператор для валидации данных в MinIO.
    """
    
    template_fields = ['bucket_name', 'object_name']
    
    @apply_defaults
    def __init__(self,
                 bucket_name: str,
                 object_name: str,
                 validation_rules: Dict[str, Any],
                 minio_conn_id: str = 'minio_default',
                 *args, **kwargs):
        """
        Инициализация оператора валидации.
        
        Args:
            bucket_name: Название бакета в MinIO
            object_name: Название объекта в бакете
            validation_rules: Правила валидации
            minio_conn_id: ID подключения к MinIO
        """
        super().__init__(*args, **kwargs)
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.validation_rules = validation_rules
        self.minio_conn_id = minio_conn_id
    
    def execute(self, context):
        """Валидация данных в MinIO."""
        logger.info(f"Validating data in {self.object_name} from bucket {self.bucket_name}")
        
        # Получаем подключение к MinIO
        minio_client = self._get_minio_client()
        
        try:
            # Скачиваем файл во временную директорию
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                minio_client.fget_object(self.bucket_name, self.object_name, tmp_file.name)
                file_path = tmp_file.name
            
            # Валидируем данные в зависимости от типа файла
            validation_results = self._validate_file(file_path)
            
            # Очистка временного файла
            os.unlink(file_path)
            
            # Проверяем результаты валидации
            failed_validations = [rule for rule, result in validation_results.items() if not result['passed']]
            
            if failed_validations:
                logger.error(f"Data validation failed for rules: {failed_validations}")
                raise Exception(f"Data validation failed for rules: {failed_validations}")
            else:
                logger.info("All data validation checks passed")
            
            # Сохраняем результаты в XCom
            context['task_instance'].xcom_push(key='validation_results', value=validation_results)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            raise
    
    def _validate_file(self, file_path: str) -> Dict[str, Any]:
        """Валидация файла."""
        import pandas as pd
        
        validation_results = {}
        
        try:
            # Определяем тип файла по расширению
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                # Валидация CSV файла
                df = pd.read_csv(file_path, sep=";")
                
                validation_results = {
                    'file_exists': {'passed': True, 'message': 'File exists'},
                    'has_data': {'passed': len(df) > 0, 'message': f'File has {len(df)} rows'},
                    'has_required_columns': {
                        'passed': all(col in df.columns for col in ['dt', 'lon', 'lat']),
                        'message': 'File has required columns'
                    },
                    'no_duplicates': {
                        'passed': not df.duplicated().any(),
                        'message': 'File has no duplicates'
                    },
                    'no_nulls_in_key_columns': {
                        'passed': not df[['dt', 'lon', 'lat']].isnull().any().any(),
                        'message': 'No nulls in key columns'
                    }
                }
                
            elif file_ext == '.nc':
                # Валидация NetCDF файла
                import xarray as xr
                
                ds = xr.open_dataset(file_path)
                
                validation_results = {
                    'file_exists': {'passed': True, 'message': 'File exists'},
                    'has_data': {'passed': len(ds.dims) > 0, 'message': 'File has dimensions'},
                    'has_required_variables': {
                        'passed': any(var in ds.data_vars for var in ['t2m', 'tp', 'u10', 'v10']),
                        'message': 'File has required variables'
                    },
                    'has_time_dimension': {
                        'passed': 'time' in ds.dims or 'valid_time' in ds.dims,
                        'message': 'File has time dimension'
                    }
                }
                
            else:
                validation_results = {
                    'file_exists': {'passed': True, 'message': 'File exists'},
                    'unknown_format': {'passed': False, 'message': f'Unknown file format: {file_ext}'}
                }
                
        except Exception as e:
            validation_results = {
                'file_readable': {'passed': False, 'message': f'Error reading file: {str(e)}'}
            }
        
        return validation_results
    
    def _get_minio_client(self):
        """Получение клиента MinIO."""
        return Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )


class WildfireMinIOPlugin:
    """Плагин с MinIO операторами."""
    
    name = "wildfire_minio_plugin"
    operators = [
        MinIODownloadOperator,
        MinIOUploadOperator,
        MinIOListOperator,
        MinIODataValidationOperator
    ]
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = [] 