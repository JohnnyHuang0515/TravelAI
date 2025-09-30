"""
認證相關的 FastAPI Dependencies
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ....infrastructure.persistence.database import get_db
from ....application.services.auth_service import AuthService
from ....infrastructure.persistence.orm_models import User


# 安全性設定
security = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """取得認證服務"""
    return AuthService(db)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    取得當前登入的使用者（必須登入）
    
    Raises:
        HTTPException: 如果未登入或 Token 無效
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供認證資訊",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 無效或已過期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已被停用"
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    取得當前使用者（可選，允許訪客）
    
    Returns:
        User 或 None（訪客）
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    
    if user and user.is_active:
        return user
    
    return None
