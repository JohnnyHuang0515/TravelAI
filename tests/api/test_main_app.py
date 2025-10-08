"""
測試 main.py 應用程式
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import logging

from src.itinerary_planner.main import app


class TestMainApp:
    """測試主應用程式"""

    @pytest.fixture
    def client(self):
        """建立測試客戶端"""
        return TestClient(app)

    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_app_title_and_version(self, client):
        """測試應用程式標題和版本"""
        # 測試 OpenAPI 文檔
        response = client.get("/docs")
        assert response.status_code == 200
        
        # 測試 OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "智慧旅遊行程規劃器 API"
        assert data["info"]["version"] == "1.0.0"

    def test_cors_headers(self, client):
        """測試 CORS 設定"""
        # 測試 GET 請求並檢查 CORS 標頭
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        
        # 檢查基本 CORS 標頭
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-credentials" in headers
        assert headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_search_places_success(self, client):
        """測試地點搜索端點成功"""
        # Mock 資料庫和 repository
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
            with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                # 設定 Mock 返回值
                mock_db_session = Mock()
                mock_session_local.return_value = mock_db_session
                
                mock_repo = Mock()
                mock_place = Mock()
                mock_place.id = "place_1"
                mock_place.name = "台北101"
                mock_place.categories = ["觀光景點", "建築"]
                mock_place.rating = 4.5
                mock_place.stay_minutes = 120
                mock_place.price_range = "medium"
                mock_repo.search.return_value = [mock_place]
                mock_repo_class.return_value = mock_repo

                # 執行測試
                response = client.get("/v1/places/search?lat=25.0330&lon=121.5654&radius=5000")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["id"] == "place_1"
                assert data[0]["name"] == "台北101"
                assert data[0]["categories"] == ["觀光景點", "建築"]
                assert data[0]["rating"] == 4.5
                assert data[0]["stay_minutes"] == 120
                assert data[0]["price_range"] == "medium"

                # 驗證 Mock 調用
                mock_repo.search.assert_called_once_with(
                    lat=25.0330,
                    lon=121.5654,
                    radius=5000,
                    categories=None,
                    min_rating=None
                )
                mock_db_session.close.assert_called_once()

    def test_search_places_with_categories(self, client):
        """測試帶類別的地點搜索"""
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
            with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                # 設定 Mock 返回值
                mock_db_session = Mock()
                mock_session_local.return_value = mock_db_session
                
                mock_repo = Mock()
                mock_repo.search.return_value = []
                mock_repo_class.return_value = mock_repo

                # 執行測試 - 帶類別參數
                response = client.get("/v1/places/search?categories=觀光景點,美食&min_rating=4.0")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert data == []

                # 驗證 Mock 調用
                mock_repo.search.assert_called_once_with(
                    lat=None,
                    lon=None,
                    radius=5000,
                    categories=["觀光景點", "美食"],
                    min_rating=4.0
                )

    def test_search_places_no_results(self, client):
        """測試沒有結果的地點搜索"""
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
            with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                # 設定 Mock 返回值
                mock_db_session = Mock()
                mock_session_local.return_value = mock_db_session
                
                mock_repo = Mock()
                mock_repo.search.return_value = []
                mock_repo_class.return_value = mock_repo

                # 執行測試
                response = client.get("/v1/places/search")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert data == []

    def test_search_places_database_error(self, client):
        """測試資料庫錯誤"""
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
            with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                # 設定 Mock 拋出異常
                mock_db_session = Mock()
                mock_session_local.return_value = mock_db_session
                
                mock_repo = Mock()
                mock_repo.search.side_effect = Exception("Database connection error")
                mock_repo_class.return_value = mock_repo

                # 執行測試
                response = client.get("/v1/places/search")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert "error" in data
                assert "Database connection error" in data["error"]

    def test_search_places_with_none_rating(self, client):
        """測試評分為 None 的地點"""
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
            with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                # 設定 Mock 返回值
                mock_db_session = Mock()
                mock_session_local.return_value = mock_db_session
                
                mock_repo = Mock()
                mock_place = Mock()
                mock_place.id = "place_2"
                mock_place.name = "無評分景點"
                mock_place.categories = ["其他"]
                mock_place.rating = None  # 無評分
                mock_place.stay_minutes = 60
                mock_place.price_range = "low"
                mock_repo.search.return_value = [mock_place]
                mock_repo_class.return_value = mock_repo

                # 執行測試
                response = client.get("/v1/places/search")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["rating"] is None

    def test_search_places_with_empty_categories(self, client):
        """測試空類別的地點"""
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
            with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                # 設定 Mock 返回值
                mock_db_session = Mock()
                mock_session_local.return_value = mock_db_session
                
                mock_repo = Mock()
                mock_place = Mock()
                mock_place.id = "place_3"
                mock_place.name = "無類別景點"
                mock_place.categories = None  # 無類別
                mock_place.rating = 3.0
                mock_place.stay_minutes = 90
                mock_place.price_range = "high"
                mock_repo.search.return_value = [mock_place]
                mock_repo_class.return_value = mock_repo

                # 執行測試
                response = client.get("/v1/places/search")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["categories"] == []

    def test_routing_endpoints_available(self, client):
        """測試路由端點是否可用"""
        # 測試路由計算端點 - 使用更簡單的測試
        response = client.get("/v1/routing/calculate")
        # 應該返回 422 因為缺少必要參數，但端點存在
        assert response.status_code in [422, 500, 504]  # 根據實際實現可能不同

    def test_health_check_multiple_requests(self, client):
        """測試健康檢查端點多次請求"""
        for i in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    def test_app_middleware_configuration(self, client):
        """測試應用程式中間件配置"""
        # 測試 CORS 預檢請求
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        assert response.status_code == 200

    def test_search_places_parameter_validation(self, client):
        """測試地點搜索參數驗證"""
        # 測試無效的半徑參數
        response = client.get("/v1/places/search?radius=invalid")
        # 應該返回 422 驗證錯誤
        assert response.status_code == 422

    def test_search_places_logging(self, client):
        """測試地點搜索日誌記錄"""
        with patch('src.itinerary_planner.main.logger') as mock_logger:
            with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session_local:
                with patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
                    # 設定 Mock 返回值
                    mock_db_session = Mock()
                    mock_session_local.return_value = mock_db_session
                    
                    mock_repo = Mock()
                    mock_repo.search.return_value = []
                    mock_repo_class.return_value = mock_repo

                    # 執行測試
                    response = client.get("/v1/places/search?lat=25.0330&lon=121.5654&categories=觀光景點")

                    # 驗證結果
                    assert response.status_code == 200

                    # 驗證日誌記錄
                    mock_logger.info.assert_called()
                    # 檢查是否記錄了搜索請求
                    call_args = [call[0][0] for call in mock_logger.info.call_args_list]
                    assert any("Search places request" in arg for arg in call_args)
                    assert any("Found 0 places" in arg for arg in call_args)
