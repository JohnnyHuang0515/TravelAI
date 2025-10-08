"""
測試 OAuth Interface API 端點 (簡化版)
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, AsyncMock
import datetime
from uuid import uuid4

from src.itinerary_planner.infrastructure.persistence.orm_models import User
from src.itinerary_planner.main import app
from src.itinerary_planner.interfaces.api.v1.endpoints.oauth import get_oauth_service
from src.itinerary_planner.infrastructure.persistence.database import get_db


class TestOAuthInterfaceEndpoints:
    """測試 OAuth Interface 端點"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端"""
        return TestClient(app, follow_redirects=False)

    @pytest.fixture
    def sample_user(self):
        """建立範例使用者"""
        return User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            provider="google",
            provider_id="google_123456",
            avatar_url="https://example.com/avatar.jpg",
            profile=None,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            last_login=datetime.datetime.now(datetime.timezone.utc),
            is_active=True,
            is_verified=True
        )

    @pytest.fixture
    def mock_oauth_service(self):
        """Mock OAuth 服務"""
        service = AsyncMock()
        service.get_google_auth_url.return_value = "https://accounts.google.com/oauth/authorize?client_id=test"
        service.handle_google_callback.return_value = (Mock(), "access_token_123")
        return service

    def test_google_oauth_login_success(self, client, mock_oauth_service):
        """測試 Google OAuth 登入成功"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service

        # 執行測試
        response = client.get("/v1/auth/oauth/google")

        # 驗證結果
        assert response.status_code == 307  # RedirectResponse
        assert "accounts.google.com" in response.headers["location"]

        # 驗證服務調用
        mock_oauth_service.get_google_auth_url.assert_called_once()

        app.dependency_overrides.clear()

    def test_google_oauth_login_error(self, client, mock_oauth_service):
        """測試 Google OAuth 登入錯誤"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service

        # 設定 Mock 拋出錯誤
        mock_oauth_service.get_google_auth_url.side_effect = ValueError("OAuth 配置錯誤")

        # 執行測試
        response = client.get("/v1/auth/oauth/google")

        # 驗證結果
        assert response.status_code == 500
        assert "OAuth 配置錯誤" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_google_oauth_callback_success(self, client, mock_oauth_service, sample_user):
        """測試 Google OAuth 回調成功"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service

        # 執行測試
        response = client.get("/v1/auth/oauth/google/callback?code=test_code&state=test_state")

        # 驗證結果
        assert response.status_code == 307  # RedirectResponse
        location = response.headers["location"]
        assert "localhost:3000/oauth/callback" in location
        assert "token=access_token_123" in location

        # 驗證服務調用
        mock_oauth_service.handle_google_callback.assert_called_once_with("test_code", "test_state")

        app.dependency_overrides.clear()

    def test_google_oauth_callback_missing_params(self, client):
        """測試 Google OAuth 回調缺少參數"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試 - 缺少 code 參數
        response = client.get("/v1/auth/oauth/google/callback?state=test_state")

        # 驗證結果
        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()

    def test_google_oauth_callback_missing_state(self, client):
        """測試 Google OAuth 回調缺少 state 參數"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試 - 缺少 state 參數
        response = client.get("/v1/auth/oauth/google/callback?code=test_code")

        # 驗證結果
        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()
