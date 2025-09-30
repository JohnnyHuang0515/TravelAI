"""
認證服務
處理使用者註冊、登入、JWT Token 生成等認證相關邏輯
"""

import os
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import bcrypt
import jwt
from sqlalchemy.orm import Session

from ...infrastructure.repositories.user_repository import UserRepository, UserPreferenceRepository
from ...infrastructure.persistence.orm_models import User


class AuthService:
    """認證服務"""
    
    # JWT 設定
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 小時
    REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 天
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.preference_repo = UserPreferenceRepository(db)
    
    # ========================================================================
    # 密碼處理
    # ========================================================================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密碼"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    # ========================================================================
    # JWT Token 處理
    # ========================================================================
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """建立 Access Token"""
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            'sub': str(user_id),
            'email': email,
            'exp': expire,
            'type': 'access'
        }
        return jwt.encode(payload, self.JWT_SECRET, algorithm=self.JWT_ALGORITHM)
    
    def create_refresh_token(self, user_id: str, email: str) -> str:
        """建立 Refresh Token"""
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            'sub': str(user_id),
            'email': email,
            'exp': expire,
            'type': 'refresh'
        }
        return jwt.encode(payload, self.JWT_SECRET, algorithm=self.JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """驗證 Token"""
        try:
            payload = jwt.decode(
                token,
                self.JWT_SECRET,
                algorithms=[self.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    # ========================================================================
    # 註冊與登入
    # ========================================================================
    
    def register(
        self,
        email: str,
        password: str,
        username: str = None
    ) -> Tuple[User, str, str]:
        """
        註冊新使用者
        
        Returns:
            (User, access_token, refresh_token)
        
        Raises:
            ValueError: 如果 Email 已存在
        """
        # 檢查 Email 是否已存在
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError('此 Email 已被註冊')
        
        # 加密密碼
        password_hash = self.hash_password(password)
        
        # 建立使用者
        user = self.user_repo.create_user(
            email=email,
            username=username or email.split('@')[0],
            password_hash=password_hash,
            provider='email'
        )
        
        # 建立預設偏好設定
        self.preference_repo.create_preference(user_id=str(user.id))
        
        # 生成 Token
        access_token = self.create_access_token(str(user.id), user.email)
        refresh_token = self.create_refresh_token(str(user.id), user.email)
        
        return user, access_token, refresh_token
    
    def login(self, email: str, password: str) -> Tuple[User, str, str]:
        """
        使用者登入
        
        Returns:
            (User, access_token, refresh_token)
        
        Raises:
            ValueError: 如果帳號密碼錯誤
        """
        # 查找使用者
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError('帳號或密碼錯誤')
        
        # 檢查是否為 Email 登入
        if user.provider != 'email':
            raise ValueError(f'此帳號使用 {user.provider} 登入，請使用正確的登入方式')
        
        # 驗證密碼
        if not self.verify_password(password, user.password_hash):
            raise ValueError('帳號或密碼錯誤')
        
        # 檢查帳號狀態
        if not user.is_active:
            raise ValueError('帳號已被停用')
        
        # 更新最後登入時間
        self.user_repo.update_last_login(str(user.id))
        
        # 生成 Token
        access_token = self.create_access_token(str(user.id), user.email)
        refresh_token = self.create_refresh_token(str(user.id), user.email)
        
        return user, access_token, refresh_token
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        使用 Refresh Token 更新 Access Token
        
        Returns:
            新的 access_token，失敗返回 None
        """
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
        
        user_id = payload.get('sub')
        email = payload.get('email')
        
        # 驗證使用者是否存在且活躍
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        # 生成新的 Access Token
        return self.create_access_token(user_id, email)
    
    # ========================================================================
    # OAuth 登入
    # ========================================================================
    
    def oauth_login(
        self,
        provider: str,
        provider_id: str,
        email: str,
        username: str = None,
        profile: dict = None
    ) -> Tuple[User, str, str]:
        """
        OAuth 登入（Google, Facebook 等）
        
        Returns:
            (User, access_token, refresh_token)
        """
        # 查找是否已有此 OAuth 帳號
        user = self.user_repo.get_by_provider(provider, provider_id)
        
        if not user:
            # 檢查 Email 是否已存在
            existing_user = self.user_repo.get_by_email(email)
            if existing_user:
                # Email 已存在但使用不同的登入方式
                raise ValueError(f'此 Email 已使用 {existing_user.provider} 註冊')
            
            # 建立新的 OAuth 使用者
            user = self.user_repo.create_oauth_user(
                email=email,
                username=username or email.split('@')[0],
                provider=provider,
                provider_id=provider_id,
                profile=profile or {}
            )
            
            # 建立預設偏好設定
            self.preference_repo.create_preference(user_id=str(user.id))
        else:
            # 更新最後登入時間
            self.user_repo.update_last_login(str(user.id))
        
        # 生成 Token
        access_token = self.create_access_token(str(user.id), user.email)
        refresh_token = self.create_refresh_token(str(user.id), user.email)
        
        return user, access_token, refresh_token
    
    # ========================================================================
    # 使用者資料
    # ========================================================================
    
    def get_current_user(self, token: str) -> Optional[User]:
        """根據 Token 取得當前使用者"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('sub')
        return self.user_repo.get_by_id(user_id)
    
    def update_user_profile(
        self,
        user_id: str,
        username: str = None,
        profile: dict = None
    ) -> Optional[User]:
        """更新使用者個人資料"""
        update_data = {}
        if username is not None:
            update_data['username'] = username
        if profile is not None:
            update_data['profile'] = profile
        
        return self.user_repo.update_user(user_id, **update_data)
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """修改密碼"""
        user = self.user_repo.get_by_id(user_id)
        if not user or user.provider != 'email':
            return False
        
        # 驗證舊密碼
        if not self.verify_password(old_password, user.password_hash):
            return False
        
        # 更新為新密碼
        new_hash = self.hash_password(new_password)
        self.user_repo.update_user(user_id, password_hash=new_hash)
        return True
