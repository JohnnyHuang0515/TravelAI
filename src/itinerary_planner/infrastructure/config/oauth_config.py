"""
OAuth 配置設定
"""

import os
from typing import Optional

class OAuthConfig:
    """OAuth 提供商配置"""
    
    # Google OAuth 設定
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8001/v1/auth/oauth/google/callback"
    )
    GOOGLE_AUTHORIZATION_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"
    GOOGLE_SCOPES: list = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    
    @classmethod
    def is_google_configured(cls) -> bool:
        """檢查 Google OAuth 是否已配置"""
        return bool(cls.GOOGLE_CLIENT_ID and cls.GOOGLE_CLIENT_SECRET)
    
    @classmethod
    def get_google_auth_url(cls, state: str) -> str:
        """生成 Google OAuth 授權 URL"""
        params = {
            "client_id": cls.GOOGLE_CLIENT_ID,
            "redirect_uri": cls.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(cls.GOOGLE_SCOPES),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{cls.GOOGLE_AUTHORIZATION_URL}?{query_string}"
