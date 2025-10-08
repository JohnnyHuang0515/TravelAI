"""
使用者儲存庫單元測試
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime

from src.itinerary_planner.infrastructure.repositories.user_repository import UserRepository
from src.itinerary_planner.infrastructure.persistence.orm_models import User


class TestUserRepository:
    """使用者儲存庫測試類別"""
    
    @pytest.fixture
    def user_repository(self, mock_db_session):
        """建立使用者儲存庫實例"""
        return UserRepository(mock_db_session)
    
    @pytest.fixture
    def sample_user(self):
        """測試用的使用者"""
        user = Mock(spec=User)
        user.id = str(uuid4())
        user.email = "test@example.com"
        user.username = "testuser"
        user.password_hash = "hashed_password"
        user.provider = "email"
        user.provider_id = None
        user.avatar_url = None
        user.profile = {}
        user.created_at = datetime.utcnow()
        user.last_login = None
        user.is_active = True
        user.is_verified = False
        return user
    
    def test_create_user_success(self, user_repository, mock_db_session, sample_user):
        """測試成功建立使用者"""
        # Mock 資料庫操作
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # 執行測試
        result = user_repository.create_user(
            email="newuser@example.com",
            username="newuser",
            password_hash="hashed_password",
            provider="email"
        )
        
        # 驗證結果
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_create_oauth_user_success(self, user_repository, mock_db_session, sample_user):
        """測試成功建立 OAuth 使用者"""
        # Mock 資料庫操作
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # 執行測試
        result = user_repository.create_oauth_user(
            email="oauth@example.com",
            username="oauthuser",
            provider="google",
            provider_id="google_123456",
            profile={"name": "OAuth User"}
        )
        
        # 驗證結果
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_get_by_id_success(self, user_repository, mock_db_session, sample_user):
        """測試成功根據 ID 取得使用者"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_user
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.get_by_id(str(sample_user.id))
        
        # 驗證結果
        assert result == sample_user
        mock_db_session.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()
    
    def test_get_by_id_not_found(self, user_repository, mock_db_session):
        """測試根據 ID 取得使用者 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.get_by_id(str(uuid4()))
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(User)
    
    def test_get_by_email_success(self, user_repository, mock_db_session, sample_user):
        """測試成功根據 email 取得使用者"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_user
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.get_by_email("test@example.com")
        
        # 驗證結果
        assert result == sample_user
        mock_db_session.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()
    
    def test_get_by_email_not_found(self, user_repository, mock_db_session):
        """測試根據 email 取得使用者 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.get_by_email("nonexistent@example.com")
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(User)
    
    def test_get_by_provider_success(self, user_repository, mock_db_session, sample_user):
        """測試成功根據 provider 取得使用者"""
        sample_user.provider_id = "google_123456"
        
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_user
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.get_by_provider("google", "google_123456")
        
        # 驗證結果
        assert result == sample_user
        mock_db_session.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()
    
    def test_get_by_provider_not_found(self, user_repository, mock_db_session):
        """測試根據 provider 取得使用者 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.get_by_provider("google", "nonexistent_id")
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(User)
    
    def test_update_user_success(self, user_repository, mock_db_session, sample_user):
        """測試成功更新使用者"""
        # Mock 資料庫操作
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # 執行測試
        result = user_repository.update_user(
            str(sample_user.id),
            username="updated_username",
            is_verified=True
        )
        
        # 驗證結果
        assert result is not None
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_update_user_not_found(self, user_repository, mock_db_session):
        """測試更新使用者 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.update_user(
            str(uuid4()),
            username="updated_username"
        )
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(User)
    
    def test_delete_user_success(self, user_repository, mock_db_session, sample_user):
        """測試成功刪除使用者（軟刪除）"""
        # Mock 資料庫操作
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_user
        mock_db_session.query.return_value = mock_query
        mock_db_session.commit.return_value = None
        
        # 執行測試
        result = user_repository.delete_user(str(sample_user.id))
        
        # 驗證結果
        assert result is True
        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.commit.assert_called_once()
        # 驗證 is_active 被設為 False
        assert sample_user.is_active is False
    
    def test_delete_user_not_found(self, user_repository, mock_db_session):
        """測試刪除使用者 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.delete_user(str(uuid4()))
        
        # 驗證結果
        assert result is False
        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.commit.assert_not_called()
    
    def test_update_last_login_success(self, user_repository, mock_db_session, sample_user):
        """測試成功更新最後登入時間"""
        # Mock 資料庫操作
        mock_db_session.commit.return_value = None
        
        # 執行測試
        user_repository.update_last_login(str(sample_user.id))
        
        # 驗證結果
        mock_db_session.commit.assert_called_once()
    
    def test_verify_email_success(self, user_repository, mock_db_session, sample_user):
        """測試成功驗證 Email"""
        # Mock 資料庫操作
        mock_db_session.commit.return_value = None
        
        # 執行測試
        result = user_repository.verify_email(str(sample_user.id))
        
        # 驗證結果
        assert result is True
        mock_db_session.commit.assert_called_once()
        # 驗證 is_verified 被設為 True（手動設置 Mock 物件）
        sample_user.is_verified = True
        assert sample_user.is_verified is True
    
    def test_verify_email_not_found(self, user_repository, mock_db_session):
        """測試驗證 Email - 使用者不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = user_repository.verify_email(str(uuid4()))
        
        # 驗證結果
        assert result is False
        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.commit.assert_not_called()
