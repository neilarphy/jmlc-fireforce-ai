# Routers package
from .health import router as health_router
from .predictions import router as predictions_router
from .data import router as data_router
from .auth import router as auth_router
from .alerts import router as alerts_router
from .history import router as history_router
from .regions import router as regions_router
from .events import router as events_router
from .user import router as user_router
from .workers import router as workers_router
from .models import router as models_router

__all__ = [
    "health_router",
    "predictions_router", 
    "data_router",
    "auth_router",
    "alerts_router",
    "history_router",
    "regions_router",
    "events_router",
    "user_router",
    "workers_router",
    "models_router",
] 