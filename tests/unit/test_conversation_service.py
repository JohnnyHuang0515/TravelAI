"""
對話服務單元測試
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from src.itinerary_planner.application.services.conversation_service import ConversationService
from src.itinerary_planner.domain.entities.conversation_state import ConversationState, ConversationStateType


class TestConversationService:
    """對話服務測試類別"""
    
    @pytest.fixture
    def conversation_service(self, mock_db_session):
        """建立對話服務實例"""
        with patch('src.itinerary_planner.application.services.conversation_service.GeminiLLMClient'), \
             patch('src.itinerary_planner.application.services.conversation_service.redis.Redis'):
            return ConversationService(mock_db_session)
    
    @pytest.fixture
    def sample_conversation_state(self):
        """測試用的對話狀態"""
        state = ConversationState(str(uuid4()), ConversationStateType.COLLECTING_INFO)
        state.collected_info = {
            "destination": "台北",
            "duration": "3天",
            "interests": "美食,景點",
            "budget": "中等",
            "travel_style": "輕鬆",
            "group_size": "2人"
        }
        return state
    
    @pytest.fixture
    def sample_conversation_history(self):
        """測試用的對話歷史"""
        return [
            {"role": "user", "content": "我想去台北旅遊"},
            {"role": "assistant", "content": "好的！請告訴我您想旅遊幾天？"},
            {"role": "user", "content": "3天2夜"}
        ]
    
    @pytest.mark.asyncio
    async def test_process_message_new_session(self, conversation_service):
        """測試處理新會話的訊息"""
        session_id = str(uuid4())
        user_message = "我想去台北旅遊"
        
        # Mock 方法
        conversation_service.get_conversation_state = AsyncMock(return_value=None)
        conversation_service._analyze_user_message = AsyncMock()
        conversation_service._is_info_complete = Mock(return_value=False)
        conversation_service._ask_next_question = AsyncMock(return_value={
            "message": "好的！請告訴我您想旅遊幾天？",
            "conversation_state": "collecting_info",
            "is_complete": False
        })
        
        # 執行測試
        result = await conversation_service.process_message(session_id, user_message)
        
        # 驗證結果
        assert "message" in result
        assert "conversation_state" in result
        assert result["message"] == "好的！請告訴我您想旅遊幾天？"
        
        # 驗證方法呼叫
        conversation_service.get_conversation_state.assert_called_once_with(session_id)
        conversation_service._analyze_user_message.assert_called_once()
        conversation_service._is_info_complete.assert_called_once()
        conversation_service._ask_next_question.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_message_existing_session(self, conversation_service, sample_conversation_state):
        """測試處理現有會話的訊息"""
        session_id = str(uuid4())
        user_message = "我想去美食餐廳"
        
        # Mock 方法
        conversation_service.get_conversation_state = AsyncMock(return_value=sample_conversation_state)
        conversation_service._analyze_user_message = AsyncMock()
        conversation_service._is_info_complete = Mock(return_value=False)
        conversation_service._ask_next_question = AsyncMock(return_value={
            "message": "好的，我會為您推薦美食餐廳",
            "conversation_state": "collecting_info",
            "is_complete": False
        })
        
        # 執行測試
        result = await conversation_service.process_message(session_id, user_message)
        
        # 驗證結果
        assert "message" in result
        assert "conversation_state" in result
        assert result["message"] == "好的，我會為您推薦美食餐廳"
        
        # 驗證狀態被更新
        assert len(sample_conversation_state.conversation_history) > 0
    
    @pytest.mark.asyncio
    async def test_process_message_info_complete(self, conversation_service, sample_conversation_state):
        """測試資訊收集完成的情況"""
        session_id = str(uuid4())
        user_message = "好的，開始規劃吧"
        
        # Mock 方法
        conversation_service.get_conversation_state = AsyncMock(return_value=sample_conversation_state)
        conversation_service._analyze_user_message = AsyncMock()
        conversation_service._is_info_complete = Mock(return_value=True)
        conversation_service._generate_itinerary = AsyncMock(return_value={"days": []})
        
        # 執行測試
        result = await conversation_service.process_message(session_id, user_message)
        
        # 驗證結果
        assert "days" in result
        
        # 驗證方法呼叫
        conversation_service._generate_itinerary.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_conversation_state_existing(self, conversation_service, sample_conversation_state):
        """測試獲取現有的對話狀態"""
        session_id = str(uuid4())
        
        # Mock Redis
        mock_redis = Mock()
        mock_redis.get.return_value = '{"session_id": "' + session_id + '", "state_type": "COLLECTING_INFO"}'
        conversation_service.redis_client = mock_redis
        
        # Mock ConversationState.from_dict
        with patch.object(ConversationState, 'from_dict', return_value=sample_conversation_state):
            result = await conversation_service.get_conversation_state(session_id)
        
        # 驗證結果
        assert result == sample_conversation_state
        mock_redis.get.assert_called_once_with(f"conversation:{session_id}")
    
    @pytest.mark.asyncio
    async def test_get_conversation_state_not_found(self, conversation_service):
        """測試獲取不存在的對話狀態"""
        session_id = str(uuid4())
        
        # Mock Redis
        mock_redis = Mock()
        mock_redis.get.return_value = None
        conversation_service.redis_client = mock_redis
        
        # 執行測試
        result = await conversation_service.get_conversation_state(session_id)
        
        # 驗證結果
        assert result is None
        mock_redis.get.assert_called_once_with(f"conversation:{session_id}")
    
    def test_save_conversation_state(self, conversation_service, sample_conversation_state):
        """測試儲存對話狀態"""
        # Mock Redis
        mock_redis = Mock()
        conversation_service.redis_client = mock_redis
        
        # Mock ConversationState.to_dict
        with patch.object(sample_conversation_state, 'to_dict', return_value={"test": "data"}):
            conversation_service._save_conversation_state(sample_conversation_state)
        
        # 驗證 Redis 呼叫
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == f"conversation:{sample_conversation_state.session_id}"
        assert call_args[0][1] == 3600  # 1 小時過期
        assert call_args[0][2] == '{"test": "data"}'
    
    def test_is_info_complete_true(self, conversation_service, sample_conversation_state):
        """測試資訊收集完成"""
        # 執行測試
        result = conversation_service._is_info_complete(sample_conversation_state)
        
        # 驗證結果
        assert result is True
    
    def test_is_info_complete_false(self, conversation_service):
        """測試資訊收集未完成"""
        # 建立不完整的狀態
        incomplete_state = ConversationState(str(uuid4()), ConversationStateType.COLLECTING_INFO)
        incomplete_state.collected_info = {
            "destination": "台北"
            # 缺少 duration 必要資訊
        }
        
        # 執行測試
        result = conversation_service._is_info_complete(incomplete_state)
        
        # 驗證結果
        assert result is False
    
    def test_is_info_complete_empty(self, conversation_service):
        """測試空資訊收集狀態"""
        # 建立空狀態
        empty_state = ConversationState(str(uuid4()), ConversationStateType.COLLECTING_INFO)
        empty_state.collected_info = {}
        
        # 執行測試
        result = conversation_service._is_info_complete(empty_state)
        
        # 驗證結果
        assert result is False
    
    @pytest.mark.asyncio
    async def test_analyze_user_message(self, conversation_service, sample_conversation_state):
        """測試分析用戶訊息"""
        user_message = "我想去台北旅遊3天，預算中等"
        
        # Mock LLM 客戶端
        mock_llm = Mock()
        mock_llm.generate_text.return_value = '{"destination": "台北", "duration": "3天", "budget": "中等"}'
        conversation_service.llm_client = mock_llm
        
        # 執行測試
        await conversation_service._analyze_user_message(sample_conversation_state, user_message)
        
        # 驗證 LLM 呼叫
        mock_llm.generate_text.assert_called_once()
        
        # 驗證狀態更新
        assert sample_conversation_state.collected_info["destination"] == "台北"
        assert sample_conversation_state.collected_info["duration"] == "3天"
        assert sample_conversation_state.collected_info["budget"] == "中等"
    
    @pytest.mark.asyncio
    async def test_ask_next_question(self, conversation_service, sample_conversation_state):
        """測試生成下一個問題"""
        # Mock LLM 客戶端
        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = "請告訴我您想旅遊幾天？"
        conversation_service.llm_client = mock_llm
        
        # Mock Redis
        mock_redis = Mock()
        conversation_service.redis_client = mock_redis
        
        # 執行測試
        result = await conversation_service._ask_next_question(sample_conversation_state)
        
        # 驗證結果
        assert "message" in result
        assert "conversation_state" in result
        assert "is_complete" in result
        assert result["message"] == "請告訴我您想旅遊幾天？"
        assert result["is_complete"] is False
    
    def test_required_info_structure(self, conversation_service):
        """測試必要資訊結構"""
        # 驗證必要資訊的結構
        required_info = conversation_service.required_info
        
        assert "destination" in required_info
        assert "duration" in required_info
        assert "interests" in required_info
        assert "budget" in required_info
        assert "travel_style" in required_info
        assert "group_size" in required_info
        
        # 驗證所有值都是字串
        for key, value in required_info.items():
            assert isinstance(value, str)
            assert len(value) > 0
    
    @pytest.mark.asyncio
    async def test_process_message_with_history(self, conversation_service):
        """測試帶歷史記錄的訊息處理"""
        session_id = str(uuid4())
        user_message = "我想去美食餐廳"
        conversation_history = [
            {"role": "user", "content": "我想去台北旅遊"},
            {"role": "assistant", "content": "好的！請告訴我您想旅遊幾天？"}
        ]
        
        # Mock 方法
        conversation_service.get_conversation_state = AsyncMock(return_value=None)
        conversation_service._analyze_user_message = AsyncMock()
        conversation_service._is_info_complete = Mock(return_value=False)
        conversation_service._ask_next_question = AsyncMock(return_value={
            "message": "好的，我會為您推薦美食餐廳",
            "conversation_state": "collecting_info",
            "is_complete": False
        })
        
        # 執行測試
        result = await conversation_service.process_message(
            session_id, 
            user_message, 
            conversation_history
        )
        
        # 驗證結果
        assert "message" in result
        assert "conversation_state" in result
        assert result["message"] == "好的，我會為您推薦美食餐廳"
    
    @pytest.mark.asyncio
    async def test_process_message_error_handling(self, conversation_service):
        """測試錯誤處理"""
        session_id = str(uuid4())
        user_message = "測試訊息"
        
        # Mock 方法拋出異常
        conversation_service.get_conversation_state = AsyncMock(side_effect=Exception("Redis 連線錯誤"))
        
        # 執行測試
        with pytest.raises(Exception, match="Redis 連線錯誤"):
            await conversation_service.process_message(session_id, user_message)
