"""
User settings schemas for API responses.
"""
from pydantic import BaseModel
from typing import Optional

class UserSettings(BaseModel):
    darkMode: bool = False
    autoRefresh: bool = True
    soundNotifications: bool = True
    language: str = "ru"
    colorScheme: str = "blue"

class SettingsUpdate(BaseModel):
    settings: UserSettings 