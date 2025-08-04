#!/usr/bin/env python3
"""
Скрипт для настройки подключения к удаленным сервисам.
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Создание .env файла"""
    env_content = """# =============================================================================
# 🔥 Wildfire Prediction API - Конфигурация для удаленных сервисов
# =============================================================================

# База данных PostgreSQL (удаленная)
DATABASE_URL=postgresql://wildfire_user:wildfire_pass@your-server.com:5432/wildfire_db

# Redis (удаленный)
REDIS_URL=redis://your-server.com:6379/0

# MLflow (удаленный)
MLFLOW_TRACKING_URI=http://your-server.com:5000
MLFLOW_MODEL_NAME=wildfire-prediction
MLFLOW_MODEL_VERSION=latest
MLFLOW_EXPERIMENT_NAME=wildfire-prediction

# MinIO (удаленный)
MINIO_ENDPOINT=your-server.com:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET=wildfire-data
MINIO_SECURE=true

# API настройки
API_V1_STR=/api/v1
PROJECT_NAME=Wildfire Prediction System
VERSION=1.0.0

# CORS (настройте под ваш домен)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "https://your-domain.com"]

# Безопасность
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  Файл .env уже существует!")
        response = input("Перезаписать? (y/N): ")
        if response.lower() != 'y':
            print("❌ Отменено")
            return False
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Файл .env создан")
    print("📝 Отредактируйте .env файл с вашими настройками сервисов")
    return True

def test_connections():
    """Тестирование подключений к сервисам"""
    print("🔍 Тестирование подключений к сервисам...")
    
    try:
        from app.core.config import settings
        
        print(f"📊 Настройки сервисов:")
        service_status = settings.get_service_status()
        
        for service, config in service_status.items():
            status = "✅" if config.get("configured") else "❌"
            print(f"  {status} {service}: {config}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def setup_database():
    """Настройка базы данных"""
    print("🗄️  Настройка базы данных...")
    
    # Создаем миграцию
    print("📝 Создание начальной миграции...")
    os.system("python migrate.py initial")
    
    # Применяем миграции
    print("⬆️  Применение миграций...")
    os.system("python migrate.py upgrade")
    
    print("✅ База данных настроена")

def setup_minio():
    """Настройка MinIO"""
    print("🗂️  Настройка MinIO...")
    
    try:
        from app.services.minio_service import MinIOService
        
        minio = MinIOService()
        result = minio.test_connection()
        
        if result.get("status") == "healthy":
            print("✅ MinIO подключение успешно")
            
            # Создаем бакет если не существует
            if minio.ensure_bucket_exists():
                print("✅ Бакет создан/проверен")
            else:
                print("❌ Ошибка создания бакета")
        else:
            print(f"❌ Ошибка подключения к MinIO: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Ошибка настройки MinIO: {e}")

def setup_mlflow():
    """Настройка MLflow"""
    print("🔬 Настройка MLflow...")
    
    try:
        from app.services.mlflow_service import MLflowService
        
        mlflow = MLflowService()
        result = mlflow.test_connection()
        
        if result.get("status") == "healthy":
            print("✅ MLflow подключение успешно")
        else:
            print(f"❌ Ошибка подключения к MLflow: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Ошибка настройки MLflow: {e}")

def main():
    """Главная функция"""
    print("🔥 Wildfire Prediction - Настройка удаленных сервисов")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("""
Использование:
  python setup_remote.py <команда>

Команды:
  env          - Создать .env файл
  test         - Тестировать подключения
  db           - Настроить базу данных
  minio        - Настроить MinIO
  mlflow       - Настроить MLflow
  all          - Выполнить все настройки

Примеры:
  python setup_remote.py env
  python setup_remote.py test
  python setup_remote.py all
        """)
        return
    
    command = sys.argv[1]
    
    if command == "env":
        create_env_file()
    elif command == "test":
        test_connections()
    elif command == "db":
        setup_database()
    elif command == "minio":
        setup_minio()
    elif command == "mlflow":
        setup_mlflow()
    elif command == "all":
        print("🚀 Выполнение всех настроек...")
        create_env_file()
        test_connections()
        setup_database()
        setup_minio()
        setup_mlflow()
        print("✅ Все настройки завершены!")
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main() 