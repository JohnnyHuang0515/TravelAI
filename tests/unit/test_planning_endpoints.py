import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.itinerary_planner.api.v1.endpoints.planning import (
    router,
    propose_itinerary,
    handle_itinerary_feedback,
    ProposeRequest,
    FeedbackRequest
)
from src.itinerary_planner.domain.models.itinerary import Itinerary, Day, Visit, Accommodation
from src.itinerary_planner.infrastructure.persistence.orm_models import User


class TestPlanningEndpoints:
    """測試行程規劃端點"""

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
        accommodation = Accommodation(
            place_id="acc1",
            name="台北君悅酒店",
            check_in="15:00",
            check_out="11:00",
            nights=1,
            type="hotel"
        )
        day = Day(
            date="2024-01-01",
            visits=[visit],
            accommodation=accommodation
        )
        return Itinerary(days=[day])

    @pytest.fixture
    def sample_propose_request(self):
        """建立範例提案請求"""
        return ProposeRequest(
            session_id="session123",
            text="我想去台北三天兩夜"
        )

    @pytest.fixture
    def sample_feedback_request(self, sample_itinerary):
        """建立範例回饋請求"""
        return FeedbackRequest(
            session_id="session123",
            itinerary=sample_itinerary,
            feedback_text="請刪除第一天的行程"
        )

    @pytest.mark.asyncio
    async def test_propose_itinerary_success(self, sample_propose_request, sample_user, sample_itinerary):
        """測試成功提案行程"""
        # 模擬 LangGraph 結果
        mock_result = {
            "session_id": "session123",
            "is_info_complete": True,
            "itinerary": sample_itinerary,
            "error": None
        }
        
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.UserPreferenceRepository') as mock_pref_repo, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(return_value=mock_result)
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_pref_repo_instance = Mock()
            mock_pref_repo.return_value = mock_pref_repo_instance
            mock_pref_repo_instance.get_by_user_id.return_value = None
            
            result = await propose_itinerary(sample_propose_request, sample_user, mock_db)
            
            assert result == sample_itinerary
            mock_graph.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_propose_itinerary_with_user_preferences(self, sample_propose_request, sample_user, sample_itinerary):
        """測試使用使用者偏好提案行程"""
        # 模擬使用者偏好
        mock_preferences = Mock()
        mock_preferences.favorite_themes = ["美食", "文化"]
        mock_preferences.travel_pace = "relaxed"
        mock_preferences.budget_level = "luxury"
        mock_preferences.default_daily_start = "10:00"
        mock_preferences.default_daily_end = "20:00"
        
        # 模擬 LangGraph 結果
        mock_result = {
            "session_id": "session123",
            "is_info_complete": True,
            "itinerary": sample_itinerary,
            "error": None
        }
        
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.UserPreferenceRepository') as mock_pref_repo, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(return_value=mock_result)
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_pref_repo_instance = Mock()
            mock_pref_repo.return_value = mock_pref_repo_instance
            mock_pref_repo_instance.get_by_user_id.return_value = mock_preferences
            
            result = await propose_itinerary(sample_propose_request, sample_user, mock_db)
            
            assert result == sample_itinerary
            mock_pref_repo_instance.get_by_user_id.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_propose_itinerary_guest_user(self, sample_propose_request, sample_itinerary):
        """測試訪客使用者提案行程"""
        # 模擬 LangGraph 結果
        mock_result = {
            "session_id": "session123",
            "is_info_complete": True,
            "itinerary": sample_itinerary,
            "error": None
        }
        
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(return_value=mock_result)
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            result = await propose_itinerary(sample_propose_request, None, mock_db)
            
            assert result == sample_itinerary
            mock_graph.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_propose_itinerary_incomplete_info(self, sample_propose_request, sample_user):
        """測試資訊不完整時的回應"""
        # 模擬 LangGraph 結果 - 資訊不完整
        mock_result = {
            "session_id": "session123",
            "is_info_complete": False,
            "ai_response": "請告訴我您想去哪裡旅遊？",
            "next_question": "您希望什麼時候出發？",
            "collected_info": {"destination": "台北"},
            "itinerary": None,
            "error": None
        }
        
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.UserPreferenceRepository') as mock_pref_repo, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(return_value=mock_result)
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_pref_repo_instance = Mock()
            mock_pref_repo.return_value = mock_pref_repo_instance
            mock_pref_repo_instance.get_by_user_id.return_value = None
            
            result = await propose_itinerary(sample_propose_request, sample_user, mock_db)
            
            assert result["session_id"] == "session123"
            assert result["message"] == "請告訴我您想去哪裡旅遊？"
            assert result["is_complete"] is False
            assert result["next_question"] == "您希望什麼時候出發？"
            assert result["collected_info"] == {"destination": "台北"}
            assert result["days"] == []

    @pytest.mark.asyncio
    async def test_propose_itinerary_with_error(self, sample_propose_request, sample_user):
        """測試提案行程時發生錯誤"""
        # 模擬 LangGraph 結果 - 有錯誤
        mock_result = {
            "session_id": "session123",
            "is_info_complete": False,
            "itinerary": None,
            "error": "無法找到合適的地點"
        }
        
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.UserPreferenceRepository') as mock_pref_repo, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(return_value=mock_result)
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_pref_repo_instance = Mock()
            mock_pref_repo.return_value = mock_pref_repo_instance
            mock_pref_repo_instance.get_by_user_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await propose_itinerary(sample_propose_request, sample_user, mock_db)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "無法找到合適的地點"

    @pytest.mark.asyncio
    async def test_propose_itinerary_no_itinerary(self, sample_propose_request, sample_user):
        """測試提案行程時沒有生成行程"""
        # 模擬 LangGraph 結果 - 沒有行程
        mock_result = {
            "session_id": "session123",
            "is_info_complete": True,
            "itinerary": None,
            "error": None
        }
        
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.UserPreferenceRepository') as mock_pref_repo, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(return_value=mock_result)
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_pref_repo_instance = Mock()
            mock_pref_repo.return_value = mock_pref_repo_instance
            mock_pref_repo_instance.get_by_user_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await propose_itinerary(sample_propose_request, sample_user, mock_db)
            
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "Failed to generate itinerary"

    @pytest.mark.asyncio
    async def test_propose_itinerary_exception(self, sample_propose_request, sample_user):
        """測試提案行程時發生異常"""
        with patch('src.itinerary_planner.application.graph.app_graph') as mock_graph, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.UserPreferenceRepository') as mock_pref_repo, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.get_db') as mock_get_db:
            
            mock_graph.ainvoke = AsyncMock(side_effect=Exception("Database connection failed"))
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_pref_repo_instance = Mock()
            mock_pref_repo.return_value = mock_pref_repo_instance
            mock_pref_repo_instance.get_by_user_id.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await propose_itinerary(sample_propose_request, sample_user, mock_db)
            
            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "Database connection failed"

    def test_handle_itinerary_feedback_success(self, sample_feedback_request, sample_itinerary):
        """測試成功處理行程回饋"""
        # 模擬回饋解析器結果
        mock_dsl = {
            "op": "DROP",
            "target": {"day": 1}
        }
        
        # 模擬更新後的行程
        updated_itinerary = Itinerary(days=[])
        
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.greedy_planner') as mock_planner:
            
            mock_parser.parse.return_value = mock_dsl
            mock_planner.handle_feedback.return_value = updated_itinerary
            
            result = handle_itinerary_feedback(sample_feedback_request)
            
            assert result == updated_itinerary
            mock_parser.parse.assert_called_once_with("請刪除第一天的行程")
            mock_planner.handle_feedback.assert_called_once_with(sample_itinerary, mock_dsl)

    def test_handle_itinerary_feedback_parse_error(self, sample_feedback_request):
        """測試回饋解析錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser:
            mock_parser.parse.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                handle_itinerary_feedback(sample_feedback_request)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Could not understand the feedback."

    def test_handle_itinerary_feedback_empty_dsl(self, sample_feedback_request):
        """測試回饋解析為空 DSL"""
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser:
            mock_parser.parse.return_value = {}
            
            with pytest.raises(HTTPException) as exc_info:
                handle_itinerary_feedback(sample_feedback_request)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Could not understand the feedback."

    def test_handle_itinerary_feedback_planner_error(self, sample_feedback_request, sample_itinerary):
        """測試行程規劃器錯誤"""
        mock_dsl = {
            "op": "DROP",
            "target": {"day": 1}
        }
        
        with patch('src.itinerary_planner.api.v1.endpoints.planning.feedback_parser') as mock_parser, \
             patch('src.itinerary_planner.api.v1.endpoints.planning.greedy_planner') as mock_planner:
            
            mock_parser.parse.return_value = mock_dsl
            mock_planner.handle_feedback.side_effect = Exception("Planning error")
            
            with pytest.raises(Exception) as exc_info:
                handle_itinerary_feedback(sample_feedback_request)
            
            assert str(exc_info.value) == "Planning error"

    def test_propose_request_model(self, sample_propose_request):
        """測試提案請求模型"""
        assert sample_propose_request.session_id == "session123"
        assert sample_propose_request.text == "我想去台北三天兩夜"

    def test_feedback_request_model(self, sample_feedback_request, sample_itinerary):
        """測試回饋請求模型"""
        assert sample_feedback_request.session_id == "session123"
        assert sample_feedback_request.itinerary == sample_itinerary
        assert sample_feedback_request.feedback_text == "請刪除第一天的行程"

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router is not None
        assert len(router.routes) == 2  # 兩個端點

    def test_endpoint_paths(self):
        """測試端點路徑"""
        routes = [route.path for route in router.routes]
        assert "/propose" in routes
        assert "/feedback" in routes
