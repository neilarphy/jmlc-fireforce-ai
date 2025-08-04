"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from .config import settings

# Создание движка базы данных
engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,  # Установить True для отладки SQL запросов
    connect_args={"options": "-c search_path=fireforceai,public"}
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """Генератор для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Инициализация базы данных"""
    try:
        # Создаем все таблицы
        from ..models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Проверяем подключение
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection verified")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise e 