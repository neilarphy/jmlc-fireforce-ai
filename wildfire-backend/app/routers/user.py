"""
User endpoints for managing user settings and preferences.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from ..schemas.user import UserSettings, SettingsUpdate
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/user", tags=["user"])

# Инициализация сервиса
db_service = DatabaseService()

@router.get("/settings", response_model=UserSettings)
async def get_user_settings():
    """Получение настроек пользователя"""
    try:
        # В реальном приложении здесь была бы логика получения настроек из БД
        # Пока возвращаем настройки по умолчанию
        settings = UserSettings()
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user settings: {str(e)}"
        )

@router.put("/settings")
async def update_user_settings(settings_update: SettingsUpdate):
    """Обновление настроек пользователя"""
    try:
        # В реальном приложении здесь была бы логика сохранения в БД
        # Пока просто возвращаем успешный ответ
        return {
            "message": "User settings updated successfully",
            "settings": settings_update.settings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user settings: {str(e)}"
        )

@router.get("/profile")
async def get_user_profile():
    """Получение профиля пользователя"""
    try:
        # В реальном приложении здесь была бы логика получения профиля из БД
        profile = {
            "id": 1,
            "username": "admin",
            "email": "admin@wildfire.com",
            "full_name": "Администратор системы",
            "role": "admin",
            "created_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-15T10:30:00Z"
        }
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.put("/profile")
async def update_user_profile(profile_data: dict):
    """Обновление профиля пользователя"""
    try:
        # В реальном приложении здесь была бы логика обновления в БД
        return {
            "message": "User profile updated successfully",
            "profile": profile_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update user profile: {str(e)}"
        ) 