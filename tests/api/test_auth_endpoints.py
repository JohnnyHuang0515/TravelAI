import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI
import datetime

from src.itinerary_planner.api.v1.endpoints.auth import (
    router,
    register,
    login,
    refresh_token,
    logout,
    get_current_user_info,
    update_current_user,
    change_password,
    get_user_preferences,
    update_user_preferences
)
from src.itinerary_planner.api.v1.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UpdatePreferenceRequest
)
from src.itinerary_planner.infrastructure.persistence.orm_models import User


class TestAuthEndpoints:
    """測試認證 API 端點"""

    @pytest.fixture
    def app(self):
        """建立 FastAPI 應用程式"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """建立測試客戶端"""
        return TestClient(app)

    @pytest.fixture
    def sample_user(self):
        """建立範例使用者"""
        user = Mock(spec=User)
        user.id = "user123"
        user.email = "test@example.com"
        user.username = "testuser"
        user.is_active = True
        user.is_verified = True
        user.created_at = datetime.datetime.now(datetime.timezone.utc)
        user.last_login = datetime.datetime.now(datetime.timezone.utc)
        user.avatar_url = None
        user.profile = None
        return user

    @pytest.fixture
    def sample_register_request(self):
        """建立範例註冊請求"""
        return RegisterRequest(
            email="newuser@example.com",
            password="password123",
            username="newuser"
        )

    @pytest.fixture
    def sample_login_request(self):
        """建立範例登入請求"""
        return LoginRequest(
            email="test@example.com",
            password="password123"
        )

    @pytest.fixture
    def sample_refresh_request(self):
        """建立範例刷新令牌請求"""
        return RefreshTokenRequest(
            refresh_token="refresh_token_123"
        )

    @pytest.fixture
    def sample_change_password_request(self):
        """建立範例修改密碼請求"""
        return ChangePasswordRequest(
            old_password="old_password",
            new_password="new_password123"
        )

    @pytest.fixture
    def sample_update_preference_request(self):
        """建立範例更新偏好請求"""
        return UpdatePreferenceRequest(
            favorite_themes=["美食", "文化"],
            travel_pace="relaxed",
            budget_level="moderate",
            default_daily_start="09:00",
            default_daily_end="18:00"
        )

    @pytest.mark.asyncio
    async def test_register_success(self, sample_register_request, sample_user):
        """測試成功註冊"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬註冊成功
            mock_auth_service.register.return_value = (
                sample_user,
                "access_token_123",
                "refresh_token_123"
            )
            
            result = await register(sample_register_request, mock_auth_service)
            
            assert result["user"]["email"] == sample_user.email
            assert result["access_token"] == "access_token_123"
            assert result["refresh_token"] == "refresh_token_123"
            mock_auth_service.register.assert_called_once_with(
                email=sample_register_request.email,
                password=sample_register_request.password,
                username=sample_register_request.username
            )

    @pytest.mark.asyncio
    async def test_register_email_exists(self, sample_register_request):
        """測試註冊時郵箱已存在"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬郵箱已存在
            mock_auth_service.register.side_effect = ValueError("Email 已存在")
            
            with pytest.raises(HTTPException) as exc_info:
                await register(sample_register_request, mock_auth_service)
            
            assert exc_info.value.status_code == 400
            assert "Email 已存在" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_success(self, sample_login_request, sample_user):
        """測試成功登入"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬登入成功
            mock_auth_service.login.return_value = (
                sample_user,
                "access_token_123",
                "refresh_token_123"
            )
            
            result = await login(sample_login_request, mock_auth_service)
            
            assert result["user"]["email"] == sample_user.email
            assert result["access_token"] == "access_token_123"
            assert result["refresh_token"] == "refresh_token_123"
            mock_auth_service.login.assert_called_once_with(
                email=sample_login_request.email,
                password=sample_login_request.password
            )

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, sample_login_request):
        """測試登入時憑證無效"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬憑證無效
            mock_auth_service.login.side_effect = ValueError("無效的憑證")
            
            with pytest.raises(HTTPException) as exc_info:
                await login(sample_login_request, mock_auth_service)
            
            assert exc_info.value.status_code == 401
            assert "無效的憑證" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, sample_refresh_request):
        """測試成功刷新令牌"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬刷新成功
            mock_auth_service.refresh_access_token.return_value = "new_access_token_456"
            
            result = await refresh_token(sample_refresh_request, mock_auth_service)
            
            assert result.access_token == "new_access_token_456"
            mock_auth_service.refresh_access_token.assert_called_once_with(
                sample_refresh_request.refresh_token
            )

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, sample_refresh_request):
        """測試刷新令牌無效"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬令牌無效
            mock_auth_service.refresh_access_token.side_effect = ValueError("Refresh Token 無效或已過期")
            
            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(sample_refresh_request, mock_auth_service)
            
            assert exc_info.value.status_code == 401
            assert "Refresh Token 無效或已過期" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_info_success(self, sample_user):
        """測試成功獲取當前使用者資訊"""
        result = await get_current_user_info(sample_user)
        
        assert result["id"] == str(sample_user.id)
        assert result["email"] == sample_user.email
        assert result["username"] == sample_user.username
        assert result["is_verified"] == sample_user.is_verified

    @pytest.mark.asyncio
    async def test_logout_success(self, sample_user):
        """測試成功登出"""
        result = await logout(sample_user)
        
        assert result.message == "登出成功"

    @pytest.mark.asyncio
    async def test_change_password_success(self, sample_user, sample_change_password_request):
        """測試成功修改密碼"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬修改密碼成功
            mock_auth_service.change_password.return_value = True
            
            result = await change_password(sample_change_password_request, sample_user, mock_auth_service)
            
            assert result.message == "密碼修改成功"
            mock_auth_service.change_password.assert_called_once_with(
                user_id=str(sample_user.id),
                old_password=sample_change_password_request.old_password,
                new_password=sample_change_password_request.new_password
            )

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, sample_user, sample_change_password_request):
        """測試修改密碼時當前密碼錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.get_auth_service') as mock_get_auth_service:
            mock_auth_service = Mock()
            mock_get_auth_service.return_value = mock_auth_service
            
            # 模擬當前密碼錯誤
            mock_auth_service.change_password.side_effect = ValueError("當前密碼錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await change_password(sample_change_password_request, sample_user, mock_auth_service)
            
            assert exc_info.value.status_code == 400
            assert "當前密碼錯誤" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_user_preferences_not_found(self, sample_user):
        """測試獲取偏好時偏好不存在"""
        with patch('src.itinerary_planner.api.v1.endpoints.auth.UserPreferenceRepository') as mock_pref_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.auth.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_pref_repo = Mock()
            mock_pref_repo_class.return_value = mock_pref_repo
            
            # 模擬偏好不存在
            mock_pref_repo.get_by_user_id.return_value = None
            
            result = await get_user_preferences(sample_user, mock_db)
            
            # 應該返回預設偏好
            assert result.favorite_themes == []
            assert result.travel_pace == "moderate"
            assert result.budget_level == "moderate"

    def test_register_request_model(self):
        """測試 RegisterRequest 模型"""
        request = RegisterRequest(
            email="test@example.com",
            password="password123",
            username="testuser"
        )
        
        assert request.email == "test@example.com"
        assert request.password == "password123"
        assert request.username == "testuser"

    def test_login_request_model(self):
        """測試 LoginRequest 模型"""
        request = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_refresh_token_request_model(self):
        """測試 RefreshTokenRequest 模型"""
        request = RefreshTokenRequest(
            refresh_token="refresh_token_123"
        )
        
        assert request.refresh_token == "refresh_token_123"

    def test_change_password_request_model(self):
        """測試 ChangePasswordRequest 模型"""
        request = ChangePasswordRequest(
            old_password="old_password",
            new_password="new_password123"
        )
        
        assert request.old_password == "old_password"
        assert request.new_password == "new_password123"

    def test_update_preference_request_model(self):
        """測試 UpdatePreferenceRequest 模型"""
        request = UpdatePreferenceRequest(
            favorite_themes=["美食", "文化"],
            travel_pace="relaxed",
            budget_level="moderate",
            default_daily_start="09:00",
            default_daily_end="18:00"
        )
        
        assert request.favorite_themes == ["美食", "文化"]
        assert request.travel_pace == "relaxed"
        assert request.budget_level == "moderate"
        assert request.default_daily_start == "09:00"
        assert request.default_daily_end == "18:00"

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == "/auth"
        assert len(router.routes) == 9  # register, login, refresh, logout, me (GET), me (PUT), change-password, preferences (GET), preferences (PUT)

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/auth/register" in route_paths
        assert "/auth/login" in route_paths
        assert "/auth/refresh" in route_paths
        assert "/auth/logout" in route_paths
        assert "/auth/me" in route_paths
        assert "/auth/me/change-password" in route_paths
        assert "/auth/me/preferences" in route_paths
