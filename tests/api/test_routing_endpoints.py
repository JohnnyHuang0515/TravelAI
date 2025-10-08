"""
測試 routing.py 端點
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, AsyncMock, patch
import datetime
from uuid import uuid4

from src.itinerary_planner.infrastructure.persistence.orm_models import User
from src.itinerary_planner.api.v1.endpoints.routing import router
from src.itinerary_planner.infrastructure.persistence.database import get_db


class TestRoutingEndpoints:
    """測試路由計算端點"""

    @pytest.fixture
    def app(self):
        """建立 FastAPI 應用程式實例"""
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
        return User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            provider="email",
            provider_id=None,
            avatar_url=None,
            profile=None,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            last_login=datetime.datetime.now(datetime.timezone.utc),
            is_active=True,
            is_verified=True
        )

    @pytest.mark.asyncio
    async def test_calculate_route_get_success(self, app, client):
        """測試成功計算路線 (GET)"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # Mock OSRM client
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            with patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon_service:
                # 設定 Mock 返回值
                mock_osrm.get_route_alternatives = AsyncMock(return_value=[
                    {"distance": 5000, "duration": 1200}
                ])
                
                mock_carbon_service_instance = Mock()
                mock_carbon_service_instance.calculate_carbon_emission.return_value = 150.5
                mock_carbon_service.return_value = mock_carbon_service_instance

                # 執行測試
                response = client.get("/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700&vehicle_type=car&route_preference=fastest&traffic_conditions=normal")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert "duration" in data
                assert "distance" in data
                assert "carbon_emission" in data
                assert data["duration"] == 1200
                assert data["distance"] == 5000
                assert data["carbon_emission"] == 150.5

                # 驗證 Mock 調用
                mock_osrm.get_route_alternatives.assert_called_once_with(
                    (25.0330, 121.5654),
                    (25.0400, 121.5700),
                    "fastest"
                )
                mock_carbon_service_instance.calculate_carbon_emission.assert_called_once_with(
                    distance=5000,
                    vehicle_type="car",
                    traffic_conditions="normal"
                )

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_get_osrm_failure(self, app, client):
        """測試 OSRM 失敗時使用預設值"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # Mock OSRM client 返回空結果
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            with patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon_service:
                # 設定 Mock 返回值
                mock_osrm.get_route_alternatives = AsyncMock(return_value=[])
                
                mock_carbon_service_instance = Mock()
                mock_carbon_service_instance.calculate_carbon_emission.return_value = 200.0
                mock_carbon_service.return_value = mock_carbon_service_instance

                # 執行測試
                response = client.get("/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700&vehicle_type=motorcycle")

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert data["duration"] == 1800  # 預設 30 分鐘
                assert data["distance"] == 10000  # 預設 10 公里
                assert data["carbon_emission"] == 200.0

                # 驗證使用預設值計算碳排放
                mock_carbon_service_instance.calculate_carbon_emission.assert_called_once_with(
                    distance=10000,
                    vehicle_type="motorcycle",
                    traffic_conditions="normal"
                )

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_get_invalid_vehicle_type(self, app, client):
        """測試無效的交通工具類型"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試
        response = client.get("/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700&vehicle_type=invalid")

        # 驗證結果
        assert response.status_code == 500
        assert "不支援的交通工具類型" in response.json()["detail"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_get_invalid_route_preference(self, app, client):
        """測試無效的路線偏好"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試
        response = client.get("/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700&route_preference=invalid")

        # 驗證結果
        assert response.status_code == 500
        assert "不支援的路線偏好" in response.json()["detail"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_get_missing_parameters(self, app, client):
        """測試缺少必要參數"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試 - 缺少 end_lat
        response = client.get("/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lon=121.5700")

        # 驗證結果
        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_get_exception(self, app, client):
        """測試計算路線時發生異常"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # Mock OSRM client 拋出異常
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            mock_osrm.get_route_alternatives = AsyncMock(side_effect=Exception("OSRM service error"))

            # 執行測試
            response = client.get("/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700")

            # 驗證結果
            assert response.status_code == 500
            assert "路由計算失敗: OSRM service error" in response.json()["detail"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_post_success(self, app, client):
        """測試成功計算路線 (POST)"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # Mock OSRM client
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            with patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon_service:
                # 設定 Mock 返回值
                mock_osrm.get_route_alternatives = AsyncMock(return_value=[
                    {"distance": 3000, "duration": 900}
                ])
                
                mock_carbon_service_instance = Mock()
                mock_carbon_service_instance.calculate_carbon_emission.return_value = 120.0
                mock_carbon_service.return_value = mock_carbon_service_instance

                # 準備請求資料
                request_data = {
                    "start_lat": 25.0330,
                    "start_lon": 121.5654,
                    "end_lat": 25.0400,
                    "end_lon": 121.5700,
                    "vehicle_type": "bus",
                    "route_preference": "shortest",
                    "traffic_conditions": "heavy"
                }

                # 執行測試
                response = client.post("/routing/calculate", json=request_data)

                # 驗證結果
                assert response.status_code == 200
                data = response.json()
                assert data["duration"] == 900
                assert data["distance"] == 3000
                assert data["carbon_emission"] == 120.0

                # 驗證 Mock 調用
                mock_osrm.get_route_alternatives.assert_called_once_with(
                    (25.0330, 121.5654),
                    (25.0400, 121.5700),
                    "shortest"
                )
                mock_carbon_service_instance.calculate_carbon_emission.assert_called_once_with(
                    distance=3000,
                    vehicle_type="bus",
                    traffic_conditions="heavy"
                )

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_post_validation_error(self, app, client):
        """測試 POST 請求驗證錯誤"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 準備無效的請求資料
        request_data = {
            "start_lat": 25.0330,
            "start_lon": 121.5654,
            "end_lat": 25.0400,
            # 缺少 end_lon
            "vehicle_type": "car"
        }

        # 執行測試
        response = client.post("/routing/calculate", json=request_data)

        # 驗證結果
        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_success(self, app, client):
        """測試成功計算旅行時間矩陣"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # Mock OSRM client
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            # 設定 Mock 返回值
            mock_matrix = [
                [0, 300, 600],
                [300, 0, 400],
                [600, 400, 0]
            ]
            mock_osrm.get_travel_time_matrix = AsyncMock(return_value=mock_matrix)

            # 執行測試
            response = client.get("/routing/matrix?locations=25.0330,121.5654;25.0400,121.5700;25.0500,121.5800&vehicle_type=car")

            # 驗證結果
            assert response.status_code == 200
            data = response.json()
            assert "matrix" in data
            assert "locations" in data
            assert "vehicle_type" in data
            assert data["matrix"] == mock_matrix
            assert data["vehicle_type"] == "car"
            assert len(data["locations"]) == 3

            # 驗證 Mock 調用
            expected_locations = [(25.0330, 121.5654), (25.0400, 121.5700), (25.0500, 121.5800)]
            mock_osrm.get_travel_time_matrix.assert_called_once_with(
                expected_locations,
                route_preference="fastest"
            )

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_insufficient_locations(self, app, client):
        """測試地點數量不足"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試 - 只有一個地點
        response = client.get("/routing/matrix?locations=25.0330,121.5654&vehicle_type=car")

        # 驗證結果
        assert response.status_code == 500
        assert "至少需要兩個地點" in response.json()["detail"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_invalid_format(self, app, client):
        """測試無效的地點格式"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試 - 無效格式
        response = client.get("/routing/matrix?locations=invalid_format&vehicle_type=car")

        # 驗證結果
        assert response.status_code == 500
        assert "時間矩陣計算失敗" in response.json()["detail"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_missing_parameters(self, app, client):
        """測試缺少必要參數"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # 執行測試 - 缺少 locations 參數
        response = client.get("/routing/matrix?vehicle_type=car")

        # 驗證結果
        assert response.status_code == 422  # Validation error

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_exception(self, app, client):
        """測試計算時間矩陣時發生異常"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        # Mock OSRM client 拋出異常
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            mock_osrm.get_travel_time_matrix = AsyncMock(side_effect=Exception("Matrix calculation error"))

            # 執行測試
            response = client.get("/routing/matrix?locations=25.0330,121.5654;25.0400,121.5700&vehicle_type=car")

            # 驗證結果
            assert response.status_code == 500
            assert "時間矩陣計算失敗: Matrix calculation error" in response.json()["detail"]

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_different_vehicle_types(self, app, client):
        """測試不同交通工具類型"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        vehicle_types = ["car", "motorcycle", "bus"]
        
        for vehicle_type in vehicle_types:
            with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
                with patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon_service:
                    # 設定 Mock 返回值
                    mock_osrm.get_route_alternatives = AsyncMock(return_value=[
                        {"distance": 2000, "duration": 600}
                    ])
                    
                    mock_carbon_service_instance = Mock()
                    mock_carbon_service_instance.calculate_carbon_emission.return_value = 100.0
                    mock_carbon_service.return_value = mock_carbon_service_instance

                    # 執行測試
                    response = client.get(f"/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700&vehicle_type={vehicle_type}")

                    # 驗證結果
                    assert response.status_code == 200
                    data = response.json()
                    assert data["carbon_emission"] == 100.0

                    # 驗證 Mock 調用
                    mock_carbon_service_instance.calculate_carbon_emission.assert_called_once_with(
                        distance=2000,
                        vehicle_type=vehicle_type,
                        traffic_conditions="normal"
                    )

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_calculate_route_different_traffic_conditions(self, app, client):
        """測試不同交通狀況"""
        # 準備 Mock 依賴
        def get_mock_db():
            yield Mock()

        app.dependency_overrides[get_db] = get_mock_db

        traffic_conditions = ["normal", "heavy", "light"]
        
        for traffic in traffic_conditions:
            with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
                with patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon_service:
                    # 設定 Mock 返回值
                    mock_osrm.get_route_alternatives = AsyncMock(return_value=[
                        {"distance": 1500, "duration": 450}
                    ])
                    
                    mock_carbon_service_instance = Mock()
                    mock_carbon_service_instance.calculate_carbon_emission.return_value = 80.0
                    mock_carbon_service.return_value = mock_carbon_service_instance

                    # 執行測試
                    response = client.get(f"/routing/calculate?start_lat=25.0330&start_lon=121.5654&end_lat=25.0400&end_lon=121.5700&traffic_conditions={traffic}")

                    # 驗證結果
                    assert response.status_code == 200
                    data = response.json()
                    assert data["carbon_emission"] == 80.0

                    # 驗證 Mock 調用
                    mock_carbon_service_instance.calculate_carbon_emission.assert_called_once_with(
                        distance=1500,
                        vehicle_type="car",
                        traffic_conditions=traffic
                    )

        app.dependency_overrides.clear()
