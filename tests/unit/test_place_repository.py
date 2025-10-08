"""
景點儲存庫單元測試
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.itinerary_planner.infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
from tests.test_orm_models import Place as OrmPlace, Hour as OrmHour


class TestPostgresPlaceRepository:
    """景點儲存庫測試類別"""
    
    @pytest.fixture
    def place_repository(self, mock_db_session):
        """建立景點儲存庫實例"""
        return PostgresPlaceRepository(mock_db_session)
    
    def test_search_success(self, place_repository, mock_db_session):
        """測試搜尋景點成功"""
        # Mock 資料庫查詢結果
        mock_place1 = Mock(spec=OrmPlace)
        mock_place1.id = "place-1"
        mock_place1.name = "台北101"
        mock_place1.categories = ["景點", "購物"]
        mock_place1.rating = 4.5
        
        mock_place2 = Mock(spec=OrmPlace)
        mock_place2.id = "place-2"
        mock_place2.name = "西門町"
        mock_place2.categories = ["景點", "購物"]
        mock_place2.rating = 4.2
        
        mock_places = [mock_place1, mock_place2]
        
        # 設定 Mock 鏈式調用 - 直接返回結果
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用返回自己
        mock_query.limit.return_value = mock_query   # 鏈式調用返回自己
        mock_query.all.return_value = mock_places    # 最終返回結果
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = place_repository.search(
            lat=25.0330,
            lon=121.5654,
            radius=5000,
            categories=["景點", "購物"],
            min_rating=4.0
        )
        
        # 驗證結果
        assert len(result) == 2
        assert result[0].name == "台北101"
        assert result[1].name == "西門町"
    
    def test_search_no_results(self, place_repository, mock_db_session):
        """測試搜尋景點無結果"""
        # 設定 Mock 鏈式調用 - 直接返回空結果
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用返回自己
        mock_query.limit.return_value = mock_query   # 鏈式調用返回自己
        mock_query.all.return_value = []             # 最終返回空列表
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = place_repository.search(
            lat=25.0330,
            lon=121.5654,
            radius=1000,
            categories=["不存在類別"],
            min_rating=5.0
        )
        
        # 驗證結果
        assert result == []
    
    def test_search_by_categories_only(self, place_repository, mock_db_session):
        """測試僅按類別搜尋景點"""
        # Mock 資料庫查詢結果
        mock_place1 = Mock(spec=OrmPlace)
        mock_place1.id = "place-1"
        mock_place1.name = "台北101"
        mock_place1.categories = ["景點", "購物"]
        mock_place1.rating = 4.5
        
        mock_places = [mock_place1]
        
        # 設定 Mock 鏈式調用 - 直接返回結果
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用返回自己
        mock_query.limit.return_value = mock_query   # 鏈式調用返回自己
        mock_query.all.return_value = mock_places    # 最終返回結果
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = place_repository.search(categories=["景點"])
        
        # 驗證結果
        assert len(result) == 1
        assert result[0].name == "台北101"
    
    def test_search_by_rating_only(self, place_repository, mock_db_session):
        """測試僅按評分搜尋景點"""
        # Mock 資料庫查詢結果
        mock_place1 = Mock(spec=OrmPlace)
        mock_place1.id = "place-1"
        mock_place1.name = "台北101"
        mock_place1.categories = ["景點", "購物"]
        mock_place1.rating = 4.5
        
        mock_places = [mock_place1]
        
        # 設定 Mock 鏈式調用 - 直接返回結果
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用返回自己
        mock_query.limit.return_value = mock_query   # 鏈式調用返回自己
        mock_query.all.return_value = mock_places    # 最終返回結果
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = place_repository.search(min_rating=4.0)
        
        # 驗證結果
        assert len(result) == 1
        assert result[0].rating >= 4.0
    
    def test_search_by_location_radius(self, place_repository, mock_db_session):
        """測試按地理位置和半徑搜尋景點"""
        # Mock 資料庫查詢結果
        mock_place1 = Mock(spec=OrmPlace)
        mock_place1.id = "place-1"
        mock_place1.name = "台北101"
        mock_place1.categories = ["景點", "購物"]
        mock_place1.rating = 4.5
        
        mock_places = [mock_place1]
        
        # 設定 Mock 鏈式調用 - 直接返回結果
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用返回自己
        mock_query.limit.return_value = mock_query   # 鏈式調用返回自己
        mock_query.all.return_value = mock_places    # 最終返回結果
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        result = place_repository.search(
            lat=25.0330,
            lon=121.5654,
            radius=2000
        )
        
        # 驗證結果
        assert len(result) == 1
        assert result[0].name == "台北101"
    
    def test_search_by_vector(self, place_repository, mock_db_session):
        """測試按向量相似度搜尋景點"""
        # Mock 資料庫查詢結果
        mock_place1 = Mock(spec=OrmPlace)
        mock_place1.id = "place-1"
        mock_place1.name = "台北101"
        mock_place1.categories = ["景點", "購物"]
        mock_place1.rating = 4.5
        
        mock_places = [mock_place1]
        
        # 設定 Mock 鏈式調用 - 直接返回結果
        mock_query = Mock()
        mock_query.filter.return_value = mock_query  # 鏈式調用返回自己
        mock_query.order_by.return_value = mock_query  # 鏈式調用返回自己
        mock_query.limit.return_value = mock_query   # 鏈式調用返回自己
        mock_query.all.return_value = mock_places    # 最終返回結果
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        embedding = [0.1, 0.2, 0.3] * 512  # 模擬 1536 維向量
        result = place_repository.search_by_vector(embedding, top_k=10)
        
        # 驗證結果
        assert len(result) == 1
        assert result[0].name == "台北101"
    
    def test_search_by_vector_empty_embedding(self, place_repository, mock_db_session):
        """測試空向量搜尋景點"""
        # 執行測試
        result = place_repository.search_by_vector([])
        
        # 驗證結果
        assert result == []
    
    def test_get_hours_for_places(self, place_repository, mock_db_session):
        """測試獲取景點營業時間"""
        # Mock 資料庫查詢結果
        mock_hours = [
            Mock(spec=OrmHour, place_id="place-1", weekday=1, open_min=540, close_min=1020),
            Mock(spec=OrmHour, place_id="place-2", weekday=1, open_min=600, close_min=1080)
        ]
        
        # 設定 Mock 查詢
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_hours
        mock_db_session.query.return_value = mock_query
        
        # 執行測試
        place_ids = ["place-1", "place-2"]
        result = place_repository.get_hours_for_places(place_ids)
        
        # 驗證結果
        assert len(result) == 2
        assert "place-1" in result
        assert "place-2" in result
        assert len(result["place-1"]) == 1
        assert len(result["place-2"]) == 1
    
    def test_get_hours_for_places_empty_list(self, place_repository, mock_db_session):
        """測試獲取空列表景點的營業時間"""
        # 執行測試
        result = place_repository.get_hours_for_places([])
        
        # 驗證結果
        assert result == {}