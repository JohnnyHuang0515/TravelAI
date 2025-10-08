"""
OAuth 認證服務
"""

import secrets
import httpx
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from ...infrastructure.config.oauth_config import OAuthConfig
from ...infrastructure.persistence.orm_models import User, UserPreference
from ...infrastructure.repositories.user_repository import UserRepository, UserPreferenceRepository
from .auth_service import AuthService


class OAuthService:
    """OAuth 認證服務"""
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service
        self.oauth_states: Dict[str, datetime] = {}  # 簡單的狀態儲存，生產環境應使用 Redis
    
    def generate_state(self) -> str:
        """生成 OAuth state 參數"""
        state = secrets.token_urlsafe(32)
        self.oauth_states[state] = datetime.utcnow() + timedelta(minutes=10)
        return state
    
    def validate_state(self, state: str) -> bool:
        """驗證 OAuth state 參數"""
        if state not in self.oauth_states:
            return False
        
        expiry = self.oauth_states[state]
        if datetime.utcnow() > expiry:
            del self.oauth_states[state]
            return False
        
        del self.oauth_states[state]
        return True
    
    async def get_google_auth_url(self) -> str:
        """取得 Google OAuth 授權 URL"""
        if not OAuthConfig.is_google_configured():
            raise ValueError("Google OAuth 尚未配置")
        
        state = self.generate_state()
        return OAuthConfig.get_google_auth_url(state)
    
    async def exchange_google_code(self, code: str) -> Dict:
        """交換 Google OAuth code 取得 access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OAuthConfig.GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": OAuthConfig.GOOGLE_CLIENT_ID,
                    "client_secret": OAuthConfig.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": OAuthConfig.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to exchange code: {response.text}")
            
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict:
        """取得 Google 使用者資訊"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OAuthConfig.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to get user info: {response.text}")
            
            return response.json()
    
    async def handle_google_callback(
        self, 
        code: str, 
        state: str
    ) -> Tuple[User, str]:
        """
        處理 Google OAuth 回調
        
        Returns:
            Tuple[User, str]: (使用者物件, JWT token)
        """
        # 驗證 state
        if not self.validate_state(state):
            raise ValueError("Invalid or expired state")
        
        # 交換 code 取得 access token
        token_data = await self.exchange_google_code(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("No access token received")
        
        # 取得使用者資訊
        user_info = await self.get_google_user_info(access_token)
        
        email = user_info.get("email")
        name = user_info.get("name")
        google_id = user_info.get("id")
        picture = user_info.get("picture")
        
        if not email or not google_id:
            raise ValueError("Incomplete user information")
        
        # 查詢或建立使用者
        user = self.user_repository.get_by_email(email)
        
        if user:
            # 更新現有使用者的 provider_id（如果尚未綁定）
            if not user.provider_id:
                user.provider_id = google_id
                user.provider = 'google'
                # 更新使用者資料
                self.user_repository.db.commit()
        else:
            # 建立新使用者
            user = self.user_repository.create_oauth_user(
                email=email,
                username=name or email.split("@")[0],
                provider='google',
                provider_id=google_id,  # 統一使用 provider_id
                profile={'avatar_url': picture}
            )
            
            # 建立預設偏好設定
            pref_repo = UserPreferenceRepository(self.user_repository.db)
            pref_repo.create_preference(user_id=str(user.id))
        
        # 生成 JWT token
        access_token = self.auth_service.create_access_token(str(user.id), user.email)
        refresh_token = self.auth_service.create_refresh_token(str(user.id), user.email)
        
        return user, access_token
