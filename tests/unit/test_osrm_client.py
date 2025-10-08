"""
測試 osrm_client.py
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx

from src.itinerary_planner.infrastructure.clients.osrm_client import OSRMClient, osrm_client


class TestOSRMClient:
    """測試 OSRM 客戶端"""

    @pytest.fixture
    def osrm_client_instance(self):
        """建立 OSRM 客戶端實例"""
        return OSRMClient("http://localhost:5000")

    @pytest.mark.asyncio
    async def test_osrm_client_initialization(self):
        """測試 OSRM 客戶端初始化"""
        client = OSRMClient("http://test:5000")
        assert client.base_url == "http://test:5000"

    @pytest.mark.asyncio
    async def test_osrm_client_default_url(self):
        """測試 OSRM 客戶端預設 URL"""
        client = OSRMClient()
        assert client.base_url == "http://localhost:5000"

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_success(self, osrm_client_instance):
        """測試成功獲取旅行時間矩陣"""
        # 準備測試資料
        locations = [(25.0330, 121.5654), (25.0400, 121.5700), (25.0500, 121.5800)]
        expected_matrix = [[0, 300, 600], [300, 0, 400], [600, 400, 0]]
        
        # Mock httpx.AsyncClient
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"durations": expected_matrix}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_travel_time_matrix(locations)
            
            # 驗證結果
            assert result == expected_matrix
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_empty_locations(self, osrm_client_instance):
        """測試空地點列表"""
        result = await osrm_client_instance.get_travel_time_matrix([])
        assert result == []

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_shortest_route(self, osrm_client_instance):
        """測試最短路線偏好"""
        locations = [(25.0330, 121.5654), (25.0400, 121.5700)]
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"durations": [[0, 200], [200, 0]]}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_travel_time_matrix(locations, "shortest")
            
            # 驗證結果
            assert result == [[0, 200], [200, 0]]
            # 驗證請求參數包含 distance 註解
            call_args = mock_client.get.call_args
            assert call_args[1]['params']['annotations'] == 'distance'

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_balanced_route(self, osrm_client_instance):
        """測試平衡路線偏好"""
        locations = [(25.0330, 121.5654), (25.0400, 121.5700)]
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"durations": [[0, 250], [250, 0]]}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_travel_time_matrix(locations, "balanced")
            
            # 驗證結果
            assert result == [[0, 250], [250, 0]]
            # 驗證請求參數包含 duration,distance 註解
            call_args = mock_client.get.call_args
            assert call_args[1]['params']['annotations'] == 'duration,distance'

    @pytest.mark.asyncio
    async def test_get_travel_time_matrix_request_failure(self, osrm_client_instance):
        """測試請求失敗時返回模擬矩陣"""
        locations = [(25.0330, 121.5654), (25.0400, 121.5700)]
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_travel_time_matrix(locations)
            
            # 驗證結果（應該返回模擬矩陣）
            expected = [[0, 300], [300, 0]]
            assert result == expected

    @pytest.mark.asyncio
    async def test_get_route_alternatives_success(self, osrm_client_instance):
        """測試成功獲取替代路線"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        expected_routes = [
            {"duration": 300, "distance": 5000, "weight": 300},
            {"duration": 350, "distance": 4500, "weight": 350}
        ]
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "routes": [
                    {"duration": 300, "distance": 5000, "weight": 300},
                    {"duration": 350, "distance": 4500, "weight": 350}
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_route_alternatives(start, end)
            
            # 驗證結果
            assert result == expected_routes
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_route_alternatives_shortest_preference(self, osrm_client_instance):
        """測試最短路線偏好"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"routes": [{"duration": 200, "distance": 3000, "weight": 200}]}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_route_alternatives(start, end, "shortest")
            
            # 驗證結果
            assert len(result) == 1
            assert result[0]["duration"] == 200
            # 驗證請求參數
            call_args = mock_client.get.call_args
            assert call_args[1]['params']['continue_straight'] == 'false'

    @pytest.mark.asyncio
    async def test_get_route_alternatives_balanced_preference(self, osrm_client_instance):
        """測試平衡路線偏好"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"routes": [{"duration": 250, "distance": 4000, "weight": 250}]}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_route_alternatives(start, end, "balanced")
            
            # 驗證結果
            assert len(result) == 1
            assert result[0]["duration"] == 250
            # 驗證請求參數
            call_args = mock_client.get.call_args
            assert call_args[1]['params']['geometries'] == 'polyline'

    @pytest.mark.asyncio
    async def test_get_route_alternatives_request_failure(self, osrm_client_instance):
        """測試請求失敗時返回空列表"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_route_alternatives(start, end)
            
            # 驗證結果（應該返回空列表）
            assert result == []

    @pytest.mark.asyncio
    async def test_get_route_alternatives_empty_routes(self, osrm_client_instance):
        """測試空路線回應"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"routes": []}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_route_alternatives(start, end)
            
            # 驗證結果
            assert result == []

    @pytest.mark.asyncio
    async def test_get_route_alternatives_missing_fields(self, osrm_client_instance):
        """測試路線回應缺少某些欄位"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {
                "routes": [
                    {"duration": 300},  # 缺少 distance 和 weight
                    {"distance": 5000}  # 缺少 duration 和 weight
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            result = await osrm_client_instance.get_route_alternatives(start, end)
            
            # 驗證結果（應該使用預設值 0）
            expected = [
                {"duration": 300, "distance": 0, "weight": 0},
                {"duration": 0, "distance": 5000, "weight": 0}
            ]
            assert result == expected

    def test_singleton_instance(self):
        """測試單例實例"""
        # 驗證單例實例存在
        assert osrm_client is not None
        assert isinstance(osrm_client, OSRMClient)

    @pytest.mark.asyncio
    async def test_coordinate_formatting(self, osrm_client_instance):
        """測試座標格式化"""
        start = (25.0330, 121.5654)
        end = (25.0400, 121.5700)
        
        with patch('src.itinerary_planner.infrastructure.clients.osrm_client.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.json.return_value = {"routes": []}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # 執行測試
            await osrm_client_instance.get_route_alternatives(start, end)
            
            # 驗證 URL 格式（經度在前，緯度在後）
            call_args = mock_client.get.call_args
            url = call_args[0][0]
            assert "121.5654,25.033;121.57,25.04" in url
