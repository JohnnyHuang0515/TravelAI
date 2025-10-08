import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json

from src.itinerary_planner.main import app
from src.itinerary_planner.application.services.unified_conversation_engine import ConversationIntent


class TestUnifiedConversationEndpoints:
    """統一對話API端點測試"""
    
    @pytest.fixture
    def client(self):
        """創建測試客戶端"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_services(self):
        """模擬服務依賴"""
        with patch('src.itinerary_planner.api.v1.endpoints.unified_conversation.get_conversation_engine') as mock_engine, \
             patch('src.itinerary_planner.api.v1.endpoints.unified_conversation.get_performance_optimizer') as mock_optimizer:
            
            # 模擬對話引擎
            mock_engine_instance = AsyncMock()
            mock_engine_instance.process_message = AsyncMock()
            mock_engine_instance.get_conversation_state = AsyncMock()
            mock_engine_instance.reset_conversation = AsyncMock()
            mock_engine.return_value = mock_engine_instance
            
            # 模擬性能優化器
            mock_optimizer_instance = Mock()
            mock_optimizer_instance.measure_performance = lambda x: lambda f: f
            mock_optimizer_instance.get_cached_result = Mock(return_value=None)
            mock_optimizer_instance.cache_result = Mock()
            mock_optimizer_instance.invalidate_cache = Mock()
            mock_optimizer_instance.cleanup_expired_cache = Mock()
            mock_optimizer_instance.optimize_memory_usage = Mock()
            mock_optimizer_instance.get_performance_report = Mock()
            mock_optimizer_instance.health_check = AsyncMock()
            mock_optimizer.return_value = mock_optimizer_instance
            
            yield {
                'conversation_engine': mock_engine_instance,
                'performance_optimizer': mock_optimizer_instance
            }
    
    def test_chat_endpoint_success(self, client, mock_services):
        """測試聊天端點成功情況"""
        # 設置模擬回應
        mock_response = {
            "session_id": "test_session",
            "message": "您好！我是您的旅遊助手，請告訴我您想去哪裡旅遊？",
            "intent": "greeting",
            "suggestions": ["告訴我您想去哪裡旅遊"],
            "collected_info": {},
            "is_complete": False,
            "confidence_score": 0.9,
            "turn_count": 1,
            "timestamp": "2024-01-01T10:00:00"
        }
        
        mock_services['conversation_engine'].process_message.return_value = mock_response
        
        # 發送請求
        response = client.post("/v1/conversation/chat", json={
            "session_id": "test_session",
            "message": "你好",
            "conversation_history": [],
            "user_preferences": {},
            "context": {}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session"
        assert data["intent"] == "greeting"
        assert data["is_complete"] == False
        
        # 驗證服務被調用
        mock_services['conversation_engine'].process_message.assert_called_once()
    
    def test_chat_endpoint_error(self, client, mock_services):
        """測試聊天端點錯誤情況"""
        # 設置模擬錯誤
        mock_services['conversation_engine'].process_message.side_effect = Exception("Test error")
        
        response = client.post("/v1/conversation/chat", json={
            "session_id": "test_session",
            "message": "你好"
        })
        
        assert response.status_code == 500
        assert "Chat processing failed" in response.json()["detail"]
    
    def test_message_endpoint(self, client, mock_services):
        """測試訊息端點"""
        mock_response = {
            "session_id": "test_session",
            "message": "好的，我了解了",
            "intent": "provide_info",
            "suggestions": [],
            "collected_info": {"destination": "台北"},
            "is_complete": False,
            "confidence_score": 0.8,
            "turn_count": 2,
            "timestamp": "2024-01-01T10:01:00"
        }
        
        mock_services['conversation_engine'].process_message.return_value = mock_response
        
        response = client.post("/v1/conversation/message", json={
            "session_id": "test_session",
            "message": "我想去台北",
            "metadata": {"source": "test"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "provide_info"
        assert "台北" in str(data["collected_info"])
    
    def test_get_conversation_state_success(self, client, mock_services):
        """測試獲取對話狀態成功"""
        mock_state = {
            "session_id": "test_session",
            "current_intent": "provide_info",
            "collected_info": {"destination": "台北", "duration": 3},
            "conversation_history": [
                {"role": "user", "content": "我想去台北", "timestamp": "2024-01-01T10:00:00"},
                {"role": "assistant", "content": "好的", "timestamp": "2024-01-01T10:01:00"}
            ],
            "confidence_score": 0.8,
            "last_activity": "2024-01-01T10:01:00",
            "turn_count": 2
        }
        
        mock_services['conversation_engine'].get_conversation_state.return_value = mock_state
        
        response = client.get("/v1/conversation/state/test_session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session"
        assert data["current_intent"] == "provide_info"
        assert data["turn_count"] == 2
    
    def test_get_conversation_state_not_found(self, client, mock_services):
        """測試獲取對話狀態不存在"""
        mock_services['conversation_engine'].get_conversation_state.return_value = None
        
        response = client.get("/v1/conversation/state/nonexistent_session")
        
        assert response.status_code == 404
        assert "Conversation not found" in response.json()["detail"]
    
    def test_reset_conversation_success(self, client, mock_services):
        """測試重置對話成功"""
        mock_services['conversation_engine'].reset_conversation.return_value = True
        
        response = client.post("/v1/conversation/reset/test_session")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Conversation reset successfully"
        
        mock_services['conversation_engine'].reset_conversation.assert_called_once_with("test_session")
    
    def test_reset_conversation_failure(self, client, mock_services):
        """測試重置對話失敗"""
        mock_services['conversation_engine'].reset_conversation.return_value = False
        
        response = client.post("/v1/conversation/reset/test_session")
        
        assert response.status_code == 500
        assert "Failed to reset conversation" in response.json()["detail"]
    
    def test_analyze_message(self, client, mock_services):
        """測試分析訊息端點"""
        with patch('src.itinerary_planner.api.v1.endpoints.unified_conversation.get_intelligent_understanding') as mock_understanding:
            mock_understanding_instance = AsyncMock()
            mock_understanding_instance.analyze_message.return_value = {
                "intent": {"type": "provide_info", "confidence": 0.9},
                "entities": [],
                "sentiment": {"sentiment": "positive", "confidence": 0.8},
                "contextual_info": {"topic": "planning"},
                "confidence": 0.85,
                "processed_at": "2024-01-01T10:00:00"
            }
            mock_understanding.return_value = mock_understanding_instance
            
            response = client.post("/v1/conversation/analyze", json={
                "session_id": "test_session",
                "message": "我想去台北旅遊",
                "metadata": {"source": "test"}
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test_session"
            assert "analysis" in data
    
    def test_get_performance_report(self, client, mock_services):
        """測試獲取性能報告"""
        mock_report = {
            "summary": {
                "total_operations": 100,
                "average_execution_time": 0.5,
                "overall_cache_hit_rate": 0.7,
                "total_errors": 2
            },
            "operation_stats": {
                "chat": {"total_calls": 50, "avg_time": 0.3},
                "analyze": {"total_calls": 30, "avg_time": 0.8}
            },
            "cache_stats": {
                "memory_cache_size": 150,
                "max_memory_cache_size": 1000
            },
            "generated_at": "2024-01-01T10:00:00"
        }
        
        mock_services['performance_optimizer'].get_performance_report.return_value = mock_report
        
        response = client.get("/v1/conversation/performance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_operations"] == 100
        assert data["summary"]["overall_cache_hit_rate"] == 0.7
    
    @pytest.mark.asyncio
    async def test_health_check(self, client, mock_services):
        """測試健康檢查"""
        mock_health = {
            "timestamp": "2024-01-01T10:00:00",
            "status": "healthy",
            "components": {
                "redis": {"status": "healthy", "response_time": 0.001},
                "database": {"status": "healthy", "response_time": 0.005},
                "memory_cache": {"status": "healthy", "usage": 50, "max_size": 1000}
            }
        }
        
        mock_services['performance_optimizer'].health_check.return_value = mock_health
        
        response = client.get("/v1/conversation/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
    
    def test_invalidate_cache(self, client, mock_services):
        """測試快取失效"""
        response = client.post("/v1/conversation/cache/invalidate", params={
            "cache_type": "conversation_context",
            "key": "test_session"
        })
        
        assert response.status_code == 200
        assert "Cache invalidation scheduled" in response.json()["message"]
    
    def test_cleanup_cache(self, client, mock_services):
        """測試快取清理"""
        response = client.post("/v1/conversation/cache/cleanup")
        
        assert response.status_code == 200
        assert "Cache cleanup scheduled" in response.json()["message"]
    
    def test_get_suggestions(self, client, mock_services):
        """測試獲取建議"""
        mock_state = {
            "session_id": "test_session",
            "collected_info": {"destination": "台北"}
        }
        
        mock_services['conversation_engine'].get_conversation_state.return_value = mock_state
        
        response = client.get("/v1/conversation/suggestions/test_session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session"
        assert "suggestions" in data
    
    def test_get_session_stats(self, client, mock_services):
        """測試獲取會話統計"""
        mock_state = {
            "session_id": "test_session",
            "collected_info": {"destination": "台北", "duration": 3},
            "conversation_history": [
                {"role": "user", "content": "test", "timestamp": "2024-01-01T10:00:00"},
                {"role": "assistant", "content": "test", "timestamp": "2024-01-01T10:01:00"}
            ],
            "confidence_score": 0.8,
            "last_activity": "2024-01-01T10:01:00"
        }
        
        mock_services['conversation_engine'].get_conversation_state.return_value = mock_state
        
        response = client.get("/v1/conversation/stats/test_session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test_session"
        assert "turn_count" in data
        assert "completion_rate" in data
    
    def test_batch_chat(self, client, mock_services):
        """測試批量聊天"""
        mock_response = {
            "session_id": "test_session",
            "message": "好的",
            "intent": "provide_info",
            "suggestions": [],
            "collected_info": {},
            "is_complete": False,
            "confidence_score": 0.8,
            "turn_count": 1,
            "timestamp": "2024-01-01T10:00:00"
        }
        
        mock_services['conversation_engine'].process_message.return_value = mock_response
        
        requests = [
            {"session_id": "session1", "message": "我想去台北"},
            {"session_id": "session2", "message": "我想去高雄"}
        ]
        
        response = client.post("/v1/conversation/batch/chat", json=requests)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_processed"] == 2
        assert len(data["results"]) == 2
    
    def test_batch_reset(self, client, mock_services):
        """測試批量重置"""
        mock_services['conversation_engine'].reset_conversation.return_value = True
        
        session_ids = ["session1", "session2", "session3"]
        
        response = client.post("/v1/conversation/batch/reset", json=session_ids)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_requested"] == 3
        assert data["successful_resets"] == 3
        assert data["failed_resets"] == 0
    
    def test_invalid_json_request(self, client):
        """測試無效JSON請求"""
        response = client.post("/v1/conversation/chat", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """測試缺少必填字段"""
        response = client.post("/v1/conversation/chat", json={
            "session_id": "test_session"
            # 缺少 message 字段
        })
        
        assert response.status_code == 422
    
    def test_message_too_long(self, client):
        """測試訊息過長"""
        long_message = "a" * 1001  # 超過1000字符限制
        
        response = client.post("/v1/conversation/chat", json={
            "session_id": "test_session",
            "message": long_message
        })
        
        assert response.status_code == 422


class TestConversationFlow:
    """對話流程測試"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_services(self):
        with patch('src.itinerary_planner.api.v1.endpoints.unified_conversation.get_conversation_engine') as mock_engine, \
             patch('src.itinerary_planner.api.v1.endpoints.unified_conversation.get_performance_optimizer') as mock_optimizer:
            
            mock_engine_instance = AsyncMock()
            mock_optimizer_instance = Mock()
            mock_optimizer_instance.measure_performance = lambda x: lambda f: f
            mock_optimizer_instance.get_cached_result = Mock(return_value=None)
            mock_optimizer_instance.cache_result = Mock()
            mock_optimizer_instance.optimize_memory_usage = Mock()
            
            mock_engine.return_value = mock_engine_instance
            mock_optimizer.return_value = mock_optimizer_instance
            
            yield {
                'conversation_engine': mock_engine_instance,
                'performance_optimizer': mock_optimizer_instance
            }
    
    def test_complete_conversation_flow(self, client, mock_services):
        """測試完整對話流程"""
        session_id = "test_session"
        
        # 1. 打招呼
        greeting_response = {
            "session_id": session_id,
            "message": "您好！我是您的旅遊助手，請告訴我您想去哪裡旅遊？",
            "intent": "greeting",
            "suggestions": ["告訴我您想去哪裡旅遊"],
            "collected_info": {},
            "is_complete": False,
            "confidence_score": 0.9,
            "turn_count": 1,
            "timestamp": "2024-01-01T10:00:00"
        }
        
        # 2. 提供目的地
        destination_response = {
            "session_id": session_id,
            "message": "好的，台北是個很棒的目的地！請告訴我您計劃旅遊幾天？",
            "intent": "provide_info",
            "suggestions": ["告訴我您計劃旅遊幾天"],
            "collected_info": {"destination": "台北"},
            "is_complete": False,
            "confidence_score": 0.8,
            "turn_count": 2,
            "timestamp": "2024-01-01T10:01:00"
        }
        
        # 3. 提供完整信息
        complete_response = {
            "session_id": session_id,
            "message": "太棒了！我已經為您規劃好了行程。",
            "intent": "itinerary_generated",
            "suggestions": ["查看行程詳情", "調整行程"],
            "collected_info": {"destination": "台北", "duration": 3, "interests": ["美食"]},
            "is_complete": True,
            "itinerary": {"days": [{"day": 1, "visits": []}]},
            "confidence_score": 0.95,
            "turn_count": 3,
            "timestamp": "2024-01-01T10:02:00"
        }
        
        # 設置模擬回應序列
        mock_services['conversation_engine'].process_message.side_effect = [
            greeting_response,
            destination_response,
            complete_response
        ]
        
        # 執行對話流程
        responses = []
        
        # 第一輪：打招呼
        response = client.post("/v1/conversation/chat", json={
            "session_id": session_id,
            "message": "你好"
        })
        assert response.status_code == 200
        responses.append(response.json())
        
        # 第二輪：提供目的地
        response = client.post("/v1/conversation/chat", json={
            "session_id": session_id,
            "message": "我想去台北"
        })
        assert response.status_code == 200
        responses.append(response.json())
        
        # 第三輪：提供完整信息
        response = client.post("/v1/conversation/chat", json={
            "session_id": session_id,
            "message": "我想旅遊3天，喜歡美食"
        })
        assert response.status_code == 200
        responses.append(response.json())
        
        # 驗證對話流程
        assert responses[0]["intent"] == "greeting"
        assert responses[1]["intent"] == "provide_info"
        assert responses[1]["collected_info"]["destination"] == "台北"
        assert responses[2]["intent"] == "itinerary_generated"
        assert responses[2]["is_complete"] == True
        assert "itinerary" in responses[2]
        
        # 驗證服務被調用了3次
        assert mock_services['conversation_engine'].process_message.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])

