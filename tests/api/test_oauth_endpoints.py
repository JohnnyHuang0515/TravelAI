"""
OAuth API 端點測試
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from datetime import datetime
import uuid

from src.itinerary_planner.interfaces.api.v1.endpoints.oauth import router, get_oauth_service
from src.itinerary_planner.infrastructure.persistence.orm_models import User


class TestOAuthEndpoints:
    """OAuth 端點測試類別"""

    @pytest.fixture
    def app(self):
        """創建測試應用程式"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """創建測試客戶端"""
        return TestClient(app)

    @pytest.fixture
    def sample_user(self):
        """樣本用戶"""
        user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            username="testuser",
            provider="google",
            provider_id="google_123456",
            avatar_url="https://example.com/avatar.jpg",
            profile=None,
            created_at=datetime.now(),
            last_login=datetime.now(),
            is_active=True,
            is_verified=True
        )
        return user

    @pytest.fixture
    def mock_oauth_service(self):
        """模擬 OAuth 服務"""
        service = AsyncMock()
        service.get_google_auth_url = AsyncMock()
        service.handle_google_callback = AsyncMock()
        return service

    # ============================================================================
    # Google OAuth 登入測試
    # ============================================================================

    def test_google_oauth_login_success(self, client, app, mock_oauth_service):
        """測試成功 Google OAuth 登入"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值
        mock_oauth_service.get_google_auth_url.return_value = "https://accounts.google.com/oauth/authorize?client_id=test"
        
        # 發送請求
        response = client.get("/auth/oauth/google", follow_redirects=False)
        
        # 驗證響應
        assert response.status_code == 307  # RedirectResponse
        assert "accounts.google.com" in response.headers["location"]
        
        # 驗證服務調用
        mock_oauth_service.get_google_auth_url.assert_called_once()

    def test_google_oauth_login_error(self, client, app, mock_oauth_service):
        """測試 Google OAuth 登入錯誤"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出錯誤
        mock_oauth_service.get_google_auth_url.side_effect = ValueError("OAuth 配置錯誤")
        
        # 發送請求
        response = client.get("/auth/oauth/google")
        
        # 驗證響應
        assert response.status_code == 500
        assert "OAuth 配置錯誤" in response.json()["detail"]

    # ============================================================================
    # Google OAuth 回調測試
    # ============================================================================

    def test_google_oauth_callback_success(self, client, app, sample_user, mock_oauth_service):
        """測試成功 Google OAuth 回調"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值
        mock_oauth_service.handle_google_callback.return_value = (sample_user, "access_token_123")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=test_state",
            follow_redirects=False
        )
        
        # 驗證響應
        assert response.status_code == 307  # RedirectResponse
        assert "localhost:3000/oauth/callback" in response.headers["location"]
        assert "token=access_token_123" in response.headers["location"]
        
        # 驗證服務調用
        mock_oauth_service.handle_google_callback.assert_called_once_with("test_code", "test_state")

    def test_google_oauth_callback_missing_code(self, client, app, mock_oauth_service):
        """測試缺少 code 參數"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 發送請求 - 缺少 code 參數
        response = client.get("/auth/oauth/google/callback?state=test_state")
        
        # 驗證響應
        assert response.status_code == 422  # Validation error

    def test_google_oauth_callback_missing_state(self, client, app, mock_oauth_service):
        """測試缺少 state 參數"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 發送請求 - 缺少 state 參數
        response = client.get("/auth/oauth/google/callback?code=test_code")
        
        # 驗證響應
        assert response.status_code == 422  # Validation error

    def test_google_oauth_callback_invalid_code(self, client, app, mock_oauth_service):
        """測試無效的 code 參數"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出錯誤
        mock_oauth_service.handle_google_callback.side_effect = ValueError("無效的授權碼")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=invalid_code&state=test_state",
            follow_redirects=False
        )
        
        # 驗證響應
        assert response.status_code == 307  # RedirectResponse
        assert "localhost:3000/login" in response.headers["location"]
        # URL 編碼的中文字符
        assert "error=%E7%84%A1%E6%95%88%E7%9A%84%E6%8E%88%E6%AC%8A%E7%A2%BC" in response.headers["location"]

    def test_google_oauth_callback_invalid_state(self, client, app, mock_oauth_service):
        """測試無效的 state 參數"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出錯誤
        mock_oauth_service.handle_google_callback.side_effect = ValueError("無效的 state 參數")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=invalid_state",
            follow_redirects=False
        )
        
        # 驗證響應
        assert response.status_code == 307  # RedirectResponse
        assert "localhost:3000/login" in response.headers["location"]
        # URL 編碼的中文字符
        assert "error=%E7%84%A1%E6%95%88%E7%9A%84%20state%20%E5%8F%83%E6%95%B8" in response.headers["location"]

    def test_google_oauth_callback_general_error(self, client, app, mock_oauth_service):
        """測試一般錯誤"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出一般錯誤
        mock_oauth_service.handle_google_callback.side_effect = Exception("服務器錯誤")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=test_state"
        )
        
        # 驗證響應
        assert response.status_code == 500
        assert "OAuth callback failed: 服務器錯誤" in response.json()["detail"]

    def test_google_oauth_callback_token_error(self, client, app, mock_oauth_service):
        """測試 token 獲取錯誤"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出 token 錯誤
        mock_oauth_service.handle_google_callback.side_effect = ValueError("無法獲取 access token")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=test_state",
            follow_redirects=False
        )
        
        # 驗證響應
        assert response.status_code == 307  # RedirectResponse
        assert "localhost:3000/login" in response.headers["location"]
        # URL 編碼的中文字符
        assert "error=%E7%84%A1%E6%B3%95%E7%8D%B2%E5%8F%96%20access%20token" in response.headers["location"]

    def test_google_oauth_callback_user_info_error(self, client, app, mock_oauth_service):
        """測試用戶信息獲取錯誤"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出用戶信息錯誤
        mock_oauth_service.handle_google_callback.side_effect = ValueError("無法獲取用戶信息")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=test_state",
            follow_redirects=False
        )
        
        # 驗證響應
        assert response.status_code == 307  # RedirectResponse
        assert "localhost:3000/login" in response.headers["location"]
        # URL 編碼的中文字符
        assert "error=%E7%84%A1%E6%B3%95%E7%8D%B2%E5%8F%96%E7%94%A8%E6%88%B6%E4%BF%A1%E6%81%AF" in response.headers["location"]

    # ============================================================================
    # 配置和模型測試
    # ============================================================================

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == "/auth/oauth"
        assert len(router.routes) == 2  # google, google/callback

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/auth/oauth/google" in route_paths
        assert "/auth/oauth/google/callback" in route_paths

    def test_get_oauth_service_dependency(self):
        """測試 OAuth 服務依賴注入"""
        # 這個測試主要驗證依賴函數的結構
        assert callable(get_oauth_service)

    def test_redirect_response_format(self, client, app, mock_oauth_service):
        """測試重定向響應格式"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值
        mock_oauth_service.get_google_auth_url.return_value = "https://accounts.google.com/oauth/authorize"
        
        # 發送請求
        response = client.get("/auth/oauth/google", follow_redirects=False)
        
        # 驗證響應格式
        assert response.status_code == 307
        assert "location" in response.headers
        assert response.headers["location"].startswith("https://")

    def test_callback_redirect_format(self, client, app, sample_user, mock_oauth_service):
        """測試回調重定向格式"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值
        mock_oauth_service.handle_google_callback.return_value = (sample_user, "test_token")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=test_state",
            follow_redirects=False
        )
        
        # 驗證響應格式
        assert response.status_code == 307
        assert "location" in response.headers
        assert "localhost:3000/oauth/callback" in response.headers["location"]
        assert "token=test_token" in response.headers["location"]

    def test_error_redirect_format(self, client, app, mock_oauth_service):
        """測試錯誤重定向格式"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service
        
        # 設置模擬返回值 - 拋出錯誤
        mock_oauth_service.handle_google_callback.side_effect = ValueError("測試錯誤")
        
        # 發送請求
        response = client.get(
            "/auth/oauth/google/callback?code=test_code&state=test_state",
            follow_redirects=False
        )
        
        # 驗證響應格式
        assert response.status_code == 307
        assert "location" in response.headers
        assert "localhost:3000/login" in response.headers["location"]
        # URL 編碼的中文字符
        assert "error=%E6%B8%AC%E8%A9%A6%E9%8C%AF%E8%AA%A4" in response.headers["location"]

    def test_oauth_service_async_methods(self, mock_oauth_service):
        """測試 OAuth 服務異步方法"""
        # 驗證服務方法是否為異步
        assert hasattr(mock_oauth_service, 'get_google_auth_url')
        assert hasattr(mock_oauth_service, 'handle_google_callback')
        
        # 驗證方法可以被調用
        mock_oauth_service.get_google_auth_url.return_value = "test_url"
        mock_oauth_service.handle_google_callback.return_value = (None, "test_token")
        
        # 這些調用應該不會拋出異常（異步方法返回協程對象）
        import asyncio
        async def test_async_calls():
            result1 = await mock_oauth_service.get_google_auth_url()
            result2 = await mock_oauth_service.handle_google_callback("code", "state")
            assert result1 == "test_url"
            assert result2 == (None, "test_token")
        
        # 運行異步測試
        asyncio.run(test_async_calls())
