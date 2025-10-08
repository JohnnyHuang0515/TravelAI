"""
住宿服務單元測試
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from src.itinerary_planner.application.services.accommodation_service import AccommodationPlanner
from src.itinerary_planner.domain.models.story import Story, AccommodationPreference
from src.itinerary_planner.domain.models.itinerary import Accommodation
from src.itinerary_planner.infrastructure.persistence.orm_models import Accommodation as OrmAccommodation


class TestAccommodationPlanner:
    """住宿規劃服務測試類別"""
    
    @pytest.fixture
    def accommodation_planner(self):
        """建立住宿規劃服務實例"""
        return AccommodationPlanner()
    
    @pytest.fixture
    def sample_story_with_accommodation(self):
        """測試用的故事（包含住宿偏好）"""
        from src.itinerary_planner.domain.models.story import Preference
        
        accommodation_pref = AccommodationPreference(
            type="hotel",
            budget_range=(2000, 5000),
            location_preference="city_center"
        )
        
        preference = Preference(
            themes=["文化", "歷史"],
            travel_pace="moderate",
            budget_level="medium"
        )
        
        return Story(
            days=3,
            preference=preference,
            accommodation=accommodation_pref
        )
    
    @pytest.fixture
    def sample_story_without_accommodation(self):
        """測試用的故事（不包含住宿偏好）"""
        from src.itinerary_planner.domain.models.story import Preference
        
        preference = Preference(
            themes=["文化", "歷史"],
            travel_pace="moderate",
            budget_level="medium"
        )
        
        return Story(
            days=3,
            preference=preference,
            accommodation=None
        )
    
    @pytest.fixture
    def sample_accommodation(self):
        """測試用的住宿"""
        from datetime import time
        
        accommodation = Mock(spec=OrmAccommodation)
        accommodation.id = str(uuid4())
        accommodation.name = "台北君悅酒店"
        accommodation.type = "hotel"
        accommodation.rating = 4.5
        accommodation.price_range = 3500
        accommodation.geom = "POINT(121.5654 25.0330)"
        accommodation.check_in_time = time(15, 0)  # 15:00
        accommodation.check_out_time = time(11, 0)  # 11:00
        return accommodation
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_success(self, mock_session_local, accommodation_planner, 
                                        sample_story_with_accommodation, sample_accommodation):
        """測試成功選擇住宿"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_accommodation
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_with_accommodation,
            [(25.0330, 121.5654), (25.0400, 121.5700)]
        )
        
        # 驗證結果
        assert result is not None
        assert isinstance(result, Accommodation)
        mock_session_local.assert_called_once()
        mock_db.query.assert_called_once_with(OrmAccommodation)
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_no_preference(self, mock_session_local, accommodation_planner,
                                              sample_story_without_accommodation):
        """測試沒有住宿偏好時返回 None"""
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_without_accommodation,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is None
        mock_session_local.assert_not_called()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_no_results(self, mock_session_local, accommodation_planner,
                                           sample_story_with_accommodation):
        """測試沒有找到合適住宿時返回 None"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_with_accommodation,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is None
        mock_session_local.assert_called_once()
        mock_db.query.assert_called_once_with(OrmAccommodation)
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_with_budget_filter(self, mock_session_local, accommodation_planner,
                                                   sample_story_with_accommodation, sample_accommodation):
        """測試使用預算篩選選擇住宿"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_accommodation
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_with_accommodation,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is not None
        # 驗證預算篩選被調用
        assert mock_query.filter.call_count >= 2  # 至少調用兩次 filter（預算和評分）
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_with_type_filter(self, mock_session_local, accommodation_planner,
                                                 sample_story_with_accommodation, sample_accommodation):
        """測試使用類型篩選選擇住宿"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_accommodation
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_with_accommodation,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is not None
        # 驗證類型篩選被調用
        assert mock_query.filter.call_count >= 2  # 至少調用兩次 filter（類型和評分）
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_database_error(self, mock_session_local, accommodation_planner,
                                               sample_story_with_accommodation):
        """測試資料庫錯誤時的處理"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢錯誤
        mock_db.query.side_effect = Exception("Database error")
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_with_accommodation,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is None
        mock_session_local.assert_called_once()
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_empty_locations(self, mock_session_local, accommodation_planner,
                                                sample_story_with_accommodation, sample_accommodation):
        """測試空景點位置列表時的處理"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_accommodation
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            sample_story_with_accommodation,
            []
        )
        
        # 驗證結果
        assert result is not None
        mock_session_local.assert_called_once()
        mock_db.query.assert_called_once_with(OrmAccommodation)
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_any_type(self, mock_session_local, accommodation_planner, sample_accommodation):
        """測試住宿類型為 'any' 時的處理"""
        # 建立故事，住宿類型為 'any'
        from src.itinerary_planner.domain.models.story import Preference
        
        accommodation_pref = AccommodationPreference(
            type="any",
            budget_range=(2000, 5000),
            location_preference="city_center"
        )
        
        preference = Preference(
            themes=["文化", "歷史"],
            travel_pace="moderate",
            budget_level="medium"
        )
        
        story = Story(
            days=3,
            preference=preference,
            accommodation=accommodation_pref
        )
        
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_accommodation
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            story,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is not None
        # 驗證類型篩選沒有被調用（因為類型是 'any'）
        mock_db.close.assert_called_once()
    
    @patch('src.itinerary_planner.application.services.accommodation_service.SessionLocal')
    def test_select_accommodation_no_budget_range(self, mock_session_local, accommodation_planner, sample_accommodation):
        """測試沒有預算範圍時的處理"""
        # 建立故事，沒有預算範圍
        from src.itinerary_planner.domain.models.story import Preference
        
        accommodation_pref = AccommodationPreference(
            type="hotel",
            budget_range=None,
            location_preference="city_center"
        )
        
        preference = Preference(
            themes=["文化", "歷史"],
            travel_pace="moderate",
            budget_level="medium"
        )
        
        story = Story(
            days=3,
            preference=preference,
            accommodation=accommodation_pref
        )
        
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session_local.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = sample_accommodation
        mock_db.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_planner.select_accommodation(
            story,
            [(25.0330, 121.5654)]
        )
        
        # 驗證結果
        assert result is not None
        mock_db.close.assert_called_once()
