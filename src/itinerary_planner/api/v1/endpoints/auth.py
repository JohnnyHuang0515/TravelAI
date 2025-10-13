"""
認證相關 API 端點
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....infrastructure.persistence.database import get_db
from ....application.services.auth_service import AuthService
from ....infrastructure.repositories.user_repository import UserPreferenceRepository
from ....infrastructure.persistence.orm_models import User
from ..schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    AuthResponse,
    UserResponse,
    RefreshTokenResponse,
    MessageResponse,
    UserPreferenceResponse,
    UpdatePreferenceRequest
)
from ..dependencies.auth import get_auth_service, get_current_user


router = APIRouter(tags=["認證"])


# ============================================================================
# 註冊與登入
# ============================================================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    註冊新使用者
    
    - **email**: Email 地址（唯一）
    - **password**: 密碼（至少 8 個字元）
    - **username**: 使用者名稱（可選）
    """
    try:
        user, access_token, refresh_token = auth_service.register(
            email=request.email,
            password=request.password,
            username=request.username
        )
        
        # 直接返回 JSON 避免 Pydantic 驗證問題
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "provider": user.provider,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    使用者登入
    
    - **email**: Email 地址
    - **password**: 密碼
    """
    try:
        user, access_token, refresh_token = auth_service.login(
            email=request.email,
            password=request.password
        )
        
        # 直接返回 JSON 避免 Pydantic 驗證問題
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "provider": user.provider,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    刷新 Access Token
    
    - **refresh_token**: Refresh Token
    """
    try:
        new_access_token = auth_service.refresh_access_token(request.refresh_token)
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh Token 無效或已過期"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token 無效或已過期"
        )
    
    return RefreshTokenResponse(access_token=str(new_access_token))


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    登出
    
    註：前端需要自行刪除儲存的 Token
    """
    return MessageResponse(message="登出成功")


# ============================================================================
# 使用者資料
# ============================================================================

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """取得當前使用者資料"""
    # 直接返回 JSON 避免 Pydantic 驗證問題
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "provider": current_user.provider,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@router.put("/me")
async def update_current_user(
    username: str = None,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    更新當前使用者資料
    
    - **username**: 新的使用者名稱
    """
    updated_user = auth_service.update_user_profile(
        user_id=str(current_user.id),
        username=username
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在"
        )
    
    # 直接返回 JSON 避免 Pydantic 驗證問題
    return {
        "id": str(updated_user.id),
        "email": updated_user.email,
        "username": updated_user.username,
        "provider": updated_user.provider,
        "is_verified": updated_user.is_verified,
        "created_at": updated_user.created_at.isoformat(),
        "last_login": updated_user.last_login.isoformat() if updated_user.last_login else None
    }


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    修改密碼
    
    - **old_password**: 舊密碼
    - **new_password**: 新密碼（至少 8 個字元）
    """
    success = auth_service.change_password(
        user_id=str(current_user.id),
        old_password=request.old_password,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="舊密碼錯誤或此帳號不支援密碼修改"
        )
    
    return MessageResponse(message="密碼修改成功")


# ============================================================================
# 使用者偏好
# ============================================================================

@router.get("/me/preferences", response_model=UserPreferenceResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取得使用者偏好設定"""
    pref_repo = UserPreferenceRepository(db)
    preference = pref_repo.get_by_user_id(str(current_user.id))
    
    if not preference:
        # 如果不存在，建立預設偏好
        preference = pref_repo.create_preference(user_id=str(current_user.id))
    
    return UserPreferenceResponse.from_orm(preference)


@router.put("/me/preferences", response_model=UserPreferenceResponse)
async def update_user_preferences(
    request: UpdatePreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新使用者偏好設定
    
    - **favorite_themes**: 喜愛的旅遊主題
    - **travel_pace**: 旅遊節奏 (relaxed, moderate, packed)
    - **budget_level**: 預算等級 (budget, moderate, luxury)
    - **default_daily_start**: 預設每日開始時間
    - **default_daily_end**: 預設每日結束時間
    """
    pref_repo = UserPreferenceRepository(db)
    
    # 只更新有提供的欄位
    update_data = request.dict(exclude_none=True)
    
    preference = pref_repo.update_preference(
        user_id=str(current_user.id),
        **update_data
    )
    
    return UserPreferenceResponse.from_orm(preference)
