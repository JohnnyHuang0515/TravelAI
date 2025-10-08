import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.itinerary_planner.api.v1.endpoints.routing import (
    router,
    calculate_route,
    calculate_route_post,
    get_travel_time_matrix,
    RouteCalculationRequest,
    RouteCalculationResponse
)


class TestRoutingEndpoints:
    """測試路由計算端點"""

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
    def sample_route_request(self):
        """建立範例路由請求"""
        return RouteCalculationRequest(
            start_lat=25.0330,
            start_lon=121.5654,
            end_lat=25.0478,
            end_lon=121.5319,
            vehicle_type="car",
            route_preference="fastest",
            traffic_conditions="normal"
        )

    @pytest.fixture
    def sample_route_response(self):
        """建立範例路由回應"""
        return RouteCalculationResponse(
            duration=1800.0,
            distance=10000.0,
            carbon_emission=2500.0
        )

    @pytest.mark.asyncio
    async def test_calculate_route_success(self, sample_route_response):
        """測試成功計算路由"""
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm, \
             patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon:
            
            # 模擬 OSRM 返回路線
            mock_routes = [{
                "distance": 10000,
                "duration": 1800,
                "geometry": "encoded_polyline"
            }]
            mock_osrm.get_route_alternatives = AsyncMock(return_value=mock_routes)
            
            # 模擬碳排放計算
            mock_carbon_instance = Mock()
            mock_carbon.return_value = mock_carbon_instance
            mock_carbon_instance.calculate_carbon_emission.return_value = 2500.0
            
            result = await calculate_route(
                start_lat=25.0330,
                start_lon=121.5654,
                end_lat=25.0478,
                end_lon=121.5319,
                vehicle_type="car",
                route_preference="fastest",
                traffic_conditions="normal"
            )
            
            assert result.duration == 1800.0
            assert result.distance == 10000.0
            assert result.carbon_emission == 2500.0
            mock_osrm.get_route_alternatives.assert_called_once()
            mock_carbon_instance.calculate_carbon_emission.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_route_osrm_failure(self):
        """測試 OSRM 失敗時使用預設值"""
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm, \
             patch('src.itinerary_planner.api.v1.endpoints.routing.CarbonCalculationService') as mock_carbon:
            
            # 模擬 OSRM 返回空列表
            mock_osrm.get_route_alternatives = AsyncMock(return_value=[])
            
            # 模擬碳排放計算
            mock_carbon_instance = Mock()
            mock_carbon.return_value = mock_carbon_instance
            mock_carbon_instance.calculate_carbon_emission.return_value = 2000.0
            
            result = await calculate_route(
                start_lat=25.0330,
                start_lon=121.5654,
                end_lat=25.0478,
                end_lon=121.5319,
                vehicle_type="car",
                route_preference="fastest",
                traffic_conditions="normal"
            )
            
            # 應該使用預設值
            assert result.duration == 1800.0  # 預設 30 分鐘
            assert result.distance == 10000.0  # 預設 10 公里
            assert result.carbon_emission == 2000.0

    @pytest.mark.asyncio
    async def test_calculate_route_invalid_vehicle_type(self):
        """測試無效的交通工具類型"""
        with pytest.raises(HTTPException) as exc_info:
            await calculate_route(
                start_lat=25.0330,
                start_lon=121.5654,
                end_lat=25.0478,
                end_lon=121.5319,
                vehicle_type="invalid_vehicle",
                route_preference="fastest",
                traffic_conditions="normal"
            )
        
        assert exc_info.value.status_code == 500
        assert "不支援的交通工具類型" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_calculate_route_invalid_route_preference(self):
        """測試無效的路線偏好"""
        with pytest.raises(HTTPException) as exc_info:
            await calculate_route(
                start_lat=25.0330,
                start_lon=121.5654,
                end_lat=25.0478,
                end_lon=121.5319,
                vehicle_type="car",
                route_preference="invalid_preference",
                traffic_conditions="normal"
            )
        
        assert exc_info.value.status_code == 500
        assert "不支援的路線偏好" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_calculate_route_exception(self):
        """測試計算路由時發生異常"""
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            # 模擬 OSRM 拋出異常
            mock_osrm.get_route_alternatives = AsyncMock(side_effect=Exception("OSRM 服務錯誤"))
            
            with pytest.raises(HTTPException) as exc_info:
                await calculate_route(
                    start_lat=25.0330,
                    start_lon=121.5654,
                    end_lat=25.0478,
                    end_lon=121.5319,
                    vehicle_type="car",
                    route_preference="fastest",
                    traffic_conditions="normal"
                )
            
            assert exc_info.value.status_code == 500
            assert "路由計算失敗" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_calculate_route_post_success(self, sample_route_request, sample_route_response):
        """測試 POST 方法計算路由"""
        with patch('src.itinerary_planner.api.v1.endpoints.routing.calculate_route') as mock_calculate:
            mock_calculate.return_value = sample_route_response
            
            result = await calculate_route_post(sample_route_request)
            
            assert result == sample_route_response
            mock_calculate.assert_called_once_with(
                start_lat=sample_route_request.start_lat,
                start_lon=sample_route_request.start_lon,
                end_lat=sample_route_request.end_lat,
                end_lon=sample_route_request.end_lon,
                vehicle_type=sample_route_request.vehicle_type,
                route_preference=sample_route_request.route_preference,
                traffic_conditions=sample_route_request.traffic_conditions
            )

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_success(self):
        """測試成功獲取旅行時間矩陣"""
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            # 模擬時間矩陣
            mock_matrix = [
                [0, 1800, 3600],
                [1800, 0, 1800],
                [3600, 1800, 0]
            ]
            mock_osrm.get_travel_time_matrix = AsyncMock(return_value=mock_matrix)
            
            result = await get_travel_time_matrix(
                locations="25.0330,121.5654;25.0478,121.5319;25.0614,121.5174",
                vehicle_type="car"
            )
            
            assert result["matrix"] == mock_matrix
            assert len(result["locations"]) == 3
            assert result["vehicle_type"] == "car"
            mock_osrm.get_travel_time_matrix.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_insufficient_locations(self):
        """測試地點數量不足"""
        with pytest.raises(HTTPException) as exc_info:
            await get_travel_time_matrix(
                locations="25.0330,121.5654",
                vehicle_type="car"
            )
        
        assert exc_info.value.status_code == 500
        assert "至少需要兩個地點" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_invalid_format(self):
        """測試無效的地點格式"""
        with pytest.raises(HTTPException) as exc_info:
            await get_travel_time_matrix(
                locations="invalid_format",
                vehicle_type="car"
            )
        
        assert exc_info.value.status_code == 500
        assert "時間矩陣計算失敗" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_exception(self):
        """測試時間矩陣計算異常"""
        with patch('src.itinerary_planner.api.v1.endpoints.routing.osrm_client') as mock_osrm:
            # 模擬 OSRM 拋出異常
            mock_osrm.get_travel_time_matrix = AsyncMock(side_effect=Exception("矩陣計算錯誤"))
            
            with pytest.raises(HTTPException) as exc_info:
                await get_travel_time_matrix(
                    locations="25.0330,121.5654;25.0478,121.5319",
                    vehicle_type="car"
                )
            
            assert exc_info.value.status_code == 500
            assert "時間矩陣計算失敗" in str(exc_info.value.detail)

    def test_route_calculation_request_model(self):
        """測試 RouteCalculationRequest 模型"""
        request = RouteCalculationRequest(
            start_lat=25.0330,
            start_lon=121.5654,
            end_lat=25.0478,
            end_lon=121.5319,
            vehicle_type="motorcycle",
            route_preference="shortest",
            traffic_conditions="heavy"
        )
        
        assert request.start_lat == 25.0330
        assert request.start_lon == 121.5654
        assert request.end_lat == 25.0478
        assert request.end_lon == 121.5319
        assert request.vehicle_type == "motorcycle"
        assert request.route_preference == "shortest"
        assert request.traffic_conditions == "heavy"

    def test_route_calculation_response_model(self):
        """測試 RouteCalculationResponse 模型"""
        response = RouteCalculationResponse(
            duration=1800.0,
            distance=10000.0,
            carbon_emission=2500.0,
            route_geometry="encoded_polyline"
        )
        
        assert response.duration == 1800.0
        assert response.distance == 10000.0
        assert response.carbon_emission == 2500.0
        assert response.route_geometry == "encoded_polyline"

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == "/routing"
        assert len(router.routes) == 3  # /calculate (GET), /calculate (POST), /matrix

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/routing/calculate" in route_paths
        assert "/routing/matrix" in route_paths
