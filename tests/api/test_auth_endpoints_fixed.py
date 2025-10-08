"""
認證 API 端點測試（修復版）
使用 FastAPI 的 dependency override 機制
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import uuid4
import datetime

from src.itinerary_planner.api.v1.endpoints.auth import router
from src.itinerary_planner.api.v1.dependencies.auth import get_auth_service, get_current_user


class TestAuthEndpointsFixed:
    """認證 API 端點測試類別（修復版）"""
    
    @pytest.fixture
    def app(self):
        """建立 FastAPI 應用程式實例"""
        app = FastAPI()
        app.include_router(router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """建立測試客戶端"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_user(self):
        """測試用的使用者"""
        from src.itinerary_planner.infrastructure.persistence.orm_models import User
        user = User()
        user.id = str(uuid4())
        user.email = "test@example.com"
        user.username = "testuser"
        user.is_active = True
        user.is_verified = True
        user.provider = "email"
        user.created_at = datetime.datetime.now(datetime.timezone.utc)
        user.last_login = datetime.datetime.now(datetime.timezone.utc)
        user.avatar_url = None
        user.profile = None
        return user
    
    @pytest.fixture
    def mock_auth_service(self, sample_user):
        """Mock 認證服務"""
        service = Mock()
        service.register.return_value = (sample_user, "access_token", "refresh_token")
        service.login.return_value = (sample_user, "access_token", "refresh_token")
        service.refresh_access_token.return_value = "new_access_token_456"
        service.change_password.return_value = True
        return service
    
    def test_register_success(self, app, client, sample_user, mock_auth_service):
        """測試成功註冊"""
        # 覆蓋依賴
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        # 準備請求資料
        request_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "username": "newuser"
        }
        
        # 執行測試
        response = client.post("/auth/register", json=request_data)
        
        # 驗證結果
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == sample_user.email
        mock_auth_service.register.assert_called_once_with(
            email="newuser@example.com",
            password="password123",
            username="newuser"
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_register_email_already_exists(self, app, client, mock_auth_service):
        """測試註冊時 Email 已存在"""
        # 覆蓋依賴
        mock_auth_service.register.side_effect = ValueError("Email 已存在")
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        # 準備請求資料
        request_data = {
            "email": "existing@example.com",
            "password": "password123",
            "username": "existing"
        }
        
        # 執行測試
        response = client.post("/auth/register", json=request_data)
        
        # 驗證結果
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Email 已存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_login_success(self, app, client, sample_user, mock_auth_service):
        """測試成功登入"""
        # 覆蓋依賴
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        # 準備請求資料
        request_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # 執行測試
        response = client.post("/auth/login", json=request_data)
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        mock_auth_service.login.assert_called_once_with(
            email="test@example.com",
            password="password123"
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_login_invalid_credentials(self, app, client, mock_auth_service):
        """測試登入時憑證無效"""
        # 覆蓋依賴
        mock_auth_service.login.side_effect = ValueError("帳號或密碼錯誤")
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        # 準備請求資料
        request_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # 執行測試
        response = client.post("/auth/login", json=request_data)
        
        # 驗證結果
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "帳號或密碼錯誤" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_refresh_token_success(self, app, client, mock_auth_service):
        """測試成功刷新 token"""
        # 覆蓋依賴
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        # 準備請求資料
        request_data = {
            "refresh_token": "old_refresh_token"
        }
        
        # 執行測試
        response = client.post("/auth/refresh", json=request_data)
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] == "new_access_token_456"
        mock_auth_service.refresh_access_token.assert_called_once_with("old_refresh_token")
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_refresh_token_invalid(self, app, client, mock_auth_service):
        """測試刷新 token 時 token 無效"""
        # 覆蓋依賴
        mock_auth_service.refresh_access_token.side_effect = ValueError("Refresh Token 無效或已過期")
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        
        # 準備請求資料
        request_data = {
            "refresh_token": "invalid_token"
        }
        
        # 執行測試
        response = client.post("/auth/refresh", json=request_data)
        
        # 驗證結果
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Refresh Token 無效或已過期" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_change_password_success(self, app, client, sample_user, mock_auth_service):
        """測試成功修改密碼"""
        # 覆蓋依賴
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
        app.dependency_overrides[get_current_user] = lambda: sample_user
        
        # 準備請求資料
        request_data = {
            "old_password": "oldpassword",
            "new_password": "newpassword123"
        }
        
        # 執行測試
        response = client.post("/auth/me/change-password", json=request_data)
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "密碼修改成功" in data["message"]
        mock_auth_service.change_password.assert_called_once_with(
            user_id=sample_user.id,
            old_password="oldpassword",
            new_password="newpassword123"
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_profile_success(self, app, client, sample_user):
        """測試成功取得使用者資料"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        
        # 執行測試
        response = client.get("/auth/me")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user.id
        assert data["email"] == sample_user.email
        assert data["username"] == sample_user.username
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_register_invalid_email(self, client):
        """測試註冊時 Email 格式無效"""
        # 準備請求資料
        request_data = {
            "email": "invalid-email",
            "password": "password123",
            "username": "testuser"
        }
        
        # 執行測試
        response = client.post("/auth/register", json=request_data)
        
        # 驗證結果
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, client):
        """測試註冊時密碼太弱"""
        # 準備請求資料
        request_data = {
            "email": "test@example.com",
            "password": "123",  # 太短
            "username": "testuser"
        }
        
        # 執行測試
        response = client.post("/auth/register", json=request_data)
        
        # 驗證結果
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_fields(self, client):
        """測試登入時缺少必要欄位"""
        # 準備請求資料（缺少密碼）
        request_data = {
            "email": "test@example.com"
        }
        
        # 執行測試
        response = client.post("/auth/login", json=request_data)
        
        # 驗證結果
        assert response.status_code == 422  # Validation error
    
    def test_refresh_token_missing_token(self, client):
        """測試刷新 token 時缺少 token"""
        # 準備請求資料（缺少 refresh_token）
        request_data = {}
        
        # 執行測試
        response = client.post("/auth/refresh", json=request_data)
        
        # 驗證結果
        assert response.status_code == 422  # Validation error
