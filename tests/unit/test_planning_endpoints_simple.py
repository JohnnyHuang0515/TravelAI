import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.itinerary_planner.api.v1.endpoints.planning import (
    router,
    handle_itinerary_feedback,
    ProposeRequest,
    FeedbackRequest
)
from src.itinerary_planner.domain.models.itinerary import Itinerary, Day, Visit, Accommodation
from src.itinerary_planner.infrastructure.persistence.orm_models import User


class TestPlanningEndpointsSimple:
    """測試行程規劃端點 - 簡化版本"""

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
        return user

    @pytest.fixture
    def sample_itinerary(self):
        """建立範例行程"""
        visit = Visit(
            place_id="place1",
            name="台北101",
            eta="09:00",
            etd="11:00",
            travel_minutes=30
        )
        
        day = Day(
            date="2024-01-01",
            visits=[visit]
        )
        
        return Itinerary(
            days=[day]
        )

    @pytest.fixture
    def sample_feedback_request(self, sample_itinerary):
        """建立範例回饋請求"""
        return FeedbackRequest(
            session_id="session123",
            itinerary=sample_itinerary,
            feedback_text="請刪除第一天的行程"
        )

    def test_handle_itinerary_feedback_success(self, sample_feedback_request):
        """測試成功處理行程回饋"""
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.greedy_planner') as mock_planner:
            
            # 模擬解析器返回 DSL
            mock_dsl = {"action": "remove_day", "day": 1}
            mock_parser.parse.return_value = mock_dsl
            
            # 模擬規劃器返回更新後的行程
            updated_itinerary = Itinerary(
                trip_id="trip123",
                days=[]
            )
            mock_planner.handle_feedback.return_value = updated_itinerary
            
            result = handle_itinerary_feedback(sample_feedback_request)
            
            assert result == updated_itinerary
            mock_parser.parse.assert_called_once_with("請刪除第一天的行程")
            mock_planner.handle_feedback.assert_called_once_with(sample_feedback_request.itinerary, mock_dsl)

    def test_handle_itinerary_feedback_parse_error(self, sample_feedback_request):
        """測試解析回饋失敗"""
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser:
            # 模擬解析器返回 None
            mock_parser.parse.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                handle_itinerary_feedback(sample_feedback_request)
            
            assert exc_info.value.status_code == 400
            assert "Could not understand the feedback" in str(exc_info.value.detail)

    def test_handle_itinerary_feedback_empty_dsl(self, sample_feedback_request):
        """測試空 DSL 回饋"""
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser:
            # 模擬解析器返回空字典
            mock_parser.parse.return_value = {}
            
            with pytest.raises(HTTPException) as exc_info:
                handle_itinerary_feedback(sample_feedback_request)
            
            assert exc_info.value.status_code == 400
            assert "Could not understand the feedback" in str(exc_info.value.detail)

    def test_handle_itinerary_feedback_planner_error(self, sample_feedback_request):
        """測試規劃器處理錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.greedy_planner') as mock_planner:
            
            # 模擬解析器返回 DSL
            mock_dsl = {"action": "remove_day", "day": 1}
            mock_parser.parse.return_value = mock_dsl
            
            # 模擬規劃器拋出異常
            mock_planner.handle_feedback.side_effect = Exception("規劃器錯誤")
            
            with pytest.raises(Exception) as exc_info:
                handle_itinerary_feedback(sample_feedback_request)
            
            assert "規劃器錯誤" in str(exc_info.value)

    def test_propose_request_model(self):
        """測試 ProposeRequest 模型"""
        request = ProposeRequest(
            session_id="session123",
            text="我想去台北旅遊"
        )
        
        assert request.session_id == "session123"
        assert request.text == "我想去台北旅遊"

    def test_feedback_request_model(self, sample_itinerary):
        """測試 FeedbackRequest 模型"""
        request = FeedbackRequest(
            session_id="session123",
            itinerary=sample_itinerary,
            feedback_text="請修改行程"
        )
        
        assert request.session_id == "session123"
        assert request.itinerary == sample_itinerary
        assert request.feedback_text == "請修改行程"

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == ""
        assert len(router.routes) == 2  # /propose 和 /feedback

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/propose" in route_paths
        assert "/feedback" in route_paths
