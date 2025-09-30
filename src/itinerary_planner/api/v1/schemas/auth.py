"""
認證相關的 Pydantic Schemas
"""

from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


# ============================================================================
# 請求 Schemas
# ============================================================================

class RegisterRequest(BaseModel):
    """註冊請求"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="密碼至少 8 個字元")
    username: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123",
                "username": "traveler_john"
            }
        }


class LoginRequest(BaseModel):
    """登入請求"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """刷新 Token 請求"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """修改密碼請求"""
    old_password: str
    new_password: str = Field(..., min_length=8)


# ============================================================================
# 回應 Schemas
# ============================================================================

class UserResponse(BaseModel):
    """使用者資料回應"""
    id: str
    email: str
    username: Optional[str]
    provider: str
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    @classmethod
    def from_orm(cls, user):
        """從 ORM 模型建立回應"""
        return cls(
            id=str(user.id),
            email=user.email,
            username=user.username,
            provider=user.provider,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    @classmethod
    def model_validate(cls, user):
        """Pydantic v2 相容的驗證方法"""
        return cls(
            id=str(user.id),
            email=user.email,
            username=user.username,
            provider=user.provider,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "traveler_john",
                "provider": "email",
                "is_verified": True,
                "created_at": "2025-09-30T10:00:00Z",
                "last_login": "2025-09-30T12:00:00Z"
            }
        }
    }


class AuthResponse(BaseModel):
    """認證成功回應"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "traveler_john",
                    "provider": "email",
                    "is_verified": False,
                    "created_at": "2025-09-30T10:00:00Z",
                    "last_login": None
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class RefreshTokenResponse(BaseModel):
    """刷新 Token 回應"""
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """通用訊息回應"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "操作成功"
            }
        }


# ============================================================================
# 使用者偏好 Schemas
# ============================================================================

class UserPreferenceResponse(BaseModel):
    """使用者偏好回應"""
    favorite_themes: list
    travel_pace: str
    budget_level: str
    default_daily_start: str
    default_daily_end: str
    custom_settings: dict
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "favorite_themes": ["美食", "自然", "文化"],
                "travel_pace": "moderate",
                "budget_level": "moderate",
                "default_daily_start": "09:00",
                "default_daily_end": "18:00",
                "custom_settings": {}
            }
        }


class UpdatePreferenceRequest(BaseModel):
    """更新偏好請求"""
    favorite_themes: Optional[list] = None
    travel_pace: Optional[str] = Field(None, pattern="^(relaxed|moderate|packed)$")
    budget_level: Optional[str] = Field(None, pattern="^(budget|moderate|luxury)$")
    default_daily_start: Optional[str] = None
    default_daily_end: Optional[str] = None
    custom_settings: Optional[dict] = None
