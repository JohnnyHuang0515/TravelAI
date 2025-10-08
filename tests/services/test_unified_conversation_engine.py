import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from src.itinerary_planner.application.services.unified_conversation_engine import (
    UnifiedConversationEngine,
    ConversationIntent,
    ConversationContext
)
from src.itinerary_planner.domain.entities.conversation_state import ConversationStateType


class TestUnifiedConversationEngine:
    """統一對話引擎測試"""
    
    @pytest.fixture
    def mock_db_session(self):
        """模擬數據庫會話"""
        return Mock()
    
    @pytest.fixture
    def mock_redis_client(self):
        """模擬Redis客戶端"""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        return mock_redis
    
    @pytest.fixture
    def mock_llm_client(self):
        """模擬LLM客戶端"""
        mock_client = Mock()
        mock_client.generate_response = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def engine(self, mock_db_session, mock_redis_client, mock_llm_client):
        """創建測試用的對話引擎實例"""
        with patch('src.itinerary_planner.application.services.unified_conversation_engine.GeminiLLMClient', return_value=mock_llm_client):
            with patch('src.itinerary_planner.application.services.unified_conversation_engine.redis.Redis', return_value=mock_redis_client):
                engine = UnifiedConversationEngine(mock_db_session)
                return engine
    
    @pytest.mark.asyncio
    async def test_process_message_greeting(self, engine, mock_llm_client):
        """測試處理打招呼訊息"""
        # 設置LLM回應
        mock_llm_client.generate_response.return_value = "greeting"
        
        # 測試打招呼
        result = await engine.process_message(
            session_id="test_session",
            user_message="你好"
        )
        
        assert result["intent"] == ConversationIntent.GREETING.value
        assert "您好" in result["message"]
        assert result["is_complete"] == False
        assert "suggestions" in result
    
    @pytest.mark.asyncio
    async def test_process_message_provide_info(self, engine, mock_llm_client):
        """測試處理提供信息訊息"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "provide_info",  # 意圖識別
            json.dumps({"destination": "台北", "duration": 3, "interests": ["美食"]})  # 實體提取
        ]
        
        result = await engine.process_message(
            session_id="test_session",
            user_message="我想去台北旅遊3天，喜歡美食"
        )
        
        assert result["intent"] == ConversationIntent.PROVIDE_INFO.value
        assert "台北" in str(result["collected_info"])
        assert result["is_complete"] == False  # 還需要更多信息
    
    @pytest.mark.asyncio
    async def test_process_message_complete_info(self, engine, mock_llm_client):
        """測試處理完整信息"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "provide_info",  # 意圖識別
            json.dumps({
                "destination": "台北", 
                "duration": 3, 
                "interests": ["美食", "文化"],
                "budget": "medium",
                "travel_style": "moderate",
                "group_size": 2
            })  # 實體提取
        ]
        
        # 模擬行程規劃API
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"itinerary": "test_itinerary"}
            mock_post.return_value = mock_response
            
            result = await engine.process_message(
                session_id="test_session",
                user_message="我想去台北旅遊3天，喜歡美食和文化，預算中等，2個人"
            )
            
            assert result["intent"] == "itinerary_generated"
            assert result["is_complete"] == True
            assert "itinerary" in result
    
    @pytest.mark.asyncio
    async def test_analyze_intent(self, engine, mock_llm_client):
        """測試意圖分析"""
        mock_llm_client.generate_response.return_value = "provide_info"
        
        context = ConversationContext("test_session")
        context.conversation_history = [
            {"role": "user", "content": "我想去旅遊", "timestamp": "2024-01-01T10:00:00"}
        ]
        
        intent = await engine._analyze_intent("我想去台北旅遊", context)
        
        assert intent == ConversationIntent.PROVIDE_INFO
        mock_llm_client.generate_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_entities(self, engine, mock_llm_client):
        """測試實體提取"""
        mock_llm_client.generate_response.return_value = json.dumps({
            "destination": "台北",
            "duration": 3,
            "interests": ["美食"]
        })
        
        context = ConversationContext("test_session")
        entities = await engine._extract_entities("我想去台北旅遊3天，喜歡美食", context)
        
        assert "destination" in entities
        assert "duration" in entities
        assert "interests" in entities
        assert entities["destination"] == "台北"
        assert entities["duration"] == 3
    
    @pytest.mark.asyncio
    async def test_generate_next_question(self, engine, mock_llm_client):
        """測試生成下一個問題"""
        mock_llm_client.generate_response.return_value = "請告訴我您的旅遊預算範圍？"
        
        context = ConversationContext("test_session")
        context.extracted_entities = {
            "destination": "台北",
            "duration": 3
        }
        
        question = await engine._generate_next_question(context)
        
        assert "預算" in question or "費用" in question
        mock_llm_client.generate_response.assert_called_once()
    
    def test_is_info_complete(self, engine):
        """測試信息完整性檢查"""
        # 不完整信息
        incomplete_info = {"destination": "台北"}
        assert engine._is_info_complete(incomplete_info) == False
        
        # 完整信息
        complete_info = {
            "destination": "台北",
            "duration": 3,
            "interests": ["美食"]
        }
        assert engine._is_info_complete(complete_info) == True
    
    def test_build_planning_request(self, engine):
        """測試構建規劃請求"""
        entities = {
            "destination": "台北",
            "duration": 3,
            "interests": ["美食", "文化"]
        }
        
        request_text = engine._build_planning_request(entities)
        
        assert "台北" in request_text
        assert "3天" in request_text
        assert "美食" in request_text
        assert "文化" in request_text
    
    @pytest.mark.asyncio
    async def test_generate_suggestions(self, engine):
        """測試生成建議"""
        context = ConversationContext("test_session")
        
        # 沒有目的地
        context.extracted_entities = {}
        suggestions = engine._generate_suggestions(context)
        assert any("去哪裡" in s for s in suggestions)
        
        # 有目的地但沒有天數
        context.extracted_entities = {"destination": "台北"}
        suggestions = engine._generate_suggestions(context)
        assert any("幾天" in s for s in suggestions)
        
        # 信息完整
        context.extracted_entities = {
            "destination": "台北",
            "duration": 3,
            "interests": ["美食"]
        }
        suggestions = engine._generate_suggestions(context)
        assert any("調整" in s for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_get_conversation_state(self, engine, mock_redis_client):
        """測試獲取對話狀態"""
        # 模擬Redis返回空（新會話）
        mock_redis_client.get.return_value = None
        
        state = await engine.get_conversation_state("new_session")
        
        assert state is not None
        assert state["session_id"] == "new_session"
    
    @pytest.mark.asyncio
    async def test_reset_conversation(self, engine, mock_redis_client):
        """測試重置對話"""
        mock_redis_client.delete.return_value = 1
        
        result = await engine.reset_conversation("test_session")
        
        assert result == True
        mock_redis_client.delete.assert_called_once_with("conversation_context:test_session")
    
    @pytest.mark.asyncio
    async def test_handle_modify_request(self, engine, mock_llm_client):
        """測試處理修改請求"""
        mock_llm_client.generate_response.side_effect = [
            "modify_request",  # 意圖識別
            json.dumps({"destination": "高雄"})  # 修改內容
        ]
        
        context = ConversationContext("test_session")
        context.extracted_entities = {"destination": "台北", "duration": 3}
        
        result = await engine._handle_modify_request("我想改成去高雄", context)
        
        assert result["intent"] == ConversationIntent.MODIFY_REQUEST.value
        assert "高雄" in str(result["collected_info"])
    
    @pytest.mark.asyncio
    async def test_handle_ask_question(self, engine, mock_llm_client):
        """測試處理詢問"""
        mock_llm_client.generate_response.side_effect = [
            "ask_question",  # 意圖識別
            "台北有很多美食景點，推薦您可以去士林夜市、永康街等地品嘗台灣小吃。"  # 回答
        ]
        
        context = ConversationContext("test_session")
        result = await engine._handle_ask_question("台北有什麼美食推薦？", context)
        
        assert result["intent"] == ConversationIntent.ASK_QUESTION.value
        assert "美食" in result["message"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, engine, mock_llm_client):
        """測試錯誤處理"""
        # 模擬LLM拋出異常
        mock_llm_client.generate_response.side_effect = Exception("LLM service error")
        
        result = await engine.process_message(
            session_id="test_session",
            user_message="測試錯誤處理"
        )
        
        assert "error" in result
        assert result["message"] == "抱歉，處理您的請求時遇到了一些問題。請稍後再試。"


class TestConversationContext:
    """對話上下文測試"""
    
    def test_add_message(self):
        """測試添加訊息"""
        context = ConversationContext("test_session")
        context.add_message("user", "你好")
        
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0]["role"] == "user"
        assert context.conversation_history[0]["content"] == "你好"
    
    def test_get_recent_context(self):
        """測試獲取最近上下文"""
        context = ConversationContext("test_session")
        context.add_message("user", "第一條訊息")
        context.add_message("assistant", "第一條回應")
        context.add_message("user", "第二條訊息")
        context.add_message("assistant", "第二條回應")
        context.add_message("user", "第三條訊息")
        
        recent = context.get_recent_context(limit=3)
        
        assert "第二條訊息" in recent
        assert "第三條訊息" in recent
        assert "第一條訊息" not in recent
    
    def test_update_entities(self):
        """測試更新實體"""
        context = ConversationContext("test_session")
        context.update_entities({"destination": "台北"})
        context.update_entities({"duration": 3})
        
        assert context.extracted_entities["destination"] == "台北"
        assert context.extracted_entities["duration"] == 3
    
    def test_update_preferences(self):
        """測試更新偏好"""
        context = ConversationContext("test_session")
        context.update_preferences({"budget": "medium"})
        context.update_preferences({"travel_style": "relaxed"})
        
        assert context.user_preferences["budget"] == "medium"
        assert context.user_preferences["travel_style"] == "relaxed"


if __name__ == "__main__":
    pytest.main([__file__])

