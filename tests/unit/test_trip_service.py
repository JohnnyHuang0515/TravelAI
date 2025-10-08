"""
行程服務單元測試
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from uuid import uuid4

from src.itinerary_planner.application.services.trip_service import TripService
from tests.test_orm_models import Trip as UserTrip


class TestTripService:
    """行程服務測試類別"""
    
    @pytest.fixture
    def trip_service(self, mock_db_session):
        """建立行程服務實例"""
        return TripService(mock_db_session)
    
    @pytest.fixture
    def sample_itinerary_data(self):
        """測試用的行程資料"""
        return {
            'days': [
                {
                    'date': '2025-02-01',
                    'places': [
                        {'name': '台北101', 'start_time': '09:00', 'end_time': '11:00'},
                        {'name': '鼎泰豐', 'start_time': '12:00', 'end_time': '14:00'}
                    ]
                },
                {
                    'date': '2025-02-02',
                    'places': [
                        {'name': '西門町', 'start_time': '10:00', 'end_time': '12:00'}
                    ]
                }
            ]
        }
    
    @pytest.fixture
    def sample_trip(self):
        """測試用的行程物件"""
        trip = Mock(spec=UserTrip)
        trip.id = str(uuid4())
        trip.user_id = str(uuid4())
        trip.title = "台北兩日遊"
        trip.description = "測試行程"
        trip.destination = "台北"
        trip.duration_days = 2
        trip.start_date = datetime(2025, 2, 1)
        trip.end_date = datetime(2025, 2, 2)
        trip.itinerary_data = {'days': []}
        trip.is_public = False
        trip.share_token = None
        trip.view_count = 0
        return trip
    
    def test_save_trip_success(self, trip_service, sample_itinerary_data):
        """測試成功儲存行程"""
        # Mock repository
        mock_trip = Mock(spec=UserTrip)
        mock_trip.id = str(uuid4())
        mock_trip.title = "台北兩日遊"
        
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.create_trip.return_value = mock_trip
        
        # 執行測試
        result = trip_service.save_trip(
            user_id=str(uuid4()),
            title="台北兩日遊",
            destination="台北",
            itinerary_data=sample_itinerary_data,
            description="測試行程",
            is_public=False
        )
        
        # 驗證結果
        assert result == mock_trip
        trip_service.trip_repo.create_trip.assert_called_once()
        
        # 驗證參數
        call_args = trip_service.trip_repo.create_trip.call_args
        assert call_args[1]['title'] == "台北兩日遊"
        assert call_args[1]['destination'] == "台北"
        assert call_args[1]['duration_days'] == 2
        assert call_args[1]['start_date'] == '2025-02-01'
        assert call_args[1]['end_date'] == '2025-02-02'
        assert call_args[1]['is_public'] == False
    
    def test_save_trip_empty_days(self, trip_service):
        """測試儲存空行程"""
        # Mock repository
        mock_trip = Mock(spec=UserTrip)
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.create_trip.return_value = mock_trip
        
        # 執行測試
        result = trip_service.save_trip(
            user_id=str(uuid4()),
            title="空行程",
            destination="台北",
            itinerary_data={'days': []}
        )
        
        # 驗證結果
        assert result == mock_trip
        call_args = trip_service.trip_repo.create_trip.call_args
        assert call_args[1]['duration_days'] == 0
        assert call_args[1]['start_date'] is None
        assert call_args[1]['end_date'] is None
    
    def test_get_user_trips_success(self, trip_service):
        """測試成功取得使用者行程列表"""
        # Mock repository
        mock_trips = [Mock(spec=UserTrip), Mock(spec=UserTrip)]
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_user_trips.return_value = mock_trips
        trip_service.trip_repo.count_user_trips.return_value = 25
        
        # 執行測試
        result = trip_service.get_user_trips(
            user_id=str(uuid4()),
            page=2,
            page_size=10
        )
        
        # 驗證結果
        assert result['trips'] == mock_trips
        assert result['total'] == 25
        assert result['page'] == 2
        assert result['page_size'] == 10
        assert result['total_pages'] == 3
        
        # 驗證 repository 呼叫
        call_args = trip_service.trip_repo.get_user_trips.call_args
        assert call_args[0][1] == 10  # skip
        assert call_args[0][2] == 10  # page_size
        trip_service.trip_repo.count_user_trips.assert_called_once()
    
    def test_get_trip_success_owner(self, trip_service, sample_trip):
        """測試成功取得自己的行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試
        result = trip_service.get_trip(
            trip_id=sample_trip.id,
            user_id=sample_trip.user_id
        )
        
        # 驗證結果
        assert result == sample_trip
    
    def test_get_trip_success_public(self, trip_service, sample_trip):
        """測試成功取得公開行程"""
        # 設定為公開行程
        sample_trip.is_public = True
        
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（未登入）
        result = trip_service.get_trip(trip_id=sample_trip.id)
        
        # 驗證結果
        assert result == sample_trip
    
    def test_get_trip_not_found(self, trip_service):
        """測試取得不存在的行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = None
        
        # 執行測試
        result = trip_service.get_trip(trip_id=str(uuid4()))
        
        # 驗證結果
        assert result is None
    
    def test_get_trip_permission_denied(self, trip_service, sample_trip):
        """測試權限不足"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（不同使用者）
        result = trip_service.get_trip(
            trip_id=sample_trip.id,
            user_id=str(uuid4())  # 不同的使用者 ID
        )
        
        # 驗證結果
        assert result is None
    
    def test_get_trip_private_not_logged_in(self, trip_service, sample_trip):
        """測試未登入無法取得私人行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（未登入）
        result = trip_service.get_trip(trip_id=sample_trip.id)
        
        # 驗證結果
        assert result is None
    
    def test_update_trip_success(self, trip_service, sample_trip):
        """測試成功更新行程"""
        # Mock repository
        updated_trip = Mock(spec=UserTrip)
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        trip_service.trip_repo.update_trip.return_value = updated_trip
        
        # 執行測試
        result = trip_service.update_trip(
            trip_id=sample_trip.id,
            user_id=sample_trip.user_id,
            title="更新後的標題",
            description="更新後的描述"
        )
        
        # 驗證結果
        assert result == updated_trip
        trip_service.trip_repo.update_trip.assert_called_once_with(
            sample_trip.id,
            title="更新後的標題",
            description="更新後的描述"
        )
    
    def test_update_trip_not_found(self, trip_service):
        """測試更新不存在的行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = None
        
        # 執行測試
        result = trip_service.update_trip(
            trip_id=str(uuid4()),
            user_id=str(uuid4()),
            title="新標題"
        )
        
        # 驗證結果
        assert result is None
    
    def test_update_trip_permission_denied(self, trip_service, sample_trip):
        """測試權限不足無法更新"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（不同使用者）
        result = trip_service.update_trip(
            trip_id=sample_trip.id,
            user_id=str(uuid4()),  # 不同的使用者 ID
            title="新標題"
        )
        
        # 驗證結果
        assert result is None
    
    def test_delete_trip_success(self, trip_service, sample_trip):
        """測試成功刪除行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        trip_service.trip_repo.delete_trip.return_value = True
        
        # 執行測試
        result = trip_service.delete_trip(
            trip_id=sample_trip.id,
            user_id=sample_trip.user_id
        )
        
        # 驗證結果
        assert result is True
        trip_service.trip_repo.delete_trip.assert_called_once_with(sample_trip.id)
    
    def test_delete_trip_not_found(self, trip_service):
        """測試刪除不存在的行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = None
        
        # 執行測試
        result = trip_service.delete_trip(
            trip_id=str(uuid4()),
            user_id=str(uuid4())
        )
        
        # 驗證結果
        assert result is False
    
    def test_delete_trip_permission_denied(self, trip_service, sample_trip):
        """測試權限不足無法刪除"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（不同使用者）
        result = trip_service.delete_trip(
            trip_id=sample_trip.id,
            user_id=str(uuid4())  # 不同的使用者 ID
        )
        
        # 驗證結果
        assert result is False
    
    def test_share_trip_success_new_token(self, trip_service, sample_trip):
        """測試成功分享行程（生成新 token）"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        trip_service.trip_repo.generate_share_token.return_value = "new_share_token"
        
        # 執行測試
        result = trip_service.share_trip(
            trip_id=sample_trip.id,
            user_id=sample_trip.user_id
        )
        
        # 驗證結果
        assert result == "new_share_token"
        trip_service.trip_repo.generate_share_token.assert_called_once_with(sample_trip.id)
    
    def test_share_trip_success_existing_token(self, trip_service, sample_trip):
        """測試成功分享行程（使用現有 token）"""
        # 設定現有的 share_token
        sample_trip.share_token = "existing_share_token"
        
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試
        result = trip_service.share_trip(
            trip_id=sample_trip.id,
            user_id=sample_trip.user_id
        )
        
        # 驗證結果
        assert result == "existing_share_token"
        # 不應該呼叫 generate_share_token
        trip_service.trip_repo.generate_share_token.assert_not_called()
    
    def test_share_trip_not_found(self, trip_service):
        """測試分享不存在的行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = None
        
        # 執行測試
        result = trip_service.share_trip(
            trip_id=str(uuid4()),
            user_id=str(uuid4())
        )
        
        # 驗證結果
        assert result is None
    
    def test_share_trip_permission_denied(self, trip_service, sample_trip):
        """測試權限不足無法分享"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（不同使用者）
        result = trip_service.share_trip(
            trip_id=sample_trip.id,
            user_id=str(uuid4())  # 不同的使用者 ID
        )
        
        # 驗證結果
        assert result is None
    
    def test_get_public_trip_success(self, trip_service, sample_trip):
        """測試成功取得公開行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_share_token.return_value = sample_trip
        trip_service.trip_repo.increment_view_count.return_value = None
        
        # 執行測試
        result = trip_service.get_public_trip(share_token="test_token")
        
        # 驗證結果
        assert result == sample_trip
        trip_service.trip_repo.get_by_share_token.assert_called_once_with("test_token")
        trip_service.trip_repo.increment_view_count.assert_called_once_with(sample_trip.id)
    
    def test_get_public_trip_not_found(self, trip_service):
        """測試取得不存在的公開行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_share_token.return_value = None
        
        # 執行測試
        result = trip_service.get_public_trip(share_token="invalid_token")
        
        # 驗證結果
        assert result is None
        trip_service.trip_repo.increment_view_count.assert_not_called()
    
    def test_copy_trip_success_public(self, trip_service, sample_trip):
        """測試成功複製公開行程"""
        # 設定為公開行程
        sample_trip.is_public = True
        
        # Mock repository
        copied_trip = Mock(spec=UserTrip)
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        trip_service.trip_repo.copy_trip.return_value = copied_trip
        
        # 執行測試
        result = trip_service.copy_trip(
            trip_id=sample_trip.id,
            new_user_id=str(uuid4()),
            new_title="複製的行程"
        )
        
        # 驗證結果
        assert result == copied_trip
        call_args = trip_service.trip_repo.copy_trip.call_args
        assert call_args[0][0] == sample_trip.id
        assert call_args[0][2] == "複製的行程"
    
    def test_copy_trip_success_own(self, trip_service, sample_trip):
        """測試成功複製自己的行程"""
        # Mock repository
        copied_trip = Mock(spec=UserTrip)
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        trip_service.trip_repo.copy_trip.return_value = copied_trip
        
        # 執行測試（複製自己的行程）
        result = trip_service.copy_trip(
            trip_id=sample_trip.id,
            new_user_id=sample_trip.user_id,
            new_title="複製的行程"
        )
        
        # 驗證結果
        assert result == copied_trip
    
    def test_copy_trip_not_found(self, trip_service):
        """測試複製不存在的行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = None
        
        # 執行測試
        result = trip_service.copy_trip(
            trip_id=str(uuid4()),
            new_user_id=str(uuid4())
        )
        
        # 驗證結果
        assert result is None
    
    def test_copy_trip_permission_denied(self, trip_service, sample_trip):
        """測試權限不足無法複製私人行程"""
        # Mock repository
        trip_service.trip_repo = Mock()
        trip_service.trip_repo.get_by_id.return_value = sample_trip
        
        # 執行測試（複製別人的私人行程）
        result = trip_service.copy_trip(
            trip_id=sample_trip.id,
            new_user_id=str(uuid4())  # 不同的使用者 ID
        )
        
        # 驗證結果
        assert result is None
