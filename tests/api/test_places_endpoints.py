import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.itinerary_planner.api.v1.endpoints.places import (
    router,
    search_places
)
from src.itinerary_planner.domain.models.place import Place as DomainPlace


class TestPlacesEndpoints:
    """測試地點 API 端點"""

    @pytest.fixture
    def app(self):
        """建立 FastAPI 應用程式"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """建立測試客戶端"""
        return TestClient(app)

    @pytest.fixture
    def sample_orm_place(self):
        """建立範例 ORM 地點"""
        place = Mock()
        place.id = "place123"
        place.name = "台北101"
        place.categories = ["觀光景點", "建築"]
        place.rating = 4.5
        place.stay_minutes = 120
        return place

    @pytest.fixture
    def sample_domain_place(self):
        """建立範例 Domain 地點"""
        return DomainPlace(
            id="place123",
            name="台北101",
            categories=["觀光景點", "建築"],
            rating=4.5,
            stay_minutes=120
        )

    def test_search_places_success(self, sample_orm_place):
        """測試成功搜索地點"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=["觀光景點"],
                min_rating=4.0,
                db=mock_db
            )
            
            assert len(result) == 1
            assert result[0].id == "place123"
            assert result[0].name == "台北101"
            assert result[0].categories == ["觀光景點", "建築"]
            assert result[0].rating == 4.5
            assert result[0].stay_minutes == 120
            
            mock_repo.search.assert_called_once_with(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=["觀光景點"],
                min_rating=4.0
            )

    def test_search_places_no_results(self):
        """測試搜索無結果"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬無結果
            mock_repo.search.return_value = []
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None,
                db=mock_db
            )
            
            assert len(result) == 0
            mock_repo.search.assert_called_once_with(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None
            )

    def test_search_places_with_categories(self, sample_orm_place):
        """測試帶類別搜索"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=["觀光景點", "餐廳"],
                min_rating=None,
                db=mock_db
            )
            
            assert len(result) == 1
            mock_repo.search.assert_called_once_with(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=["觀光景點", "餐廳"],
                min_rating=None
            )

    def test_search_places_with_min_rating(self, sample_orm_place):
        """測試帶最低評分搜索"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=4.0,
                db=mock_db
            )
            
            assert len(result) == 1
            mock_repo.search.assert_called_once_with(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=4.0
            )

    def test_search_places_no_location(self, sample_orm_place):
        """測試無位置搜索"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=None,
                lon=None,
                radius=5000,
                categories=None,
                min_rating=None,
                db=mock_db
            )
            
            assert len(result) == 1
            mock_repo.search.assert_called_once_with(
                lat=None,
                lon=None,
                radius=5000,
                categories=None,
                min_rating=None
            )

    def test_search_places_database_error(self):
        """測試資料庫錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬資料庫錯誤
            mock_repo.search.side_effect = Exception("資料庫連接錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                search_places(
                    lat=25.0330,
                    lon=121.5654,
                    radius=5000,
                    categories=None,
                    min_rating=None,
                    db=mock_db
                )
            
            assert exc_info.value.status_code == 500
            assert "搜索地點時發生錯誤" in str(exc_info.value.detail)

    def test_search_places_with_none_rating(self, sample_orm_place):
        """測試地點評分為 None 的情況"""
        # 修改範例地點，評分為 None
        sample_orm_place.rating = None
        
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None,
                db=mock_db
            )
            
            assert len(result) == 1
            assert result[0].rating is None

    def test_search_places_with_none_categories(self, sample_orm_place):
        """測試地點類別為 None 的情況"""
        # 修改範例地點，類別為 None
        sample_orm_place.categories = None
        
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None,
                db=mock_db
            )
            
            assert len(result) == 1
            assert result[0].categories == []

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == ""
        assert len(router.routes) == 1  # search

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/search" in route_paths

    def test_domain_place_model(self, sample_domain_place):
        """測試 Domain Place 模型"""
        assert sample_domain_place.id == "place123"
        assert sample_domain_place.name == "台北101"
        assert sample_domain_place.categories == ["觀光景點", "建築"]
        assert sample_domain_place.rating == 4.5
        assert sample_domain_place.stay_minutes == 120

    def test_domain_place_with_none_values(self):
        """測試 Domain Place 模型帶 None 值"""
        place = DomainPlace(
            id="place456",
            name="測試地點",
            categories=[],
            rating=None,
            stay_minutes=60
        )
        
        assert place.id == "place456"
        assert place.name == "測試地點"
        assert place.categories == []
        assert place.rating is None
        assert place.stay_minutes == 60

    def test_search_places_logging(self, sample_orm_place):
        """測試搜索地點的日誌記錄"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places.logger') as mock_logger:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬搜索成功
            mock_repo.search.return_value = [sample_orm_place]
            
            result = search_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=["觀光景點"],
                min_rating=4.0,
                db=mock_db
            )
            
            # 驗證日誌記錄
            mock_logger.info.assert_any_call(
                "Search places request: lat=25.033, lon=121.5654, radius=5000, categories=['觀光景點'], min_rating=4.0"
            )
            mock_logger.info.assert_any_call("Found 1 places")

    def test_search_places_error_logging(self):
        """測試搜索地點錯誤的日誌記錄"""
        with patch('src.itinerary_planner.api.v1.endpoints.places.PostgresPlaceRepository') as mock_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places.logger') as mock_logger:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # 模擬資料庫錯誤
            mock_repo.search.side_effect = Exception("資料庫連接錯誤")
            
            with pytest.raises(HTTPException):
                search_places(
                    lat=25.0330,
                    lon=121.5654,
                    radius=5000,
                    categories=None,
                    min_rating=None,
                    db=mock_db
                )
            
            # 驗證錯誤日誌記錄
            mock_logger.error.assert_called_once()
            error_call_args = mock_logger.error.call_args[0]
            assert "Error in search_places" in error_call_args[0]
            assert "資料庫連接錯誤" in error_call_args[0]