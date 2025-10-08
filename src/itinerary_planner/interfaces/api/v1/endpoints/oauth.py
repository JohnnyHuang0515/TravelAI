"""
OAuth 認證 API 端點
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from .....application.services.oauth_service import OAuthService
from .....application.services.auth_service import AuthService
from .....infrastructure.repositories.user_repository import UserRepository
from .....infrastructure.persistence.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth/oauth", tags=["OAuth"])


def get_oauth_service(db: Session = Depends(get_db)) -> OAuthService:
    """取得 OAuth 服務實例"""
    user_repository = UserRepository(db)
    auth_service = AuthService(db)
    return OAuthService(user_repository, auth_service)


@router.get("/google")
async def google_oauth_login(
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Google OAuth 登入
    
    重定向使用者到 Google 授權頁面
    """
    try:
        auth_url = await oauth_service.get_google_auth_url()
        return RedirectResponse(url=auth_url)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(..., description="Google OAuth authorization code"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """
    Google OAuth 回調端點
    
    處理 Google 授權後的回調，建立或登入使用者
    """
    try:
        user, token = await oauth_service.handle_google_callback(code, state)
        
        # 重定向到前端，帶上 token
        frontend_url = "http://localhost:3000/oauth/callback"
        redirect_url = f"{frontend_url}?token={token}"
        
        return RedirectResponse(url=redirect_url)
        
    except ValueError as e:
        # 錯誤時重定向到登入頁面，帶上錯誤訊息
        error_url = f"http://localhost:3000/login?error={str(e)}"
        return RedirectResponse(url=error_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")
