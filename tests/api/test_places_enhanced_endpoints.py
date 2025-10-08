import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI
import datetime

from src.itinerary_planner.api.v1.endpoints.places_enhanced import (
    router,
    get_nearby_places,
    get_my_favorites,
    add_favorite,
    remove_favorite
)
from src.itinerary_planner.infrastructure.persistence.orm_models import User, Place
from src.itinerary_planner.api.v1.schemas.auth import MessageResponse


class TestPlacesEnhancedEndpoints:
    """測試增強版地點 API 端點"""

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
    def sample_user(self):
        """建立範例使用者"""
        user = Mock(spec=User)
        user.id = "user123"
        user.email = "test@example.com"
        user.username = "testuser"
        user.is_active = True
        user.is_verified = True
        user.created_at = datetime.datetime.now(datetime.timezone.utc)
        user.last_login = datetime.datetime.now(datetime.timezone.utc)
        user.avatar_url = None
        user.profile = None
        return user

    @pytest.fixture
    def sample_place(self):
        """建立範例地點"""
        place = Mock(spec=Place)
        place.id = "place123"
        place.name = "台北101"
        place.categories = ["觀光景點", "建築"]
        place.rating = 4.5
        place.stay_minutes = 120
        place.price_range = "medium"
        place.geom = Mock()  # Mock geometry object
        return place

    @pytest.fixture
    def sample_favorite(self):
        """建立範例收藏"""
        favorite = Mock()
        favorite.place_id = "place123"
        favorite.notes = "很棒的景點"
        favorite.created_at = datetime.datetime.now(datetime.timezone.utc)
        return favorite

    @pytest.mark.asyncio
    async def test_get_nearby_places_success(self, sample_place):
        """測試成功獲取附近景點"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PostgresPlaceRepository') as mock_place_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.to_shape') as mock_to_shape:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock place repository
            mock_place_repo = Mock()
            mock_place_repo_class.return_value = mock_place_repo
            mock_place_repo.search.return_value = [sample_place]
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = []
            
            # Mock geometry conversion
            mock_point = Mock()
            mock_point.x = 121.5654
            mock_point.y = 25.0330
            mock_to_shape.return_value = mock_point
            
            result = await get_nearby_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=["觀光景點"],
                min_rating=4.0,
                limit=20,
                current_user=None,
                db=mock_db
            )
            
            assert "places" in result
            assert "total" in result
            assert "user_location" in result
            assert len(result["places"]) == 1
            assert result["places"][0]["name"] == "台北101"
            assert result["places"][0]["is_favorite"] is False
            assert result["user_location"]["lat"] == 25.0330
            assert result["user_location"]["lon"] == 121.5654

    @pytest.mark.asyncio
    async def test_get_nearby_places_with_user_favorites(self, sample_place, sample_user, sample_favorite):
        """測試帶使用者收藏的附近景點"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PostgresPlaceRepository') as mock_place_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.to_shape') as mock_to_shape:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock place repository
            mock_place_repo = Mock()
            mock_place_repo_class.return_value = mock_place_repo
            mock_place_repo.search.return_value = [sample_place]
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = [sample_favorite]
            
            # Mock geometry conversion
            mock_point = Mock()
            mock_point.x = 121.5654
            mock_point.y = 25.0330
            mock_to_shape.return_value = mock_point
            
            result = await get_nearby_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None,
                limit=20,
                current_user=sample_user,
                db=mock_db
            )
            
            assert len(result["places"]) == 1
            assert result["places"][0]["is_favorite"] is True
            mock_fav_repo.get_user_favorites.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_get_nearby_places_with_filters(self, sample_place):
        """測試帶篩選條件的附近景點"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PostgresPlaceRepository') as mock_place_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.to_shape') as mock_to_shape:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock place repository
            mock_place_repo = Mock()
            mock_place_repo_class.return_value = mock_place_repo
            mock_place_repo.search.return_value = [sample_place]
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = []
            
            # Mock geometry conversion
            mock_point = Mock()
            mock_point.x = 121.5654
            mock_point.y = 25.0330
            mock_to_shape.return_value = mock_point
            
            result = await get_nearby_places(
                lat=25.0330,
                lon=121.5654,
                radius=3000,
                categories=["餐廳", "咖啡廳"],
                min_rating=4.5,
                limit=10,
                current_user=None,
                db=mock_db
            )
            
            mock_place_repo.search.assert_called_once_with(
                lat=25.0330,
                lon=121.5654,
                radius=3000,
                categories=["餐廳", "咖啡廳"],
                min_rating=4.5
            )

    @pytest.mark.asyncio
    async def test_get_nearby_places_error(self):
        """測試獲取附近景點錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PostgresPlaceRepository') as mock_place_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock place repository error
            mock_place_repo = Mock()
            mock_place_repo_class.return_value = mock_place_repo
            mock_place_repo.search.side_effect = Exception("資料庫錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_nearby_places(
                    lat=25.0330,
                    lon=121.5654,
                    radius=5000,
                    categories=None,
                    min_rating=None,
                    limit=20,
                    current_user=None,
                    db=mock_db
                )
            
            assert exc_info.value.status_code == 500
            assert "搜尋附近景點時發生錯誤" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_my_favorites_success(self, sample_user, sample_favorite, sample_place):
        """測試成功獲取我的收藏"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.to_shape') as mock_to_shape:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = [sample_favorite]
            
            # Mock database query
            mock_query = Mock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = sample_place
            
            # Mock geometry conversion
            mock_point = Mock()
            mock_point.x = 121.5654
            mock_point.y = 25.0330
            mock_to_shape.return_value = mock_point
            
            result = await get_my_favorites(sample_user, mock_db)
            
            assert "favorites" in result
            assert "total" in result
            assert len(result["favorites"]) == 1
            assert result["favorites"][0]["name"] == "台北101"
            assert result["favorites"][0]["notes"] == "很棒的景點"
            mock_fav_repo.get_user_favorites.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_get_my_favorites_empty(self, sample_user):
        """測試獲取空收藏列表"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = []
            
            result = await get_my_favorites(sample_user, mock_db)
            
            assert result["favorites"] == []
            assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_add_favorite_success(self, sample_user, sample_place):
        """測試成功添加收藏"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock database query
            mock_query = Mock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = sample_place
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            
            result = await add_favorite("place123", "很棒的景點", sample_user, mock_db)
            
            assert isinstance(result, MessageResponse)
            assert result.message == "已加入收藏"
            mock_fav_repo.add_favorite.assert_called_once_with(
                user_id="user123",
                place_id="place123",
                notes="很棒的景點"
            )

    @pytest.mark.asyncio
    async def test_add_favorite_place_not_found(self, sample_user):
        """測試添加收藏時景點不存在"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock database query - place not found
            mock_query = Mock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await add_favorite("nonexistent_place", None, sample_user, mock_db)
            
            assert exc_info.value.status_code == 404
            assert "景點不存在" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_remove_favorite_success(self, sample_user):
        """測試成功移除收藏"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.remove_favorite.return_value = True
            
            result = await remove_favorite("place123", sample_user, mock_db)
            
            assert isinstance(result, MessageResponse)
            assert result.message == "已取消收藏"
            mock_fav_repo.remove_favorite.assert_called_once_with(
                user_id="user123",
                place_id="place123"
            )

    @pytest.mark.asyncio
    async def test_remove_favorite_not_found(self, sample_user):
        """測試移除不存在的收藏"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.remove_favorite.return_value = False
            
            with pytest.raises(HTTPException) as exc_info:
                await remove_favorite("place123", sample_user, mock_db)
            
            assert exc_info.value.status_code == 404
            assert "未收藏此景點" in str(exc_info.value.detail)

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == "/places"
        assert len(router.routes) == 4  # nearby, favorites, add_favorite, remove_favorite

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/places/nearby" in route_paths
        assert "/places/favorites" in route_paths
        assert "/places/{place_id}/favorite" in route_paths

    def test_message_response_model(self):
        """測試 MessageResponse 模型"""
        response = MessageResponse(message="測試訊息")
        assert response.message == "測試訊息"

    @pytest.mark.asyncio
    async def test_get_nearby_places_distance_calculation(self, sample_place):
        """測試距離計算功能"""
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PostgresPlaceRepository') as mock_place_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.to_shape') as mock_to_shape:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock place repository
            mock_place_repo = Mock()
            mock_place_repo_class.return_value = mock_place_repo
            mock_place_repo.search.return_value = [sample_place]
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = []
            
            # Mock geometry conversion - 距離較遠的地點
            mock_point = Mock()
            mock_point.x = 121.6000  # 較遠的經度
            mock_point.y = 25.1000   # 較遠的緯度
            mock_to_shape.return_value = mock_point
            
            result = await get_nearby_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None,
                limit=20,
                current_user=None,
                db=mock_db
            )
            
            assert len(result["places"]) == 1
            place_data = result["places"][0]
            assert "distance_meters" in place_data
            assert "distance_text" in place_data
            assert place_data["distance_meters"] > 0
            assert "公里" in place_data["distance_text"] or "公尺" in place_data["distance_text"]

    @pytest.mark.asyncio
    async def test_get_nearby_places_sorting(self, sample_place):
        """測試距離排序功能"""
        # 創建兩個不同距離的地點
        place1 = Mock(spec=Place)
        place1.id = "place1"
        place1.name = "近的地點"
        place1.categories = ["觀光景點"]
        place1.rating = 4.0
        place1.stay_minutes = 60
        place1.price_range = "low"
        place1.geom = Mock()
        
        place2 = Mock(spec=Place)
        place2.id = "place2"
        place2.name = "遠的地點"
        place2.categories = ["觀光景點"]
        place2.rating = 4.5
        place2.stay_minutes = 120
        place2.price_range = "high"
        place2.geom = Mock()
        
        with patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PostgresPlaceRepository') as mock_place_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.PlaceFavoriteRepository') as mock_fav_repo_class, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.get_db') as mock_get_db, \
             patch('src.itinerary_planner.api.v1.endpoints.places_enhanced.to_shape') as mock_to_shape:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock place repository
            mock_place_repo = Mock()
            mock_place_repo_class.return_value = mock_place_repo
            mock_place_repo.search.return_value = [place2, place1]  # 故意打亂順序
            
            # Mock favorite repository
            mock_fav_repo = Mock()
            mock_fav_repo_class.return_value = mock_fav_repo
            mock_fav_repo.get_user_favorites.return_value = []
            
            # Mock geometry conversion
            def mock_to_shape_side_effect(geom):
                mock_point = Mock()
                if geom == place1.geom:
                    mock_point.x = 121.5654  # 較近
                    mock_point.y = 25.0330
                else:  # place2.geom
                    mock_point.x = 121.6000  # 較遠
                    mock_point.y = 25.1000
                return mock_point
            
            mock_to_shape.side_effect = mock_to_shape_side_effect
            
            result = await get_nearby_places(
                lat=25.0330,
                lon=121.5654,
                radius=5000,
                categories=None,
                min_rating=None,
                limit=20,
                current_user=None,
                db=mock_db
            )
            
            # 驗證按距離排序
            assert len(result["places"]) == 2
            assert result["places"][0]["name"] == "近的地點"  # 距離較近的應該在前面
            assert result["places"][1]["name"] == "遠的地點"  # 距離較遠的應該在後面
            assert result["places"][0]["distance_meters"] < result["places"][1]["distance_meters"]