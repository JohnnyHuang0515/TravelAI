"""
住宿儲存庫單元測試
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from src.itinerary_planner.infrastructure.repositories.postgres_accommodation_repo import PostgresAccommodationRepository
from src.itinerary_planner.infrastructure.persistence.orm_models import Accommodation as OrmAccommodation


class TestPostgresAccommodationRepository:
    """住宿儲存庫測試類別"""
    
    @pytest.fixture
    def accommodation_repository(self, mock_db_session):
        """建立住宿儲存庫實例"""
        return PostgresAccommodationRepository(mock_db_session)
    
    @pytest.fixture
    def sample_accommodation(self):
        """測試用的住宿"""
        accommodation = Mock(spec=OrmAccommodation)
        accommodation.id = str(uuid4())
        accommodation.name = "台北君悅酒店"
        accommodation.type = "hotel"
        accommodation.rating = 4.5
        accommodation.price_range = [3000, 5000]
        accommodation.eco_friendly = True
        accommodation.geom = "POINT(121.5654 25.0330)"
        return accommodation
    
    def test_search_by_location_success(self, accommodation_repository, mock_db_session):
        """測試根據位置搜尋住宿成功"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation), Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            lat=25.0330,
            lon=121.5654,
            radius=5000
        )
        
        # 驗證結果
        assert len(result) == 2
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_by_type_success(self, accommodation_repository, mock_db_session):
        """測試根據類型搜尋住宿成功"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            accommodation_type="hotel"
        )
        
        # 驗證結果
        assert len(result) == 1
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_by_rating_success(self, accommodation_repository, mock_db_session):
        """測試根據評分搜尋住宿成功"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation), Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            min_rating=4.0
        )
        
        # 驗證結果
        assert len(result) == 2
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_by_budget_success(self, accommodation_repository, mock_db_session):
        """測試根據預算搜尋住宿成功"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            budget_range=[2000, 4000]
        )
        
        # 驗證結果
        assert len(result) == 1
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_eco_friendly_success(self, accommodation_repository, mock_db_session):
        """測試搜尋環保住宿成功"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            eco_friendly=True
        )
        
        # 驗證結果
        assert len(result) == 1
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_combined_filters_success(self, accommodation_repository, mock_db_session):
        """測試組合條件搜尋住宿成功"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            lat=25.0330,
            lon=121.5654,
            radius=5000,
            accommodation_type="hotel",
            min_rating=4.0,
            budget_range=[3000, 5000],
            eco_friendly=True
        )
        
        # 驗證結果
        assert len(result) == 1
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        # 組合條件會調用多次 filter
        assert mock_query.filter.call_count >= 1
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_no_results(self, accommodation_repository, mock_db_session):
        """測試搜尋住宿無結果"""
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用
        mock_query.limit.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search(
            accommodation_type="nonexistent_type"
        )
        
        # 驗證結果
        assert len(result) == 0
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
    def test_search_no_filters(self, accommodation_repository, mock_db_session):
        """測試無條件搜尋住宿"""
        # Mock 住宿列表
        mock_accommodations = [Mock(spec=OrmAccommodation), Mock(spec=OrmAccommodation), Mock(spec=OrmAccommodation)]
        
        # Mock 資料庫查詢鏈
        mock_query = Mock()
        mock_query.limit.return_value.all.return_value = mock_accommodations
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = accommodation_repository.search()
        
        # 驗證結果
        assert len(result) == 3
        mock_db_session.query.assert_called_once_with(OrmAccommodation)
        mock_query.limit.assert_called_once_with(20)
        mock_query.limit.return_value.all.assert_called_once()
    
