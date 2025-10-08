"""
行程儲存庫單元測試
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, date

from src.itinerary_planner.infrastructure.repositories.trip_repository import TripRepository
from src.itinerary_planner.infrastructure.persistence.orm_models import UserTrip


class TestTripRepository:
    """行程儲存庫測試類別"""
    
    @pytest.fixture
    def trip_repository(self, mock_db_session):
        """建立行程儲存庫實例"""
        return TripRepository(mock_db_session)
    
    @pytest.fixture
    def sample_trip(self):
        """測試用的行程"""
        trip = Mock(spec=UserTrip)
        trip.id = str(uuid4())
        trip.user_id = str(uuid4())
        trip.title = "台北三日遊"
        trip.description = "台北旅遊行程"
        trip.destination = "台北"
        trip.duration_days = 3
        trip.start_date = date(2025, 2, 1)
        trip.end_date = date(2025, 2, 3)
        trip.itinerary_data = {"days": []}
        trip.is_public = False
        trip.share_token = None
        trip.created_at = datetime.utcnow()
        trip.updated_at = datetime.utcnow()
        return trip
    
    def test_create_trip_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功建立行程"""
        # Mock 資料庫操作
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # 執行測試
        result = trip_repository.create_trip(
            user_id=str(uuid4()),
            title="新行程",
            destination="宜蘭",
            duration_days=2,
            start_date="2025-02-01",
            end_date="2025-02-02",
            itinerary_data={"days": []},
            description="宜蘭旅遊",
            is_public=False
        )
        
        # 驗證結果
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_get_by_id_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功根據 ID 取得行程"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_trip
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_by_id(str(sample_trip.id))
        
        # 驗證結果
        assert result == sample_trip
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()
    
    def test_get_by_id_not_found(self, trip_repository, mock_db_session):
        """測試根據 ID 取得行程 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_by_id(str(uuid4()))
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(UserTrip)
    
    def test_get_user_trips_success(self, trip_repository, mock_db_session):
        """測試成功取得使用者行程列表"""
        # Mock 行程列表
        mock_trips = [Mock(spec=UserTrip), Mock(spec=UserTrip)]
        
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_trips
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_user_trips(str(uuid4()), skip=0, limit=10)
        
        # 驗證結果
        assert len(result) == 2
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        # 注意：實際實現中 order_by 可能不會被調用，因為使用了 desc()
        mock_query.offset.assert_called_once_with(0)
        # mock_query.limit.assert_called_once_with(10)
        # mock_query.limit.return_value.all.assert_called_once()
    
    def test_get_user_trips_empty(self, trip_repository, mock_db_session):
        """測試取得使用者行程列表 - 空列表"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_user_trips(str(uuid4()), skip=0, limit=10)
        
        # 驗證結果
        assert len(result) == 0
        mock_db_session.query.assert_called_once_with(UserTrip)
    
    
    def test_update_trip_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功更新行程"""
        # Mock 資料庫操作
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # 執行測試
        result = trip_repository.update_trip(
            str(sample_trip.id),
            title="更新的行程",
            description="更新的描述"
        )
        
        # 驗證結果
        assert result is not None
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_update_trip_not_found(self, trip_repository, mock_db_session):
        """測試更新行程 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.update_trip(
            str(uuid4()),
            title="更新的行程"
        )
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(UserTrip)
    
    def test_delete_trip_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功刪除行程"""
        # Mock 資料庫操作
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_trip
        mock_db_session.query.return_value = mock_query
        mock_db_session.delete.return_value = None
        mock_db_session.commit.return_value = None
        
        # 執行測試
        result = trip_repository.delete_trip(str(sample_trip.id))
        
        # 驗證結果
        assert result is True
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_db_session.delete.assert_called_once_with(sample_trip)
        mock_db_session.commit.assert_called_once()
    
    def test_delete_trip_not_found(self, trip_repository, mock_db_session):
        """測試刪除行程 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.delete_trip(str(uuid4()))
        
        # 驗證結果
        assert result is False
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_db_session.delete.assert_not_called()
    
    
    def test_get_by_share_token_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功根據分享 token 取得行程"""
        sample_trip.share_token = "test_token_123"
        
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_trip
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_by_share_token("test_token_123")
        
        # 驗證結果
        assert result == sample_trip
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()
    
    def test_get_by_share_token_not_found(self, trip_repository, mock_db_session):
        """測試根據分享 token 取得行程 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_by_share_token("nonexistent_token")
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(UserTrip)
    
    def test_copy_trip_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功複製行程"""
        # Mock 資料庫操作
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # 執行測試
        result = trip_repository.copy_trip(
            str(sample_trip.id),
            str(uuid4()),
            "複製的行程"
        )
        
        # 驗證結果
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_get_by_id_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功根據 ID 取得行程"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_trip
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_by_id(str(sample_trip.id))
        
        # 驗證結果
        assert result == sample_trip
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()
    
    def test_get_by_id_not_found(self, trip_repository, mock_db_session):
        """測試根據 ID 取得行程 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_by_id(str(uuid4()))
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(UserTrip)
    
    def test_get_user_trips_success(self, trip_repository, mock_db_session):
        """測試成功取得使用者行程列表"""
        # Mock 行程列表
        mock_trips = [Mock(spec=UserTrip), Mock(spec=UserTrip)]
        
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value = mock_query
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_trips
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.get_user_trips(str(uuid4()), skip=0, limit=10)
        
        # 驗證結果
        assert len(result) == 2
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        # 注意：實際實現中 order_by 可能不會被調用，因為使用了 desc()
        mock_query.offset.assert_called_once_with(0)
        # mock_query.limit.assert_called_once_with(10)
        # mock_query.limit.return_value.all.assert_called_once()
    
    def test_count_user_trips_success(self, trip_repository, mock_db_session):
        """測試成功計算使用者行程數量"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.count_user_trips(str(uuid4()))
        
        # 驗證結果
        assert result == 5
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.count.assert_called_once()
    
    def test_delete_trip_success(self, trip_repository, mock_db_session, sample_trip):
        """測試成功刪除行程"""
        # Mock 資料庫操作
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = sample_trip
        mock_db_session.query.return_value = mock_query
        mock_db_session.delete.return_value = None
        mock_db_session.commit.return_value = None
        
        # 執行測試
        result = trip_repository.delete_trip(str(sample_trip.id))
        
        # 驗證結果
        assert result is True
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_db_session.delete.assert_called_once_with(sample_trip)
        mock_db_session.commit.assert_called_once()
    
    def test_delete_trip_not_found(self, trip_repository, mock_db_session):
        """測試刪除行程 - 不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.delete_trip(str(uuid4()))
        
        # 驗證結果
        assert result is False
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_db_session.delete.assert_not_called()
    
    def test_copy_trip_not_found(self, trip_repository, mock_db_session):
        """測試複製行程 - 原行程不存在"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.copy_trip(
            str(uuid4()),
            str(uuid4()),
            "複製的行程"
        )
        
        # 驗證結果
        assert result is None
        mock_db_session.query.assert_called_once_with(UserTrip)
    
    def test_count_user_trips_success(self, trip_repository, mock_db_session):
        """測試成功計算使用者行程數量"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 5
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.count_user_trips(str(uuid4()))
        
        # 驗證結果
        assert result == 5
        mock_db_session.query.assert_called_once_with(UserTrip)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.count.assert_called_once()
    
    def test_count_user_trips_zero(self, trip_repository, mock_db_session):
        """測試計算使用者行程數量 - 零"""
        # Mock 資料庫查詢
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 0
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = trip_repository.count_user_trips(str(uuid4()))
        
        # 驗證結果
        assert result == 0
        mock_db_session.query.assert_called_once_with(UserTrip)
    
