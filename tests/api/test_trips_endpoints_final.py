"""
行程 API 端點測試（最終修復版）
使用 FastAPI 的 dependency override 機制
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import uuid4
import datetime

from src.itinerary_planner.api.v1.endpoints.trips import router, get_trip_service
from src.itinerary_planner.api.v1.dependencies.auth import get_current_user
from tests.test_orm_models import User, Trip


class TestTripsEndpointsFinal:
    """行程 API 端點測試類別（最終修復版）"""
    
    @pytest.fixture
    def app(self):
        """建立 FastAPI 應用程式實例"""
        app = FastAPI()
        app.include_router(router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """建立測試客戶端"""
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    @pytest.fixture
    def sample_user(self):
        """測試用的使用者"""
        from src.itinerary_planner.infrastructure.persistence.orm_models import User
        user = User()
        user.id = str(uuid4())
        user.email = "test@example.com"
        user.username = "testuser"
        user.is_active = True
        user.is_verified = True
        user.provider = "email"
        user.created_at = datetime.datetime.now(datetime.timezone.utc)
        user.last_login = datetime.datetime.now(datetime.timezone.utc)
        user.avatar_url = None
        user.profile = None
        return user
    
    @pytest.fixture
    def sample_trip(self):
        """測試用的行程"""
        from src.itinerary_planner.infrastructure.persistence.orm_models import UserTrip
        trip = UserTrip()
        trip.id = str(uuid4())
        trip.user_id = str(uuid4())
        trip.title = "台北三日遊"
        trip.destination = "台北"
        trip.duration_days = 3
        trip.itinerary_data = {"days": []}
        trip.is_public = False
        trip.share_token = None
        trip.description = "台北旅遊行程"
        trip.start_date = None
        trip.end_date = None
        trip.view_count = 0
        trip.created_at = datetime.datetime.now(datetime.timezone.utc)
        trip.updated_at = datetime.datetime.now(datetime.timezone.utc)
        return trip
    
    @pytest.fixture
    def mock_trip_service(self, sample_trip):
        """Mock 行程服務"""
        service = Mock()
        service.save_trip.return_value = sample_trip
        service.get_user_trips.return_value = {"trips": [sample_trip], "total": 1, "page": 1, "page_size": 10, "total_pages": 1}
        service.get_trip.return_value = sample_trip
        service.update_trip.return_value = sample_trip
        service.delete_trip.return_value = True
        service.share_trip.return_value = "abc123"
        service.get_public_trip.return_value = sample_trip
        service.copy_trip.return_value = sample_trip
        return service
    
    def test_save_trip_success(self, app, client, sample_user, sample_trip, mock_trip_service):
        """測試成功儲存行程"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料
        request_data = {
            "title": "台北三日遊",
            "destination": "台北",
            "itinerary_data": {"days": []},
            "description": "台北旅遊行程",
            "is_public": False
        }
        
        # 執行測試
        response = client.post("/trips", json=request_data)
        
        # 驗證結果
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["title"] == "台北三日遊"
        assert data["destination"] == "台北"
        mock_trip_service.save_trip.assert_called_once_with(
            user_id=sample_user.id,
            title="台北三日遊",
            destination="台北",
            itinerary_data={"days": []},
            description="台北旅遊行程",
            is_public=False
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_save_trip_validation_error(self, app, client, sample_user, mock_trip_service):
        """測試儲存行程時驗證錯誤"""
        # 覆蓋依賴
        mock_trip_service.save_trip.side_effect = ValueError("行程資料無效")
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料
        request_data = {
            "title": "",  # 空標題
            "destination": "台北",
            "itinerary_data": {"days": []},
            "is_public": False
        }
        
        # 執行測試
        response = client.post("/trips", json=request_data)
        
        # 驗證結果
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # FastAPI 返回詳細的驗證錯誤列表
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) > 0
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_user_trips_success(self, app, client, sample_user, sample_trip, mock_trip_service):
        """測試成功取得使用者行程列表"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get("/trips?page=1&page_size=10")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "trips" in data
        assert len(data["trips"]) == 1
        assert data["trips"][0]["id"] == sample_trip.id
        assert data["trips"][0]["title"] == "台北三日遊"
        mock_trip_service.get_user_trips.assert_called_once_with(
            user_id=sample_user.id,
            page=1,
            page_size=10
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_user_trips_empty(self, app, client, sample_user, mock_trip_service):
        """測試取得使用者行程列表為空"""
        # 覆蓋依賴
        mock_trip_service.get_user_trips.return_value = {"trips": [], "total": 0, "page": 1, "page_size": 10, "total_pages": 0}
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get("/trips")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "trips" in data
        assert len(data["trips"]) == 0
        mock_trip_service.get_user_trips.assert_called_once_with(
            user_id=sample_user.id,
            page=1,
            page_size=10
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_trip_success_owner(self, app, client, sample_user, sample_trip, mock_trip_service):
        """測試成功取得自己的行程"""
        # 覆蓋依賴
        sample_trip.user_id = sample_user.id  # 設為行程擁有者
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get(f"/trips/{sample_trip.id}")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["title"] == "台北三日遊"
        mock_trip_service.get_trip.assert_called_once_with(
            sample_trip.id,
            sample_user.id
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_trip_success_public(self, app, client, sample_user, sample_trip, mock_trip_service):
        """測試成功取得公開行程"""
        # 覆蓋依賴
        sample_trip.is_public = True  # 設為公開行程
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get(f"/trips/{sample_trip.id}")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["title"] == "台北三日遊"
        mock_trip_service.get_trip.assert_called_once_with(
            sample_trip.id,
            sample_user.id
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_trip_not_found(self, app, client, sample_user, mock_trip_service):
        """測試取得不存在的行程"""
        # 覆蓋依賴
        mock_trip_service.get_trip.return_value = None
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get(f"/trips/{str(uuid4())}")
        
        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "行程不存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_trip_permission_denied(self, app, client, sample_user, mock_trip_service):
        """測試取得無權限的行程"""
        # 覆蓋依賴
        mock_trip_service.get_trip.side_effect = PermissionError("無權限存取此行程")
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get(f"/trips/{str(uuid4())}")
        
        # 驗證結果
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "無權限存取此行程" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_update_trip_success(self, app, client, sample_user, sample_trip, mock_trip_service):
        """測試成功更新行程"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料
        request_data = {
            "title": "更新後的台北三日遊",
            "description": "更新後的描述"
        }
        
        # 執行測試
        response = client.put(f"/trips/{sample_trip.id}", json=request_data)
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["title"] == "台北三日遊"  # 原始標題
        mock_trip_service.update_trip.assert_called_once_with(
            trip_id=sample_trip.id,
            user_id=sample_user.id,
            title="更新後的台北三日遊",
            description="更新後的描述"
        )
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_update_trip_not_found(self, app, client, sample_user, mock_trip_service):
        """測試更新不存在的行程"""
        # 覆蓋依賴
        mock_trip_service.update_trip.return_value = None
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料
        request_data = {
            "title": "更新後的標題"
        }
        
        # 執行測試
        response = client.put(f"/trips/{str(uuid4())}", json=request_data)
        
        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "行程不存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_delete_trip_success(self, app, client, sample_user, mock_trip_service):
        """測試成功刪除行程"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.delete(f"/trips/{str(uuid4())}")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "行程已刪除" in data["message"]
        mock_trip_service.delete_trip.assert_called_once()
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_delete_trip_not_found(self, app, client, sample_user, mock_trip_service):
        """測試刪除不存在的行程"""
        # 覆蓋依賴
        mock_trip_service.delete_trip.return_value = False
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.delete(f"/trips/{str(uuid4())}")
        
        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "行程不存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_share_trip_success(self, app, client, sample_user, mock_trip_service):
        """測試成功分享行程"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.post(f"/trips/{str(uuid4())}/share")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert "share_token" in data
        assert data["share_token"] == "abc123"
        mock_trip_service.share_trip.assert_called_once()
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_share_trip_not_found(self, app, client, sample_user, mock_trip_service):
        """測試分享不存在的行程"""
        # 覆蓋依賴
        mock_trip_service.share_trip.return_value = None
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.post(f"/trips/{str(uuid4())}/share")
        
        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "行程不存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_public_trip_success(self, app, client, sample_trip, mock_trip_service):
        """測試成功取得公開行程"""
        # 覆蓋依賴
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get(f"/trips/public/{str(uuid4())}")
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["title"] == "台北三日遊"
        mock_trip_service.get_public_trip.assert_called_once()
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_get_public_trip_not_found(self, app, client, mock_trip_service):
        """測試取得不存在的公開行程"""
        # 覆蓋依賴
        mock_trip_service.get_public_trip.return_value = None
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 執行測試
        response = client.get(f"/trips/public/{str(uuid4())}")
        
        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "分享連結無效或行程不存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_copy_trip_success(self, app, client, sample_user, sample_trip, mock_trip_service):
        """測試成功複製行程"""
        # 覆蓋依賴
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料
        request_data = {
            "new_title": "複製的台北三日遊"
        }
        
        # 執行測試
        response = client.post(f"/trips/{str(uuid4())}/copy", json=request_data)
        
        # 驗證結果
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_trip.id
        assert data["title"] == "台北三日遊"
        mock_trip_service.copy_trip.assert_called_once()
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_copy_trip_not_found(self, app, client, sample_user, mock_trip_service):
        """測試複製不存在的行程"""
        # 覆蓋依賴
        mock_trip_service.copy_trip.return_value = None
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料
        request_data = {
            "new_title": "複製的行程"
        }
        
        # 執行測試
        response = client.post(f"/trips/{str(uuid4())}/copy", json=request_data)
        
        # 驗證結果
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "行程不存在" in data["detail"]
        
        # 清理覆蓋
        app.dependency_overrides.clear()
    
    def test_save_trip_missing_fields(self, app, client, sample_user):
        """測試儲存行程時缺少必要欄位"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        
        # 準備請求資料（缺少必要欄位）
        request_data = {
            "title": "台北三日遊"
            # 缺少 destination 和 itinerary_data
        }
        
        # 執行測試
        response = client.post("/trips", json=request_data)
        
        # 驗證結果
        assert response.status_code == 422  # Validation error
        
        app.dependency_overrides.clear()
    
    def test_update_trip_missing_fields(self, app, client, sample_user, mock_trip_service):
        """測試更新行程時缺少必要欄位"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料（空資料）
        request_data = {}
        
        # 執行測試
        response = client.put(f"/trips/{str(uuid4())}", json=request_data)
        
        # 驗證結果 - 空請求應該返回 200（所有欄位都是可選的）
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        
        app.dependency_overrides.clear()
    
    def test_copy_trip_missing_title(self, app, client, sample_user, mock_trip_service):
        """測試複製行程時缺少標題"""
        app.dependency_overrides[get_current_user] = lambda: sample_user
        app.dependency_overrides[get_trip_service] = lambda: mock_trip_service
        
        # 準備請求資料（缺少 new_title）
        request_data = {}
        
        # 執行測試
        response = client.post(f"/trips/{str(uuid4())}/copy", json=request_data)
        
        # 驗證結果 - 空請求應該返回 200（new_title 是可選的）
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        
        app.dependency_overrides.clear()
    
    def test_get_trips_without_auth(self, client):
        """測試未認證時取得行程列表"""
        # 執行測試（沒有認證）
        response = client.get("/trips")
        
        # 驗證結果
        assert response.status_code == 401  # Unauthorized
