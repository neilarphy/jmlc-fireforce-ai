"""
Схемы для аутентификации пользователей.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    username: str
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: str  # Может быть email или username
    password: str

class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class UserProfile(BaseModel):
    """Схема профиля пользователя"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    api_key: Optional[str] = None

    class Config:
        from_attributes = True 