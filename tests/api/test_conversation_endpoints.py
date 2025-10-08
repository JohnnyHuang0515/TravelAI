import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.itinerary_planner.api.v1.endpoints.conversation import (
    router,
    chat_with_ai,
    get_conversation_state,
    reset_conversation,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ItineraryCard
)
from src.itinerary_planner.domain.entities.conversation_state import ConversationState, ConversationStateType


class TestConversationEndpoints:
    """測試對話 API 端點"""

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
    def sample_chat_request(self):
        """建立範例聊天請求"""
        return ChatRequest(
            session_id="test_session_123",
            message="我想去台北旅遊",
            conversation_history=[]
        )

    @pytest.fixture
    def sample_chat_message(self):
        """建立範例聊天訊息"""
        return ChatMessage(
            role="user",
            content="我想去台北旅遊",
            timestamp="2023-01-01T10:00:00Z"
        )

    @pytest.fixture
    def sample_conversation_state(self):
        """建立範例對話狀態"""
        return ConversationState(
            session_id="test_session_123",
            state=ConversationStateType.COLLECTING_INFO,
            collected_info={"destination": "台北"},
            conversation_history=[],
            is_complete=False
        )

    @pytest.fixture
    def sample_itinerary_card(self):
        """建立範例行程卡片"""
        return ItineraryCard(
            day=1,
            date="2023-01-01",
            activities=[
                {
                    "name": "台北101",
                    "time": "09:00-11:00",
                    "location": "信義區"
                }
            ],
            total_duration="2小時",
            theme="城市觀光"
        )

    @pytest.mark.asyncio
    async def test_chat_with_ai_success(self, sample_chat_request):
        """測試成功與 AI 對話"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬對話服務回應
            mock_response = {
                "message": "好的，我了解您想去台北旅遊。請告訴我您計劃旅遊幾天？",
                "conversation_state": "collecting_info",
                "is_complete": False
            }
            mock_service.process_message.return_value = mock_response
            
            result = await chat_with_ai(sample_chat_request, mock_db)
            
            assert result["message"] == "好的，我了解您想去台北旅遊。請告訴我您計劃旅遊幾天？"
            assert result["conversation_state"] == "collecting_info"
            assert result["is_complete"] is False
            mock_service.process_message.assert_called_once_with(
                session_id=sample_chat_request.session_id,
                user_message=sample_chat_request.message,
                conversation_history=sample_chat_request.conversation_history
            )

    @pytest.mark.asyncio
    async def test_chat_with_ai_with_itinerary(self, sample_chat_request):
        """測試對話完成並生成行程"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬完成對話並生成行程
            mock_response = {
                "message": "您的台北3日遊行程已生成完成！",
                "conversation_state": "completed",
                "itinerary": {
                    "days": [
                        {
                            "day": 1,
                            "activities": [
                                {"name": "台北101", "time": "09:00-11:00"}
                            ]
                        }
                    ]
                },
                "is_complete": True
            }
            mock_service.process_message.return_value = mock_response
            
            result = await chat_with_ai(sample_chat_request, mock_db)
            
            assert result["message"] == "您的台北3日遊行程已生成完成！"
            assert result["conversation_state"] == "completed"
            assert result["is_complete"] is True
            assert "itinerary" in result

    @pytest.mark.asyncio
    async def test_chat_with_ai_error(self, sample_chat_request):
        """測試對話處理錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬服務錯誤
            mock_service.process_message.side_effect = Exception("服務錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await chat_with_ai(sample_chat_request, mock_db)
            
            assert exc_info.value.status_code == 500
            assert "Chat processing failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_conversation_state_success(self, sample_conversation_state):
        """測試成功獲取對話狀態"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬找到對話狀態
            mock_service.get_conversation_state.return_value = sample_conversation_state
            
            result = await get_conversation_state("test_session_123", mock_db)
            
            assert result["session_id"] == "test_session_123"
            assert result["state"] == ConversationStateType.COLLECTING_INFO
            assert result["collected_info"] == {"destination": "台北"}
            assert result["is_complete"] is False
            mock_service.get_conversation_state.assert_called_once_with("test_session_123")

    @pytest.mark.asyncio
    async def test_get_conversation_state_not_found(self):
        """測試獲取不存在的對話狀態"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬找不到對話狀態
            mock_service.get_conversation_state.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_conversation_state("nonexistent_session", mock_db)
            
            assert exc_info.value.status_code == 500
            assert "Failed to get conversation state" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_conversation_state_error(self):
        """測試獲取對話狀態錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬服務錯誤
            mock_service.get_conversation_state.side_effect = Exception("服務錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_conversation_state("test_session_123", mock_db)
            
            assert exc_info.value.status_code == 500
            assert "Failed to get conversation state" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_reset_conversation_success(self):
        """測試成功重置對話"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬重置成功
            mock_service.reset_conversation.return_value = None
            
            result = await reset_conversation("test_session_123", mock_db)
            
            assert result["message"] == "Conversation reset successfully"
            mock_service.reset_conversation.assert_called_once_with("test_session_123")

    @pytest.mark.asyncio
    async def test_reset_conversation_error(self):
        """測試重置對話錯誤"""
        with patch('src.itinerary_planner.api.v1.endpoints.conversation.ConversationService') as mock_service_class, \
             patch('src.itinerary_planner.api.v1.endpoints.conversation.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # 模擬服務錯誤
            mock_service.reset_conversation.side_effect = Exception("服務錯誤")
            
            with pytest.raises(HTTPException) as exc_info:
                await reset_conversation("test_session_123", mock_db)
            
            assert exc_info.value.status_code == 500
            assert "Failed to reset conversation" in str(exc_info.value.detail)

    def test_chat_message_model(self, sample_chat_message):
        """測試 ChatMessage 模型"""
        assert sample_chat_message.role == "user"
        assert sample_chat_message.content == "我想去台北旅遊"
        assert sample_chat_message.timestamp == "2023-01-01T10:00:00Z"

    def test_chat_request_model(self, sample_chat_request):
        """測試 ChatRequest 模型"""
        assert sample_chat_request.session_id == "test_session_123"
        assert sample_chat_request.message == "我想去台北旅遊"
        assert sample_chat_request.conversation_history == []

    def test_chat_response_model(self):
        """測試 ChatResponse 模型"""
        response = ChatResponse(
            message="測試回應",
            conversation_state="collecting_info",
            is_complete=False
        )
        
        assert response.message == "測試回應"
        assert response.conversation_state == "collecting_info"
        assert response.is_complete is False
        assert response.itinerary is None
        assert response.questions is None

    def test_itinerary_card_model(self, sample_itinerary_card):
        """測試 ItineraryCard 模型"""
        assert sample_itinerary_card.day == 1
        assert sample_itinerary_card.date == "2023-01-01"
        assert len(sample_itinerary_card.activities) == 1
        assert sample_itinerary_card.total_duration == "2小時"
        assert sample_itinerary_card.theme == "城市觀光"

    def test_router_configuration(self):
        """測試路由器配置"""
        assert router.prefix == ""
        assert len(router.routes) == 3  # chat, state, reset

    def test_endpoint_paths(self):
        """測試端點路徑"""
        route_paths = [route.path for route in router.routes]
        assert "/chat" in route_paths
        assert "/state/{session_id}" in route_paths
        assert "/reset/{session_id}" in route_paths

    def test_chat_request_with_history(self):
        """測試帶有對話歷史的聊天請求"""
        history = [
            ChatMessage(role="user", content="我想去台北"),
            ChatMessage(role="assistant", content="好的，請告訴我您計劃旅遊幾天？")
        ]
        
        request = ChatRequest(
            session_id="test_session_456",
            message="3天",
            conversation_history=history
        )
        
        assert request.session_id == "test_session_456"
        assert request.message == "3天"
        assert len(request.conversation_history) == 2
        assert request.conversation_history[0].role == "user"
        assert request.conversation_history[1].role == "assistant"

    def test_chat_response_with_itinerary(self):
        """測試帶有行程的回應"""
        itinerary = {
            "days": [
                {
                    "day": 1,
                    "activities": [
                        {"name": "台北101", "time": "09:00-11:00"}
                    ]
                }
            ]
        }
        
        response = ChatResponse(
            message="行程已生成",
            conversation_state="completed",
            itinerary=itinerary,
            is_complete=True
        )
        
        assert response.message == "行程已生成"
        assert response.conversation_state == "completed"
        assert response.itinerary == itinerary
        assert response.is_complete is True

    def test_chat_response_with_questions(self):
        """測試帶有問題的回應"""
        questions = ["您喜歡什麼類型的景點？", "您的預算範圍是多少？"]
        
        response = ChatResponse(
            message="請回答以下問題",
            conversation_state="collecting_info",
            questions=questions,
            is_complete=False
        )
        
        assert response.message == "請回答以下問題"
        assert response.conversation_state == "collecting_info"
        assert response.questions == questions
        assert response.is_complete is False