import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.itinerary_planner.api.v1.dependencies.auth import (
    get_auth_service,
    get_current_user,
    get_current_user_optional,
    security
)
from src.itinerary_planner.application.services.auth_service import AuthService
from src.itinerary_planner.infrastructure.persistence.orm_models import User


class TestAuthDependencies:
    """測試認證依賴函數"""

    @pytest.fixture
    def mock_db_session(self):
        """模擬資料庫會話"""
        return Mock()

    @pytest.fixture
    def sample_user(self):
        """建立範例使用者"""
        user = Mock(spec=User)
        user.id = "user123"
        user.email = "test@example.com"
        user.username = "testuser"
        user.is_active = True
        user.is_verified = True
        return user

    @pytest.fixture
    def mock_auth_service(self):
        """模擬認證服務"""
        return Mock(spec=AuthService)

    def test_get_auth_service(self, mock_db_session):
        """測試取得認證服務"""
        with patch('src.itinerary_planner.api.v1.dependencies.auth.AuthService') as mock_auth_service_class:
            mock_auth_service = Mock()
            mock_auth_service_class.return_value = mock_auth_service
            
            result = get_auth_service(mock_db_session)
            
            assert result == mock_auth_service
            mock_auth_service_class.assert_called_once_with(mock_db_session)

    def test_get_current_user_success(self, mock_auth_service, sample_user):
        """測試成功取得當前使用者"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_auth_service.get_current_user.return_value = sample_user
        
        result = get_current_user(credentials, mock_auth_service)
        
        assert result == sample_user
        mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    def test_get_current_user_no_credentials(self, mock_auth_service):
        """測試未提供認證資訊"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None, mock_auth_service)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "未提供認證資訊"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_get_current_user_invalid_token(self, mock_auth_service):
        """測試無效的 Token"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        mock_auth_service.get_current_user.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, mock_auth_service)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Token 無效或已過期"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_get_current_user_inactive_account(self, mock_auth_service):
        """測試停用的帳號"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        inactive_user = Mock(spec=User)
        inactive_user.is_active = False
        mock_auth_service.get_current_user.return_value = inactive_user
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, mock_auth_service)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "帳號已被停用"

    def test_get_current_user_optional_no_credentials(self, mock_auth_service):
        """測試可選使用者 - 無認證資訊"""
        result = get_current_user_optional(None, mock_auth_service)
        
        assert result is None
        mock_auth_service.get_current_user.assert_not_called()

    def test_get_current_user_optional_valid_user(self, mock_auth_service, sample_user):
        """測試可選使用者 - 有效使用者"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_auth_service.get_current_user.return_value = sample_user
        
        result = get_current_user_optional(credentials, mock_auth_service)
        
        assert result == sample_user
        mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    def test_get_current_user_optional_invalid_token(self, mock_auth_service):
        """測試可選使用者 - 無效 Token"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        mock_auth_service.get_current_user.return_value = None
        
        result = get_current_user_optional(credentials, mock_auth_service)
        
        assert result is None
        mock_auth_service.get_current_user.assert_called_once_with("invalid_token")

    def test_get_current_user_optional_inactive_user(self, mock_auth_service):
        """測試可選使用者 - 停用使用者"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        inactive_user = Mock(spec=User)
        inactive_user.is_active = False
        mock_auth_service.get_current_user.return_value = inactive_user
        
        result = get_current_user_optional(credentials, mock_auth_service)
        
        assert result is None
        mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    def test_get_current_user_optional_unverified_user(self, mock_auth_service):
        """測試可選使用者 - 未驗證使用者"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        unverified_user = Mock(spec=User)
        unverified_user.is_active = True
        unverified_user.is_verified = False
        mock_auth_service.get_current_user.return_value = unverified_user
        
        result = get_current_user_optional(credentials, mock_auth_service)
        
        assert result == unverified_user
        mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    def test_security_configuration(self):
        """測試安全性設定"""
        assert security is not None
        assert security.scheme_name == "HTTPBearer"
        assert security.auto_error is False

    def test_get_current_user_different_schemes(self, mock_auth_service, sample_user):
        """測試不同認證方案"""
        # 測試 Bearer 方案
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_auth_service.get_current_user.return_value = sample_user
        
        result = get_current_user(credentials, mock_auth_service)
        
        assert result == sample_user
        mock_auth_service.get_current_user.assert_called_once_with("valid_token")

    def test_get_current_user_empty_token(self, mock_auth_service):
        """測試空 Token"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        mock_auth_service.get_current_user.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, mock_auth_service)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Token 無效或已過期"

    def test_get_current_user_optional_empty_token(self, mock_auth_service):
        """測試可選使用者 - 空 Token"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        mock_auth_service.get_current_user.return_value = None
        
        result = get_current_user_optional(credentials, mock_auth_service)
        
        assert result is None
        mock_auth_service.get_current_user.assert_called_once_with("")

    def test_get_current_user_auth_service_exception(self, mock_auth_service):
        """測試認證服務拋出異常"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_auth_service.get_current_user.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            get_current_user(credentials, mock_auth_service)
        
        assert str(exc_info.value) == "Database error"

    def test_get_current_user_optional_auth_service_exception(self, mock_auth_service):
        """測試可選使用者 - 認證服務拋出異常"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_auth_service.get_current_user.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            get_current_user_optional(credentials, mock_auth_service)
        
        assert str(exc_info.value) == "Database error"

    def test_get_current_user_verified_user(self, mock_auth_service):
        """測試已驗證使用者"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        verified_user = Mock(spec=User)
        verified_user.is_active = True
        verified_user.is_verified = True
        mock_auth_service.get_current_user.return_value = verified_user
        
        result = get_current_user(credentials, mock_auth_service)
        
        assert result == verified_user
        assert result.is_active is True
        assert result.is_verified is True

    def test_get_current_user_optional_verified_user(self, mock_auth_service):
        """測試可選使用者 - 已驗證使用者"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        verified_user = Mock(spec=User)
        verified_user.is_active = True
        verified_user.is_verified = True
        mock_auth_service.get_current_user.return_value = verified_user
        
        result = get_current_user_optional(credentials, mock_auth_service)
        
        assert result == verified_user
        assert result.is_active is True
        assert result.is_verified is True
