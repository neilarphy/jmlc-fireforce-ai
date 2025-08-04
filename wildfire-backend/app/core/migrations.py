"""
Database migrations and seeding.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from .database import SessionLocal
from ..models import (
    RawFireData, ProcessedFireData, HistoricalFire,
    RawWeatherData, ProcessedWeatherData,
    FirePrediction, User, SystemHealth
)

def seed_test_data():
    """Заполнение тестовыми данными"""
    db = SessionLocal()
    try:
        # Создаем тестовые данные о пожарах
        print("🌲 Creating test fire data...")
        for i in range(10):
            fire = RawFireData(
                dt=datetime.now() - timedelta(days=random.randint(1, 365)),
                type_name="forest_fire",
                type_id=1,
                longitude=random.uniform(30, 180),  # Россия
                latitude=random.uniform(50, 80),     # Россия
                processed=False
            )
            db.add(fire)
        
        # Создаем тестовые метеоданные
        print("🌤️ Creating test weather data...")
        for i in range(20):
            weather = RawWeatherData(
                latitude=random.uniform(50, 80),
                longitude=random.uniform(30, 180),
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 720)),
                temperature_2m=random.uniform(-30, 35),
                relative_humidity=random.uniform(20, 100),
                wind_u=random.uniform(-20, 20),
                wind_v=random.uniform(-20, 20),
                precipitation=random.uniform(0, 50),
                data_source="ERA5",
                processed=False
            )
            db.add(weather)
        
        # Создаем тестовые предсказания
        print("🔮 Creating test predictions...")
        for i in range(15):
            prediction = FirePrediction(
                latitude=random.uniform(50, 80),
                longitude=random.uniform(30, 180),
                prediction_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                risk_score=random.uniform(0, 1),
                probability=random.uniform(0, 1),
                risk_level=random.choice(["low", "medium", "high", "extreme"]),
                model_version="v1.0.0",
                model_name="wildfire-prediction",
                prediction_type="single",
                confidence=random.uniform(0.5, 1.0)
            )
            db.add(prediction)
        
        # Создаем тестового пользователя
        print("👤 Creating test user...")
        test_user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/vYqKv6",  # password
            full_name="Test User",
            role="user",
            is_active=True,
            api_key="test_api_key_123"
        )
        db.add(test_user)
        
        # Создаем записи о здоровье системы
        print("🏥 Creating system health records...")
        services = ["database", "mlflow", "minio", "redis"]
        for service in services:
            health = SystemHealth(
                service_name=service,
                status=random.choice(["healthy", "warning", "critical"]),
                response_time=random.uniform(10, 500),
                error_rate=random.uniform(0, 5),
                uptime=random.uniform(95, 100),
                last_check=datetime.now(),
                error_message=None
            )
            db.add(health)
        
        db.commit()
        print("✅ Test data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding test data: {e}")
        raise e
    finally:
        db.close()

def create_tables():
    """Создание всех таблиц"""
    from .database import engine
    from ..models import Base
    
    print("🏗️ Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

def reset_database():
    """Сброс базы данных"""
    from .database import engine
    from ..models import Base
    
    print("🗑️ Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped successfully!")
    
    print("🏗️ Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables recreated successfully!")
    
    print("🌱 Seeding test data...")
    seed_test_data()
    print("✅ Database reset complete!")
 
if __name__ == "__main__":
    # Для запуска миграций напрямую
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            create_tables()
        elif command == "seed":
            seed_test_data()
        elif command == "reset":
            reset_database()
        else:
            print("Usage: python migrations.py [create|seed|reset]")
    else:
        print("Usage: python migrations.py [create|seed|reset]") 