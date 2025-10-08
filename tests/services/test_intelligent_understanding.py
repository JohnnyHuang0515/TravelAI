import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.itinerary_planner.application.services.intelligent_understanding import (
    IntelligentUnderstandingService,
    EntityType,
    ExtractedEntity,
    ConversationContext
)


class TestIntelligentUnderstandingService:
    """智能理解服務測試"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """模擬LLM客戶端"""
        mock_client = Mock()
        mock_client.generate_response = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def understanding_service(self, mock_llm_client):
        """創建測試用的智能理解服務實例"""
        with patch('src.itinerary_planner.application.services.intelligent_understanding.GeminiLLMClient', return_value=mock_llm_client):
            service = IntelligentUnderstandingService()
            return service
    
    @pytest.fixture
    def sample_context(self):
        """創建示例對話上下文"""
        context = ConversationContext(
            session_id="test_session",
            user_profile={},
            conversation_memory={},
            recent_intents=[],
            extracted_entities=[],
            conversation_history=[],
            last_activity=datetime.now()
        )
        return context
    
    @pytest.mark.asyncio
    async def test_analyze_message_complete_flow(self, understanding_service, sample_context, mock_llm_client):
        """測試完整的訊息分析流程"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "provide_info",  # 意圖識別
            json.dumps({
                "entities": [
                    {"type": "destination", "value": "台北", "confidence": 0.9, "start_pos": 2, "end_pos": 4},
                    {"type": "duration", "value": "3", "confidence": 0.8, "start_pos": 8, "end_pos": 9}
                ]
            }),  # 實體提取
            json.dumps({
                "sentiment": "positive",
                "intensity": "moderate",
                "emotions": ["開心", "期待"],
                "confidence": 0.8
            }),  # 情感分析
        ]
        
        result = await understanding_service.analyze_message("我想去台北旅遊3天", sample_context)
        
        assert result["intent"]["type"] == "provide_info"
        assert len(result["entities"]) > 0
        assert result["sentiment"]["sentiment"] == "positive"
        assert result["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_recognize_intent_quick(self, understanding_service):
        """測試快速意圖識別"""
        # 測試關鍵詞匹配
        result = understanding_service._quick_intent_recognition("你好，我想去旅遊")
        assert result["type"] == "greeting"
        assert result["confidence"] == 0.7
        
        result = understanding_service._quick_intent_recognition("我想去台北")
        assert result["type"] == "provide_info"
        
        result = understanding_service._quick_intent_recognition("台北有什麼景點？")
        assert result["type"] == "ask_question"
    
    @pytest.mark.asyncio
    async def test_recognize_intent_llm(self, understanding_service, sample_context, mock_llm_client):
        """測試LLM意圖識別"""
        mock_llm_client.generate_response.return_value = json.dumps({
            "type": "provide_info",
            "confidence": 0.85,
            "evidence": "用戶表達了旅遊意願",
            "sub_intent": "提供目的地信息"
        })
        
        result = await understanding_service._llm_intent_analysis("我想規劃一個台北的旅遊行程", sample_context)
        
        assert result["type"] == "provide_info"
        assert result["confidence"] == 0.85
        assert "evidence" in result
    
    def test_extract_entities_by_regex(self, understanding_service):
        """測試基於正則表達式的實體提取"""
        message = "我想去台北旅遊3天，喜歡美食，預算中等"
        
        entities = understanding_service._extract_entities_by_regex(message)
        
        # 檢查是否提取到實體
        entity_types = [entity.type for entity in entities]
        assert EntityType.DESTINATION in entity_types or EntityType.INTEREST in entity_types
    
    @pytest.mark.asyncio
    async def test_extract_entities_by_llm(self, understanding_service, sample_context, mock_llm_client):
        """測試LLM實體提取"""
        mock_llm_client.generate_response.return_value = json.dumps({
            "entities": [
                {"type": "destination", "value": "台北", "confidence": 0.9, "start_pos": 2, "end_pos": 4},
                {"type": "duration", "value": "3", "confidence": 0.8, "start_pos": 8, "end_pos": 9},
                {"type": "interest", "value": "美食", "confidence": 0.7, "start_pos": 12, "end_pos": 14}
            ]
        })
        
        entities = await understanding_service._extract_entities_by_llm("我想去台北旅遊3天，喜歡美食", sample_context)
        
        assert len(entities) == 3
        assert any(entity.type == EntityType.DESTINATION for entity in entities)
        assert any(entity.type == EntityType.DURATION for entity in entities)
        assert any(entity.type == EntityType.INTEREST for entity in entities)
    
    def test_merge_entities(self, understanding_service):
        """測試實體合併"""
        entities = [
            ExtractedEntity(EntityType.DESTINATION, "台北", 0.8, "台北", 0, 2),
            ExtractedEntity(EntityType.DESTINATION, "台北市", 0.9, "台北市", 0, 3),
            ExtractedEntity(EntityType.DURATION, "3", 0.7, "3天", 5, 8)
        ]
        
        merged = understanding_service._merge_entities(entities)
        
        # 應該合併重複的實體，選擇置信度最高的
        assert len(merged) == 2  # 目的地和天數
        destination_entity = next(e for e in merged if e.type == EntityType.DESTINATION)
        assert destination_entity.value == "台北市"  # 置信度更高的
        assert destination_entity.confidence == 0.9
    
    def test_lexicon_sentiment_analysis(self, understanding_service):
        """測試基於詞典的情感分析"""
        # 正面情感
        positive_result = understanding_service._lexicon_sentiment_analysis("我喜歡這個景點，很開心")
        assert positive_result["sentiment"] == "positive"
        assert positive_result["confidence"] > 0.5
        
        # 負面情感
        negative_result = understanding_service._lexicon_sentiment_analysis("我不喜歡這個地方，很失望")
        assert negative_result["sentiment"] == "negative"
        
        # 中性情感
        neutral_result = understanding_service._lexicon_sentiment_analysis("這個地方還可以")
        assert neutral_result["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_llm_sentiment_analysis(self, understanding_service, sample_context, mock_llm_client):
        """測試LLM情感分析"""
        mock_llm_client.generate_response.return_value = json.dumps({
            "sentiment": "positive",
            "intensity": "strong",
            "emotions": ["興奮", "期待"],
            "confidence": 0.9
        })
        
        result = await understanding_service._llm_sentiment_analysis("太棒了！我迫不及待想去台北旅遊！", sample_context)
        
        assert result["sentiment"] == "positive"
        assert result["intensity"] == "strong"
        assert "興奮" in result["emotions"]
        assert result["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_identify_topic(self, understanding_service, sample_context):
        """測試主題識別"""
        result = await understanding_service._identify_topic("我想規劃一個3天的台北旅遊行程", sample_context)
        
        assert result["primary"] in ["planning", "destination", "activities"]
        assert result["confidence"] > 0
    
    def test_identify_conversation_stage(self, understanding_service):
        """測試對話階段識別"""
        # 空上下文
        context = ConversationContext("test", {}, {}, [], [], [], datetime.now())
        stage = understanding_service._identify_conversation_stage(context)
        assert stage == "initial"
        
        # 有目的地但沒有天數
        context.extracted_entities = [
            ExtractedEntity(EntityType.DESTINATION, "台北", 0.9, "台北", 0, 2)
        ]
        stage = understanding_service._identify_conversation_stage(context)
        assert stage == "collecting_duration"
        
        # 信息完整
        context.extracted_entities = [
            ExtractedEntity(EntityType.DESTINATION, "台北", 0.9, "台北", 0, 2),
            ExtractedEntity(EntityType.DURATION, "3", 0.8, "3天", 5, 8),
            ExtractedEntity(EntityType.INTEREST, "美食", 0.7, "美食", 10, 12),
            ExtractedEntity(EntityType.BUDGET, "medium", 0.6, "中等", 15, 17)
        ]
        stage = understanding_service._identify_conversation_stage(context)
        assert stage == "ready_for_planning"
    
    def test_analyze_needs_change(self, understanding_service):
        """測試需求變化分析"""
        # 有變化指示詞
        result = understanding_service._analyze_needs_change("我不要去台北，改成高雄", sample_context)
        assert result["has_change"] == True
        assert "高雄" in result["changed_items"][0]
        
        # 沒有變化指示詞
        result = understanding_service._analyze_needs_change("我想去台北旅遊", sample_context)
        assert result["has_change"] == False
    
    def test_analyze_coherence(self, understanding_service):
        """測試對話連貫性分析"""
        context = ConversationContext("test", {}, {}, [], [], [
            {"role": "user", "content": "我想去台北旅遊", "timestamp": "2024-01-01T10:00:00"},
            {"role": "assistant", "content": "好的，請告訴我您想旅遊幾天？", "timestamp": "2024-01-01T10:01:00"}
        ], datetime.now())
        
        result = understanding_service._analyze_coherence("我想去3天", context)
        
        assert result["is_coherent"] == True
        assert result["coherence_score"] > 0.3
    
    def test_calculate_context_quality(self, understanding_service):
        """測試上下文質量計算"""
        # 高質量上下文
        high_quality_context = ConversationContext("test", {}, {}, [], [
            ExtractedEntity(EntityType.DESTINATION, "台北", 0.9, "台北", 0, 2),
            ExtractedEntity(EntityType.DURATION, "3", 0.8, "3天", 5, 8),
            ExtractedEntity(EntityType.INTEREST, "美食", 0.7, "美食", 10, 12)
        ], [
            {"role": "user", "content": "我想去台北旅遊3天", "timestamp": "2024-01-01T10:00:00"},
            {"role": "assistant", "content": "好的", "timestamp": "2024-01-01T10:01:00"}
        ], datetime.now())
        
        quality = understanding_service._calculate_context_quality(high_quality_context)
        assert quality > 0.7
        
        # 低質量上下文
        low_quality_context = ConversationContext("test", {}, {}, [], [], [], datetime.now())
        quality = understanding_service._calculate_context_quality(low_quality_context)
        assert quality < 0.5
    
    def test_calculate_confidence(self, understanding_service):
        """測試置信度計算"""
        intent = {"confidence": 0.8}
        entities = [
            ExtractedEntity(EntityType.DESTINATION, "台北", 0.9, "台北", 0, 2),
            ExtractedEntity(EntityType.DURATION, "3", 0.7, "3天", 5, 8)
        ]
        sentiment = {"confidence": 0.85}
        
        confidence = understanding_service._calculate_confidence(intent, entities, sentiment)
        
        assert 0.1 <= confidence <= 0.95
        assert confidence > 0.7  # 應該相對較高
    
    def test_build_context_summary(self, understanding_service):
        """測試構建上下文摘要"""
        context = ConversationContext("test", {}, {}, [], [], [
            {"role": "user", "content": "我想去台北旅遊", "timestamp": "2024-01-01T10:00:00"},
            {"role": "assistant", "content": "好的，請告訴我您想旅遊幾天？", "timestamp": "2024-01-01T10:01:00"},
            {"role": "user", "content": "我想去3天", "timestamp": "2024-01-01T10:02:00"}
        ], datetime.now())
        
        summary = understanding_service._build_context_summary(context)
        
        assert "用戶" in summary
        assert "我想去台北旅遊" in summary
        assert "我想去3天" in summary


class TestExtractedEntity:
    """提取實體測試"""
    
    def test_entity_creation(self):
        """測試實體創建"""
        entity = ExtractedEntity(
            type=EntityType.DESTINATION,
            value="台北",
            confidence=0.9,
            context="台北",
            start_pos=0,
            end_pos=2
        )
        
        assert entity.type == EntityType.DESTINATION
        assert entity.value == "台北"
        assert entity.confidence == 0.9
        assert entity.context == "台北"
        assert entity.start_pos == 0
        assert entity.end_pos == 2


class TestConversationContext:
    """對話上下文測試"""
    
    def test_context_creation(self):
        """測試上下文創建"""
        context = ConversationContext(
            session_id="test_session",
            user_profile={"preferences": "美食"},
            conversation_memory={"last_topic": "旅遊"},
            recent_intents=["greeting"],
            extracted_entities=[],
            conversation_history=[],
            last_activity=datetime.now()
        )
        
        assert context.session_id == "test_session"
        assert context.user_profile["preferences"] == "美食"
        assert context.conversation_memory["last_topic"] == "旅遊"
        assert context.recent_intents == ["greeting"]


if __name__ == "__main__":
    pytest.main([__file__])

