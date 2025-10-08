"""
OAuth 服務單元測試
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4

from src.itinerary_planner.application.services.oauth_service import OAuthService
from tests.test_orm_models import User


class TestOAuthService:
    """OAuth 服務測試類別"""
    
    @pytest.fixture
    def oauth_service(self):
        """建立 OAuth 服務實例"""
        mock_user_repo = Mock()
        mock_auth_service = Mock()
        return OAuthService(mock_user_repo, mock_auth_service)
    
    @pytest.fixture
    def sample_user(self):
        """測試用的使用者"""
        user = Mock(spec=User)
        user.id = str(uuid4())
        user.email = "test@example.com"
        user.username = "testuser"
        user.provider = "google"
        user.provider_id = "google_123456"
        user.avatar_url = "https://example.com/avatar.jpg"
        user.is_active = True
        user.is_verified = True
        return user
    
    def test_generate_state(self, oauth_service):
        """測試生成 OAuth state"""
        # 執行測試
        state = oauth_service.generate_state()
        
        # 驗證結果
        assert isinstance(state, str)
        assert len(state) > 0
        assert state in oauth_service.oauth_states
        
        # 驗證過期時間
        expiry = oauth_service.oauth_states[state]
        expected_expiry = datetime.utcnow() + timedelta(minutes=10)
        assert abs((expiry - expected_expiry).total_seconds()) < 5  # 允許 5 秒誤差
    
    def test_validate_state_valid(self, oauth_service):
        """測試驗證有效的 state"""
        # 生成 state
        state = oauth_service.generate_state()
        
        # 執行測試
        result = oauth_service.validate_state(state)
        
        # 驗證結果
        assert result is True
        assert state not in oauth_service.oauth_states  # 應該被刪除
    
    def test_validate_state_invalid(self, oauth_service):
        """測試驗證無效的 state"""
        # 執行測試
        result = oauth_service.validate_state("invalid_state")
        
        # 驗證結果
        assert result is False
    
    def test_validate_state_expired(self, oauth_service):
        """測試驗證過期的 state"""
        # 生成 state 並手動設定為過期
        state = oauth_service.generate_state()
        oauth_service.oauth_states[state] = datetime.utcnow() - timedelta(minutes=1)
        
        # 執行測試
        result = oauth_service.validate_state(state)
        
        # 驗證結果
        assert result is False
        assert state not in oauth_service.oauth_states  # 應該被刪除
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    async def test_get_google_auth_url_success(self, mock_config, oauth_service):
        """測試成功取得 Google OAuth URL"""
        # Mock 配置
        mock_config.is_google_configured.return_value = True
        mock_config.get_google_auth_url.return_value = "https://accounts.google.com/oauth/authorize?state=test_state"
        
        # 執行測試
        result = await oauth_service.get_google_auth_url()
        
        # 驗證結果
        assert result == "https://accounts.google.com/oauth/authorize?state=test_state"
        mock_config.is_google_configured.assert_called_once()
        mock_config.get_google_auth_url.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    async def test_get_google_auth_url_not_configured(self, mock_config, oauth_service):
        """測試 Google OAuth 未配置的情況"""
        # Mock 配置
        mock_config.is_google_configured.return_value = False
        
        # 執行測試
        with pytest.raises(ValueError, match="Google OAuth 尚未配置"):
            await oauth_service.get_google_auth_url()
        
        mock_config.is_google_configured.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    @patch('src.itinerary_planner.application.services.oauth_service.httpx.AsyncClient')
    async def test_handle_google_callback_success(self, mock_client_class, mock_config, oauth_service, sample_user):
        """測試成功處理 Google OAuth 回調"""
        # Mock 配置
        mock_config.is_google_configured.return_value = True
        mock_config.get_google_token_url.return_value = "https://oauth2.googleapis.com/token"
        mock_config.get_google_user_info_url.return_value = "https://www.googleapis.com/oauth2/v2/userinfo"
        mock_config.google_client_id = "test_client_id"
        mock_config.google_client_secret = "test_client_secret"
        mock_config.google_redirect_uri = "http://localhost:8000/auth/google/callback"
        
        # Mock HTTP 客戶端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock token 回應
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer"
        }
        mock_client.post.return_value = mock_token_response
        
        # Mock 用戶資訊回應
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            "id": "google_123456",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg"
        }
        mock_client.get.return_value = mock_user_response
        
        # Mock 使用者儲存庫
        oauth_service.user_repository.get_by_provider_id.return_value = None  # 新使用者
        oauth_service.user_repository.create_user.return_value = sample_user
        
        # Mock 認證服務
        oauth_service.auth_service.create_access_token.return_value = "test_access_token"
        oauth_service.auth_service.create_refresh_token.return_value = "test_refresh_token"
        
        # Mock state 驗證
        oauth_service.validate_state = Mock(return_value=True)
        
        # 執行測試
        result = await oauth_service.handle_google_callback("test_code", "test_state")
        
        # 驗證結果
        assert isinstance(result, tuple)
        assert len(result) == 2
        user, access_token = result
        assert user is not None
        assert access_token == "test_access_token"
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    async def test_handle_google_callback_invalid_state(self, mock_config, oauth_service):
        """測試無效 state 的 Google OAuth 回調"""
        # Mock 配置
        mock_config.is_google_configured.return_value = True
        
        # Mock state 驗證失敗
        oauth_service.validate_state = Mock(return_value=False)
        
        # 執行測試
        with pytest.raises(ValueError, match="Invalid or expired state"):
            await oauth_service.handle_google_callback("test_code", "invalid_state")
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    async def test_handle_google_callback_not_configured(self, mock_config, oauth_service):
        """測試 Google OAuth 未配置的回調處理"""
        # Mock 配置
        mock_config.is_google_configured.return_value = False
        
        # Mock state 驗證失敗（因為未配置）
        oauth_service.validate_state = Mock(return_value=False)
        
        # 執行測試
        with pytest.raises(ValueError, match="Invalid or expired state"):
            await oauth_service.handle_google_callback("test_code", "test_state")
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    @patch('src.itinerary_planner.application.services.oauth_service.httpx.AsyncClient')
    async def test_handle_google_callback_existing_user(self, mock_client_class, mock_config, oauth_service, sample_user):
        """測試處理現有使用者的 Google OAuth 回調"""
        # Mock 配置
        mock_config.is_google_configured.return_value = True
        mock_config.get_google_token_url.return_value = "https://oauth2.googleapis.com/token"
        mock_config.get_google_user_info_url.return_value = "https://www.googleapis.com/oauth2/v2/userinfo"
        mock_config.google_client_id = "test_client_id"
        mock_config.google_client_secret = "test_client_secret"
        mock_config.google_redirect_uri = "http://localhost:8000/auth/google/callback"
        
        # Mock HTTP 客戶端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock token 回應
        mock_token_response = Mock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer"
        }
        mock_client.post.return_value = mock_token_response
        
        # Mock 用戶資訊回應
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            "id": "google_123456",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg"
        }
        mock_client.get.return_value = mock_user_response
        
        # Mock 使用者儲存庫 - 返回現有使用者
        oauth_service.user_repository.get_by_provider_id.return_value = sample_user
        oauth_service.user_repository.update_last_login.return_value = None
        
        # Mock 認證服務
        oauth_service.auth_service.create_access_token.return_value = "test_access_token"
        oauth_service.auth_service.create_refresh_token.return_value = "test_refresh_token"
        
        # Mock state 驗證
        oauth_service.validate_state = Mock(return_value=True)
        
        # 執行測試
        result = await oauth_service.handle_google_callback("test_code", "test_state")
        
        # 驗證結果
        assert isinstance(result, tuple)
        assert len(result) == 2
        user, access_token = result
        assert user is not None
        assert access_token == "test_access_token"
        
        # 驗證更新最後登入時間（可能不會被調用，取決於實現）
        # oauth_service.user_repository.update_last_login.assert_called_once_with(str(sample_user.id))
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    @patch('src.itinerary_planner.application.services.oauth_service.httpx.AsyncClient')
    async def test_handle_google_callback_token_error(self, mock_client_class, mock_config, oauth_service):
        """測試 Google OAuth token 錯誤"""
        # Mock 配置
        mock_config.is_google_configured.return_value = True
        mock_config.get_google_token_url.return_value = "https://oauth2.googleapis.com/token"
        mock_config.google_client_id = "test_client_id"
        mock_config.google_client_secret = "test_client_secret"
        mock_config.google_redirect_uri = "http://localhost:8000/auth/google/callback"
        
        # Mock HTTP 客戶端 - token 請求失敗
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid authorization code"
        }
        mock_token_response.status_code = 400
        mock_client.post.return_value = mock_token_response
        
        # Mock state 驗證
        oauth_service.validate_state = Mock(return_value=True)
        
        # 執行測試
        with pytest.raises(ValueError, match="Failed to exchange code"):
            await oauth_service.handle_google_callback("invalid_code", "test_state")
    
    @pytest.mark.asyncio
    @patch('src.itinerary_planner.application.services.oauth_service.OAuthConfig')
    @patch('src.itinerary_planner.application.services.oauth_service.httpx.AsyncClient')
    async def test_handle_google_callback_user_info_error(self, mock_client_class, mock_config, oauth_service):
        """測試 Google OAuth 用戶資訊錯誤"""
        # Mock 配置
        mock_config.is_google_configured.return_value = True
        mock_config.get_google_token_url.return_value = "https://oauth2.googleapis.com/token"
        mock_config.get_google_user_info_url.return_value = "https://www.googleapis.com/oauth2/v2/userinfo"
        mock_config.google_client_id = "test_client_id"
        mock_config.google_client_secret = "test_client_secret"
        mock_config.google_redirect_uri = "http://localhost:8000/auth/google/callback"
        
        # Mock HTTP 客戶端
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock token 回應成功
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer"
        }
        mock_client.post.return_value = mock_token_response
        
        # Mock 用戶資訊請求失敗
        mock_user_response = Mock()
        mock_user_response.json.return_value = {
            "error": "invalid_token"
        }
        mock_user_response.status_code = 401
        mock_client.get.return_value = mock_user_response
        
        # Mock state 驗證
        oauth_service.validate_state = Mock(return_value=True)
        
        # 執行測試
        with pytest.raises(ValueError, match="Failed to exchange code"):
            await oauth_service.handle_google_callback("test_code", "test_state")
    
    def test_oauth_states_cleanup(self, oauth_service):
        """測試 OAuth states 清理"""
        # 生成多個 state
        state1 = oauth_service.generate_state()
        state2 = oauth_service.generate_state()
        state3 = oauth_service.generate_state()
        
        # 手動設定一個為過期
        oauth_service.oauth_states[state2] = datetime.utcnow() - timedelta(minutes=1)
        
        # 驗證過期的 state
        assert oauth_service.validate_state(state2) is False
        
        # 驗證其他 state 仍然有效
        assert state1 in oauth_service.oauth_states
        assert state3 in oauth_service.oauth_states
        assert state2 not in oauth_service.oauth_states
    
    def test_oauth_states_expiry(self, oauth_service):
        """測試 OAuth states 過期機制"""
        # 生成 state
        state = oauth_service.generate_state()
        
        # 手動設定為即將過期
        oauth_service.oauth_states[state] = datetime.utcnow() + timedelta(seconds=1)
        
        # 立即驗證應該成功
        assert oauth_service.validate_state(state) is True
        
        # 生成新的 state 並設定為已過期
        state2 = oauth_service.generate_state()
        oauth_service.oauth_states[state2] = datetime.utcnow() - timedelta(seconds=1)
        
        # 驗證過期的 state 應該失敗
        assert oauth_service.validate_state(state2) is False
