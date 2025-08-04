"""
Wildfire Prediction API - Main Application
"""
import warnings
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

# Отключаем предупреждения Pydantic и bcrypt
warnings.filterwarnings("ignore", message="Field.*has conflict with protected namespace.*")
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2.*")
warnings.filterwarnings("ignore", message="error reading bcrypt version.*")

from .routers import data, health
from .routers import predictions
from .core.config import settings
from .core.database import init_db
from .routers import (
    health_router, predictions_router, data_router, auth_router,
    alerts_router, history_router, regions_router, events_router,
    user_router, workers_router, models_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Starting Wildfire Prediction API...")
    # await init_db()  # Отключаем создание таблиц - они уже созданы миграциями
    print("✅ Database connection ready")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Wildfire Prediction API...")

# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API для предсказания лесных пожаров",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все origins
    allow_credentials=False,  # Отключаем credentials для wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(data.router, prefix=settings.API_V1_STR)
app.include_router(predictions.router)
app.include_router(auth_router)  # Аутентификация без префикса API_V1_STR

# Новые роутеры
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(history_router, prefix=settings.API_V1_STR)
app.include_router(regions_router, prefix=settings.API_V1_STR)
app.include_router(events_router, prefix=settings.API_V1_STR)
app.include_router(user_router, prefix=settings.API_V1_STR)
app.include_router(workers_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Wildfire Prediction API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Простой health check"""
    return {"status": "healthy", "service": "wildfire-prediction-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 