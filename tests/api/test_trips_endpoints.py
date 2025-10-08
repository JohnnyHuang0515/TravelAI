"""
Trips API 端點測試
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime, date
import uuid

from src.itinerary_planner.api.v1.endpoints.trips import router, get_current_user, get_trip_service
from src.itinerary_planner.api.v1.schemas.trip import (
    SaveTripRequest,
    UpdateTripRequest,
    CopyTripRequest,
    TripSummaryResponse,
    TripDetailResponse,
    TripListResponse,
    ShareTripResponse,
    MessageResponse
)
from src.itinerary_planner.infrastructure.persistence.orm_models import User, UserTrip


class TestTripsEndpoints:
    """Trips 端點測試類別"""

    @pytest.fixture
    def app(self):
        """創建測試應用程式"""
        app = FastAPI()
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """創建測試客戶端"""
        return TestClient(app)

    @pytest.fixture
    def sample_user(self):
        """樣本用戶"""
        user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            username="testuser",
            provider="email",
            provider_id="test@example.com",
            avatar_url=None,
            profile=None,
            created_at=datetime.now(),
            last_login=datetime.now(),
            is_active=True,
            is_verified=True
        )
        return user

    @pytest.fixture
    def sample_trip(self):
        """樣本行程"""
        trip = UserTrip(
            id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            title="測試行程",
            description="測試描述",
            destination="台北",
            duration_days=2,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 2),
            itinerary_data={"days": [{"day": 1, "visits": []}]},
            is_public=False,
            share_token=None,
            view_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return trip

    @pytest.fixture
    def mock_trip_service(self):
        """模擬行程服務"""
        service = Mock()
        service.save_trip = Mock()
        service.get_user_trips = Mock()
        service.get_trip = Mock()
        service.update_trip = Mock()
        service.delete_trip = Mock()
        service.share_trip = Mock()
        service.get_public_trip = Mock()
        service.copy_trip = Mock()
        return service

    # ============================================================================
    # 行程 CRUD 測試
    # ============================================================================

    def test_save_trip_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功儲存行程"""
        # 設置依賴覆蓋
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.save_trip.return_value = sample_trip
        
        # 準備請求數據
        request_data = {
            "title": "測試行程",
            "description": "測試描述",
            "destination": "台北",
            "itinerary_data": {"days": [{"day": 1, "visits": []}]},
            "is_public": False
        }
        
        # 發送請求
        response = client.post("/trips", json=request_data)
        
        # 驗證響應
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "測試行程"
        assert data["destination"] == "台北"
        
        # 驗證服務調用
        mock_trip_service.save_trip.assert_called_once_with(
            user_id=str(sample_user.id),
            title="測試行程",
            destination="台北",
            itinerary_data={"days": [{"day": 1, "visits": []}]},
            description="測試描述",
            is_public=False
        )

    def test_save_trip_missing_fields(self, client, app, sample_user, mock_trip_service):
        """測試缺少必要欄位"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 缺少必要欄位
        request_data = {
            "title": "測試行程"
            # 缺少 destination 和 itinerary_data
        }
        
        response = client.post("/trips", json=request_data)
        assert response.status_code == 422

    def test_get_my_trips_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功獲取我的行程列表"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.get_user_trips.return_value = {
            "trips": [sample_trip],
            "total": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        
        # 發送請求
        response = client.get("/trips?page=1&page_size=10")
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["trips"]) == 1
        assert data["trips"][0]["title"] == "測試行程"
        
        # 驗證服務調用
        mock_trip_service.get_user_trips.assert_called_once_with(
            user_id=str(sample_user.id),
            page=1,
            page_size=10
        )

    def test_get_my_trips_empty(self, client, app, sample_user, mock_trip_service):
        """測試獲取空的行程列表"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.get_user_trips.return_value = {
            "trips": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        
        response = client.get("/trips")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["trips"]) == 0

    def test_get_trip_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功獲取行程詳情"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.get_trip.return_value = sample_trip
        
        # 發送請求
        response = client.get(f"/trips/{sample_trip.id}")
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_trip.id)
        assert data["title"] == "測試行程"
        
        # 驗證服務調用
        mock_trip_service.get_trip.assert_called_once_with(
            str(sample_trip.id), str(sample_user.id)
        )

    def test_get_trip_not_found(self, client, app, sample_user, mock_trip_service):
        """測試獲取不存在的行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.get_trip.return_value = None
        
        response = client.get("/trips/non-existent-id")
        assert response.status_code == 404
        assert "行程不存在" in response.json()["detail"]

    def test_get_trip_permission_denied(self, client, app, sample_user, mock_trip_service):
        """測試無權限獲取行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值 - 拋出權限錯誤
        mock_trip_service.get_trip.side_effect = PermissionError("無權限")
        
        response = client.get("/trips/some-id")
        assert response.status_code == 403
        assert "無權限存取此行程" in response.json()["detail"]

    def test_update_trip_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功更新行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        updated_trip = sample_trip
        updated_trip.title = "更新的行程"
        mock_trip_service.update_trip.return_value = updated_trip
        
        # 準備請求數據
        request_data = {
            "title": "更新的行程",
            "description": "更新的描述"
        }
        
        # 發送請求
        response = client.put(f"/trips/{sample_trip.id}", json=request_data)
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新的行程"
        
        # 驗證服務調用
        mock_trip_service.update_trip.assert_called_once_with(
            trip_id=str(sample_trip.id),
            user_id=str(sample_user.id),
            title="更新的行程",
            description="更新的描述"
        )

    def test_update_trip_not_found(self, client, app, sample_user, mock_trip_service):
        """測試更新不存在的行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.update_trip.return_value = None
        
        request_data = {"title": "新標題"}
        response = client.put("/trips/non-existent-id", json=request_data)
        
        assert response.status_code == 404
        assert "行程不存在" in response.json()["detail"]

    def test_delete_trip_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功刪除行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.delete_trip.return_value = True
        
        # 發送請求
        response = client.delete(f"/trips/{sample_trip.id}")
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert "行程已刪除" in data["message"]
        
        # 驗證服務調用
        mock_trip_service.delete_trip.assert_called_once_with(
            trip_id=str(sample_trip.id),
            user_id=str(sample_user.id)
        )

    def test_delete_trip_not_found(self, client, app, sample_user, mock_trip_service):
        """測試刪除不存在的行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.delete_trip.return_value = False
        
        response = client.delete("/trips/non-existent-id")
        assert response.status_code == 404
        assert "行程不存在" in response.json()["detail"]

    # ============================================================================
    # 行程分享與複製測試
    # ============================================================================

    def test_share_trip_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功分享行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.share_trip.return_value = "share_token_123"
        
        # 發送請求
        response = client.post(f"/trips/{sample_trip.id}/share")
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["share_token"] == "share_token_123"
        assert "/trips/public/share_token_123" in data["share_url"]
        
        # 驗證服務調用
        mock_trip_service.share_trip.assert_called_once_with(
            trip_id=str(sample_trip.id),
            user_id=str(sample_user.id)
        )

    def test_share_trip_not_found(self, client, app, sample_user, mock_trip_service):
        """測試分享不存在的行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.share_trip.return_value = None
        
        response = client.post("/trips/non-existent-id/share")
        assert response.status_code == 404
        assert "行程不存在" in response.json()["detail"]

    def test_get_public_trip_success(self, client, app, sample_trip, mock_trip_service):
        """測試成功獲取公開行程"""
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.get_public_trip.return_value = sample_trip
        
        # 發送請求
        response = client.get("/trips/public/share_token_123")
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_trip.id)
        assert data["title"] == "測試行程"
        
        # 驗證服務調用
        mock_trip_service.get_public_trip.assert_called_once_with("share_token_123")

    def test_get_public_trip_not_found(self, client, app, mock_trip_service):
        """測試獲取不存在的公開行程"""
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.get_public_trip.return_value = None
        
        response = client.get("/trips/public/invalid_token")
        assert response.status_code == 404
        assert "分享連結無效" in response.json()["detail"]

    def test_copy_trip_success(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試成功複製行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        new_trip = sample_trip
        new_trip.id = str(uuid.uuid4())
        new_trip.title = "複製的行程"
        mock_trip_service.copy_trip.return_value = new_trip
        
        # 準備請求數據
        request_data = {"new_title": "複製的行程"}
        
        # 發送請求
        response = client.post(f"/trips/{sample_trip.id}/copy", json=request_data)
        
        # 驗證響應
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "複製的行程"
        
        # 驗證服務調用
        mock_trip_service.copy_trip.assert_called_once_with(
            trip_id=str(sample_trip.id),
            new_user_id=str(sample_user.id),
            new_title="複製的行程"
        )

    def test_copy_trip_not_found(self, client, app, sample_user, mock_trip_service):
        """測試複製不存在的行程"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        mock_trip_service.copy_trip.return_value = None
        
        request_data = {"new_title": "新標題"}
        response = client.post("/trips/non-existent-id/copy", json=request_data)
        
        assert response.status_code == 404
        assert "行程不存在" in response.json()["detail"]

    def test_copy_trip_missing_title(self, client, app, sample_user, sample_trip, mock_trip_service):
        """測試複製行程時缺少標題"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 設置模擬返回值
        new_trip = sample_trip
        new_trip.id = str(uuid.uuid4())
        mock_trip_service.copy_trip.return_value = new_trip
        
        # 不提供 new_title
        request_data = {}
        
        response = client.post(f"/trips/{sample_trip.id}/copy", json=request_data)
        assert response.status_code == 200  # CopyTripRequest 的 new_title 是可選的

    # ============================================================================
    # 配置和模型測試
    # ============================================================================

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == "/trips"
        assert len(router.routes) == 8  # save, get_my_trips, get_trip, update, delete, share, get_public, copy

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/trips" in route_paths  # POST /trips
        assert "/trips/{trip_id}" in route_paths  # GET, PUT, DELETE
        assert "/trips/{trip_id}/share" in route_paths
        assert "/trips/public/{share_token}" in route_paths
        assert "/trips/{trip_id}/copy" in route_paths

    def test_save_trip_request_model(self):
        """測試 SaveTripRequest 模型"""
        request = SaveTripRequest(
            title="測試行程",
            destination="台北",
            itinerary_data={"days": []},
            description="測試描述",
            is_public=False
        )
        assert request.title == "測試行程"
        assert request.destination == "台北"
        assert request.is_public is False

    def test_update_trip_request_model(self):
        """測試 UpdateTripRequest 模型"""
        request = UpdateTripRequest(
            title="新標題",
            description="新描述"
        )
        assert request.title == "新標題"
        assert request.description == "新描述"
        assert request.itinerary_data is None

    def test_copy_trip_request_model(self):
        """測試 CopyTripRequest 模型"""
        request = CopyTripRequest(new_title="複製的行程")
        assert request.new_title == "複製的行程"

    def test_message_response_model(self):
        """測試 MessageResponse 模型"""
        response = MessageResponse(message="測試訊息")
        assert response.message == "測試訊息"

    def test_share_trip_response_model(self):
        """測試 ShareTripResponse 模型"""
        response = ShareTripResponse(
            share_url="/trips/public/abc123",
            share_token="abc123"
        )
        assert response.share_url == "/trips/public/abc123"
        assert response.share_token == "abc123"
