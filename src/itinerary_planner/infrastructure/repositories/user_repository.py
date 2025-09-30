"""
使用者 Repository
處理使用者相關的資料庫操作
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..persistence.orm_models import User, UserPreference


class UserRepository:
    """使用者資料存取 Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self,
        email: str,
        username: str,
        password_hash: str,
        provider: str = 'email'
    ) -> User:
        """建立新使用者"""
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            provider=provider,
            is_verified=False,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def create_oauth_user(
        self,
        email: str,
        username: str,
        provider: str,
        provider_id: str,
        profile: dict = None
    ) -> User:
        """建立 OAuth 使用者"""
        user = User(
            email=email,
            username=username,
            provider=provider,
            provider_id=provider_id,
            profile=profile or {},
            is_verified=True,  # OAuth 使用者預設已驗證
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """根據 ID 取得使用者"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根據 Email 取得使用者"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        """根據 OAuth Provider 取得使用者"""
        return self.db.query(User).filter(
            User.provider == provider,
            User.provider_id == provider_id
        ).first()
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """更新使用者資料"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_last_login(self, user_id: str) -> None:
        """更新最後登入時間"""
        from datetime import datetime
        self.update_user(user_id, last_login=datetime.utcnow())
    
    def delete_user(self, user_id: str) -> bool:
        """刪除使用者（軟刪除，設為不活躍）"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def verify_email(self, user_id: str) -> bool:
        """驗證使用者 Email"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        self.db.commit()
        return True


class UserPreferenceRepository:
    """使用者偏好 Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_preference(
        self,
        user_id: str,
        favorite_themes: list = None,
        travel_pace: str = 'moderate',
        budget_level: str = 'moderate'
    ) -> UserPreference:
        """建立使用者偏好"""
        preference = UserPreference(
            user_id=user_id,
            favorite_themes=favorite_themes or [],
            travel_pace=travel_pace,
            budget_level=budget_level
        )
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference
    
    def get_by_user_id(self, user_id: str) -> Optional[UserPreference]:
        """取得使用者偏好"""
        return self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
    
    def update_preference(self, user_id: str, **kwargs) -> Optional[UserPreference]:
        """更新使用者偏好"""
        preference = self.get_by_user_id(user_id)
        
        if not preference:
            # 如果不存在，建立新的
            return self.create_preference(user_id, **kwargs)
        
        for key, value in kwargs.items():
            if hasattr(preference, key) and value is not None:
                setattr(preference, key, value)
        
        self.db.commit()
        self.db.refresh(preference)
        return preference
