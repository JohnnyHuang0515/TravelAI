"""
認證服務單元測試
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import jwt

from src.itinerary_planner.application.services.auth_service import AuthService
from tests.test_orm_models import User


class TestAuthService:
    """認證服務測試類別"""
    
    @pytest.fixture
    def auth_service(self, test_db):
        """建立認證服務實例"""
        return AuthService(test_db)
    
    @pytest.fixture
    def sample_user_data(self):
        """測試用使用者資料"""
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
    
    def test_hash_password(self, auth_service):
        """測試密碼雜湊功能"""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        # 驗證雜湊結果不為空且不等於原始密碼
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password(self, auth_service):
        """測試密碼驗證功能"""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        # 驗證正確密碼
        assert auth_service.verify_password(password, hashed) is True
        
        # 驗證錯誤密碼
        assert auth_service.verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self, auth_service):
        """測試建立存取權杖"""
        user_id = "test-user-id"
        email = "test@example.com"
        
        token = auth_service.create_access_token(user_id, email)
        
        # 驗證權杖不為空
        assert token is not None
        assert len(token) > 0
        
        # 驗證權杖可以解碼
        decoded = jwt.decode(token, auth_service.JWT_SECRET, algorithms=[auth_service.JWT_ALGORITHM])
        assert decoded["sub"] == user_id
        assert decoded["email"] == email
        assert decoded["type"] == "access"
    
    def test_create_refresh_token(self, auth_service):
        """測試建立刷新權杖"""
        user_id = "test-user-id"
        email = "test@example.com"
        
        token = auth_service.create_refresh_token(user_id, email)
        
        # 驗證權杖不為空
        assert token is not None
        assert len(token) > 0
        
        # 驗證權杖可以解碼
        decoded = jwt.decode(token, auth_service.JWT_SECRET, algorithms=[auth_service.JWT_ALGORITHM])
        assert decoded["sub"] == user_id
        assert decoded["email"] == email
        assert decoded["type"] == "refresh"
    
    def test_verify_token_valid(self, auth_service):
        """測試驗證有效權杖"""
        user_id = "test-user-id"
        email = "test@example.com"
        
        token = auth_service.create_access_token(user_id, email)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["type"] == "access"
    
    def test_verify_token_invalid(self, auth_service):
        """測試驗證無效權杖"""
        invalid_token = "invalid.token.here"
        
        payload = auth_service.verify_token(invalid_token)
        assert payload is None
    
    def test_verify_token_expired(self, auth_service):
        """測試驗證過期權杖"""
        user_id = "test-user-id"
        email = "test@example.com"
        
        # 建立過期權杖
        expired_time = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "exp": expired_time
        }
        expired_token = jwt.encode(payload, auth_service.JWT_SECRET, algorithm=auth_service.JWT_ALGORITHM)
        
        result = auth_service.verify_token(expired_token)
        assert result is None
    
    def test_authenticate_user_success(self, auth_service):
        """測試使用者認證成功"""
        # Mock 使用者資料
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.password_hash = auth_service.hash_password("testpassword123")
        mock_user.provider = "email"
        mock_user.is_active = True
        
        # Mock 整個 user_repo 物件
        auth_service.user_repo = Mock()
        auth_service.user_repo.get_by_email.return_value = mock_user
        auth_service.user_repo.update_last_login.return_value = None
        
        # 執行登入
        result_user, access_token, refresh_token = auth_service.login("test@example.com", "testpassword123")
        
        assert result_user is not None
        assert result_user.id == "test-user-id"
        assert result_user.email == "test@example.com"
        assert access_token is not None
        assert refresh_token is not None
    
    def test_authenticate_user_wrong_password(self, auth_service):
        """測試使用者認證失敗 - 錯誤密碼"""
        # Mock 使用者資料
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.password_hash = auth_service.hash_password("correctpassword")
        mock_user.provider = "email"
        mock_user.is_active = True
        
        # Mock 整個 user_repo 物件
        auth_service.user_repo = Mock()
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        # 執行登入
        with pytest.raises(ValueError, match="帳號或密碼錯誤"):  # login 方法會拋出異常而不是返回 None
            auth_service.login("test@example.com", "wrongpassword")
    
    def test_authenticate_user_not_found(self, auth_service):
        """測試使用者認證失敗 - 使用者不存在"""
        # Mock 整個 user_repo 物件
        auth_service.user_repo = Mock()
        auth_service.user_repo.get_by_email.return_value = None
        
        # 執行登入
        with pytest.raises(ValueError, match="帳號或密碼錯誤"):  # login 方法會拋出異常而不是返回 None
            auth_service.login("nonexistent@example.com", "password")
    
    def test_authenticate_user_inactive(self, auth_service):
        """測試使用者認證失敗 - 使用者未啟用"""
        # Mock 使用者資料
        mock_user = Mock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.password_hash = auth_service.hash_password("testpassword123")
        mock_user.provider = "email"
        mock_user.is_active = False
        
        # Mock 整個 user_repo 物件
        auth_service.user_repo = Mock()
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        # 執行登入
        with pytest.raises(ValueError, match="帳號已被停用"):  # login 方法會拋出異常而不是返回 None
            auth_service.login("test@example.com", "testpassword123")
