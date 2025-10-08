import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.itinerary_planner.application.graph_state import AppState
from src.itinerary_planner.domain.entities.conversation_state import ConversationState, ConversationStateType
from src.itinerary_planner.domain.models.story import Story, Preference, AccommodationPreference, TimeWindow
from src.itinerary_planner.infrastructure.persistence.orm_models import Place


class TestGraphNodes:
    """測試 GraphNodes 類別"""

    @pytest.fixture
    def mock_graph_nodes(self):
        """建立模擬的 GraphNodes 實例"""
        with patch('src.itinerary_planner.application.graph_nodes.GeminiLLMClient') as mock_gemini, \
             patch('src.itinerary_planner.application.graph_nodes.redis.Redis') as mock_redis, \
             patch('src.itinerary_planner.application.graph_nodes.embedding_client') as mock_embedding, \
             patch('src.itinerary_planner.application.graph_nodes.llm_client') as mock_llm, \
             patch('src.itinerary_planner.application.graph_nodes.osrm_client') as mock_osrm, \
             patch('src.itinerary_planner.application.graph_nodes.rerank_service') as mock_rerank, \
             patch('src.itinerary_planner.application.graph_nodes.accommodation_recommendation_service') as mock_acc, \
             patch('src.itinerary_planner.application.graph_nodes.greedy_planner') as mock_planner:
            
            mock_gemini_instance = Mock()
            mock_gemini.return_value = mock_gemini_instance
            
            mock_redis_instance = Mock()
            mock_redis.return_value = mock_redis_instance
            
            # 模擬 GraphNodes 類別
            from src.itinerary_planner.application.graph_nodes import GraphNodes
            nodes = GraphNodes()
            nodes.gemini_client = mock_gemini_instance
            nodes.redis_client = mock_redis_instance
            
            return nodes

    @pytest.fixture
    def sample_app_state(self):
        """建立範例 AppState"""
        return {
            "user_input": "我想去台北三天兩夜",
            "session_id": "test_session_123",
            "conversation_state": None,
            "conversation_history": [],
            "collected_info": {},
            "is_info_complete": False,
            "conversation_memory": {},
            "context_summary": "",
            "previous_responses": [],
            "turn_count": 0,
            "story": None,
            "structured_candidates": [],
            "semantic_candidates": [],
            "candidates": [],
            "accommodation_candidates": [],
            "itinerary": None,
            "error": None,
            "ai_response": None,
            "next_question": None,
        }

    @pytest.fixture
    def sample_conversation_state(self):
        """建立範例 ConversationState"""
        return ConversationState(
            session_id="test_session_123",
            state_type=ConversationStateType.COLLECTING_INFO,
            collected_info={"destination": "台北", "duration": "3天"},
            conversation_history=[{"role": "user", "content": "我想去台北三天兩夜"}]
        )

    def test_init(self, mock_graph_nodes):
        """測試初始化"""
        assert mock_graph_nodes.gemini_client is not None
        assert mock_graph_nodes.redis_client is not None
        assert "destination" in mock_graph_nodes.required_info
        assert "duration" in mock_graph_nodes.required_info
        assert "interests" in mock_graph_nodes.required_info

    def test_conversation_memory_manager_new_session(self, mock_graph_nodes, sample_app_state):
        """測試對話記憶管理 - 新會話"""
        # 模擬 Redis 中沒有會話狀態
        mock_graph_nodes.redis_client.get.return_value = None
        
        result = mock_graph_nodes.conversation_memory_manager(sample_app_state)
        
        assert result["conversation_memory"] == {}
        assert result["context_summary"] == ""
        assert result["turn_count"] == 0

    def test_conversation_memory_manager_existing_session(self, mock_graph_nodes, sample_app_state):
        """測試對話記憶管理 - 現有會話"""
        # 模擬 Redis 中有會話狀態
        memory_data = {
            "context_summary": "用戶想去台北旅遊",
            "turn_count": 2,
            "previous_responses": ["好的", "了解"]
        }
        mock_graph_nodes.redis_client.get.return_value = json.dumps(memory_data)
        
        result = mock_graph_nodes.conversation_memory_manager(sample_app_state)
        
        assert result["context_summary"] == "用戶想去台北旅遊"
        assert result["turn_count"] == 2
        assert result["previous_responses"] == ["好的", "了解"]

    def test_info_collector_new_conversation(self, mock_graph_nodes, sample_app_state):
        """測試資訊收集器 - 新對話"""
        # 模擬沒有現有對話狀態
        mock_graph_nodes._get_conversation_state.return_value = None
        
        # 模擬 Gemini 分析結果
        mock_graph_nodes.gemini_client.generate_text.return_value = "請告訴我您想去哪裡旅遊？"
        
        result = mock_graph_nodes.info_collector(sample_app_state)
        
        assert result["ai_response"] == "請告訴我您想去哪裡旅遊？"
        assert result["is_info_complete"] is False

    def test_info_collector_existing_conversation(self, mock_graph_nodes, sample_app_state, sample_conversation_state):
        """測試資訊收集器 - 現有對話"""
        # 模擬有現有對話狀態
        mock_graph_nodes._get_conversation_state.return_value = sample_conversation_state
        
        # 模擬分析結果
        mock_graph_nodes._analyze_user_message_with_memory.return_value = None
        mock_graph_nodes._is_info_complete.return_value = False
        mock_graph_nodes._generate_next_question_with_memory.return_value = "您希望什麼時候出發？"
        
        result = mock_graph_nodes.info_collector(sample_app_state)
        
        assert result["ai_response"] == "您希望什麼時候出發？"
        assert result["is_info_complete"] is False

    def test_extract_story_success(self, mock_graph_nodes, sample_app_state):
        """測試成功提取故事"""
        # 模擬有對話狀態和完整資訊
        conversation_state = ConversationState(
            session_id="test_session_123",
            state_type=ConversationStateType.COLLECTING_INFO,
            collected_info={
                "destination": "台北",
                "duration": "3天",
                "interests": "美食,文化",
                "budget": "中等",
                "travel_style": "輕鬆",
                "group_size": "2人"
            },
            conversation_history=[]
        )
        
        # 模擬 Story 創建
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食", "文化"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        mock_graph_nodes.gemini_client.extract_story_from_text.return_value = mock_story
        
        sample_app_state["conversation_state"] = conversation_state
        
        result = mock_graph_nodes.extract_story(sample_app_state)
        
        assert result["story"] == mock_story
        assert result["error"] is None

    def test_extract_story_error(self, mock_graph_nodes, sample_app_state):
        """測試提取故事時發生錯誤"""
        # 模擬 Story 創建失敗
        mock_graph_nodes.gemini_client.extract_story_from_text.side_effect = Exception("API Error")
        
        result = mock_graph_nodes.extract_story(sample_app_state)
        
        assert result["story"] is None
        assert "API Error" in result["error"]

    def test_retrieve_places_structured_success(self, mock_graph_nodes, sample_app_state):
        """測試成功檢索結構化地點"""
        # 模擬 Story
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        sample_app_state["story"] = mock_story
        
        # 模擬地點檢索結果
        mock_places = [
            Place(id="1", name="台北101", categories=["景點"], rating=4.5),
            Place(id="2", name="西門町", categories=["購物"], rating=4.2)
        ]
        
        with patch('src.itinerary_planner.application.graph_nodes.SessionLocal') as mock_session_local, \
             patch('src.itinerary_planner.application.graph_nodes.PostgresPlaceRepository') as mock_repo:
            
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.search.return_value = mock_places
            
            result = mock_graph_nodes.retrieve_places_structured(sample_app_state)
            
            assert len(result["structured_candidates"]) == 2
            assert result["structured_candidates"][0].name == "台北101"
            assert result["error"] is None

    def test_retrieve_places_structured_error(self, mock_graph_nodes, sample_app_state):
        """測試檢索結構化地點時發生錯誤"""
        # 模擬 Story
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        sample_app_state["story"] = mock_story
        
        with patch('src.itinerary_planner.application.graph_nodes.SessionLocal') as mock_session_local, \
             patch('src.itinerary_planner.application.graph_nodes.PostgresPlaceRepository') as mock_repo:
            
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.search.side_effect = Exception("Database Error")
            
            result = mock_graph_nodes.retrieve_places_structured(sample_app_state)
            
            assert result["structured_candidates"] == []
            assert "Database Error" in result["error"]

    def test_retrieve_places_semantic_success(self, mock_graph_nodes, sample_app_state):
        """測試成功檢索語義地點"""
        # 模擬 Story
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        sample_app_state["story"] = mock_story
        
        # 模擬語義搜索結果
        mock_places = [
            Place(id="3", name="士林夜市", categories=["美食"], rating=4.8),
            Place(id="4", name="饒河夜市", categories=["美食"], rating=4.6)
        ]
        
        with patch('src.itinerary_planner.application.graph_nodes.SessionLocal') as mock_session_local, \
             patch('src.itinerary_planner.application.graph_nodes.PostgresPlaceRepository') as mock_repo, \
             patch('src.itinerary_planner.application.graph_nodes.embedding_client') as mock_embedding:
            
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.search_by_vector.return_value = mock_places
            mock_embedding.get_embedding.return_value = [0.1, 0.2, 0.3]
            
            result = mock_graph_nodes.retrieve_places_semantic(sample_app_state)
            
            assert len(result["semantic_candidates"]) == 2
            assert result["semantic_candidates"][0].name == "士林夜市"
            assert result["error"] is None

    def test_rank_and_merge_success(self, mock_graph_nodes, sample_app_state):
        """測試成功排序和合併"""
        # 模擬候選地點
        structured_places = [
            Place(id="1", name="台北101", categories=["景點"], rating=4.5),
            Place(id="2", name="西門町", categories=["購物"], rating=4.2)
        ]
        semantic_places = [
            Place(id="3", name="士林夜市", categories=["美食"], rating=4.8),
            Place(id="4", name="饒河夜市", categories=["美食"], rating=4.6)
        ]
        
        sample_app_state["structured_candidates"] = structured_places
        sample_app_state["semantic_candidates"] = semantic_places
        
        # 模擬 Story
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        sample_app_state["story"] = mock_story
        
        # 模擬重新排序結果
        mock_reranked_places = [
            Place(id="3", name="士林夜市", categories=["美食"], rating=4.8),
            Place(id="1", name="台北101", categories=["景點"], rating=4.5),
            Place(id="4", name="饒河夜市", categories=["美食"], rating=4.6),
            Place(id="2", name="西門町", categories=["購物"], rating=4.2)
        ]
        
        with patch('src.itinerary_planner.application.graph_nodes.rerank_service') as mock_rerank:
            mock_rerank.rerank.return_value = mock_reranked_places
            
            result = mock_graph_nodes.rank_and_merge(sample_app_state)
            
            assert len(result["candidates"]) == 4
            assert result["candidates"][0].name == "士林夜市"
            assert result["error"] is None

    def test_retrieve_accommodations_success(self, mock_graph_nodes, sample_app_state):
        """測試成功檢索住宿"""
        # 模擬候選地點
        mock_places = [
            Place(id="1", name="台北101", categories=["景點"], rating=4.5),
            Place(id="2", name="西門町", categories=["購物"], rating=4.2)
        ]
        sample_app_state["candidates"] = mock_places
        
        # 模擬 Story
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        sample_app_state["story"] = mock_story
        
        # 模擬住宿檢索結果
        mock_accommodations = [
            Mock(id="acc1", name="台北君悅酒店", type="hotel", rating=4.8),
            Mock(id="acc2", name="西門町青年旅館", type="hostel", rating=4.2)
        ]
        
        with patch('src.itinerary_planner.application.graph_nodes.SessionLocal') as mock_session_local, \
             patch('src.itinerary_planner.application.graph_nodes.PostgresAccommodationRepository') as mock_repo:
            
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            mock_repo_instance.search.return_value = mock_accommodations
            
            result = mock_graph_nodes.retrieve_accommodations(sample_app_state)
            
            assert len(result["accommodation_candidates"]) == 2
            assert result["accommodation_candidates"][0].name == "台北君悅酒店"
            assert result["error"] is None

    def test_plan_itinerary_success(self, mock_graph_nodes, sample_app_state):
        """測試成功規劃行程"""
        # 模擬候選地點和住宿
        mock_places = [
            Place(id="1", name="台北101", categories=["景點"], rating=4.5),
            Place(id="2", name="西門町", categories=["購物"], rating=4.2)
        ]
        mock_accommodations = [
            Mock(id="acc1", name="台北君悅酒店", type="hotel", rating=4.8)
        ]
        
        sample_app_state["candidates"] = mock_places
        sample_app_state["accommodation_candidates"] = mock_accommodations
        
        # 模擬 Story
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        sample_app_state["story"] = mock_story
        
        # 模擬行程規劃結果
        mock_itinerary = Mock()
        mock_itinerary.days = [Mock(), Mock(), Mock()]
        
        with patch('src.itinerary_planner.application.graph_nodes.greedy_planner') as mock_planner, \
             patch('src.itinerary_planner.application.graph_nodes.accommodation_recommendation_service') as mock_acc_service:
            
            mock_planner.plan.return_value = mock_itinerary
            mock_acc_service.recommend_accommodations_for_days.return_value = mock_itinerary.days
            
            result = mock_graph_nodes.plan_itinerary(sample_app_state)
            
            assert result["itinerary"] == mock_itinerary
            assert result["error"] is None

    def test_get_conversation_state_success(self, mock_graph_nodes):
        """測試成功獲取對話狀態"""
        # 模擬 Redis 中有對話狀態
        conversation_data = {
            "session_id": "test_session_123",
            "state_type": "COLLECTING_INFO",
            "collected_info": {"destination": "台北"},
            "conversation_history": []
        }
        mock_graph_nodes.redis_client.get.return_value = json.dumps(conversation_data)
        
        result = mock_graph_nodes._get_conversation_state("test_session_123")
        
        assert result is not None
        assert result.session_id == "test_session_123"
        assert result.state_type == ConversationStateType.COLLECTING_INFO

    def test_get_conversation_state_not_found(self, mock_graph_nodes):
        """測試獲取對話狀態 - 未找到"""
        # 模擬 Redis 中沒有對話狀態
        mock_graph_nodes.redis_client.get.return_value = None
        
        result = mock_graph_nodes._get_conversation_state("nonexistent_session")
        
        assert result is None

    def test_save_conversation_state(self, mock_graph_nodes, sample_conversation_state):
        """測試保存對話狀態"""
        mock_graph_nodes._save_conversation_state(sample_conversation_state)
        
        # 驗證 Redis set 被調用
        mock_graph_nodes.redis_client.setex.assert_called_once()
        call_args = mock_graph_nodes.redis_client.setex.call_args
        assert call_args[0][0] == f"conversation_state:{sample_conversation_state.session_id}"
        assert call_args[0][2] == 3600  # TTL

    def test_is_info_complete_true(self, mock_graph_nodes, sample_conversation_state):
        """測試資訊完整性檢查 - 完整"""
        # 設置完整資訊
        sample_conversation_state.collected_info = {
            "destination": "台北",
            "duration": "3天",
            "interests": "美食,文化",
            "budget": "中等",
            "travel_style": "輕鬆",
            "group_size": "2人"
        }
        
        result = mock_graph_nodes._is_info_complete(sample_conversation_state)
        
        assert result is True

    def test_is_info_complete_false(self, mock_graph_nodes, sample_conversation_state):
        """測試資訊完整性檢查 - 不完整"""
        # 設置不完整資訊
        sample_conversation_state.collected_info = {
            "destination": "台北",
            "duration": "3天"
        }
        
        result = mock_graph_nodes._is_info_complete(sample_conversation_state)
        
        assert result is False

    def test_fallback_keyword_analysis(self, mock_graph_nodes, sample_conversation_state):
        """測試回退關鍵字分析"""
        message = "我想去台北三天兩夜，喜歡美食和購物，預算中等"
        
        mock_graph_nodes._fallback_keyword_analysis(sample_conversation_state, message)
        
        # 驗證收集的資訊
        assert "台北" in sample_conversation_state.collected_info.get("destination", "")
        assert "3天" in sample_conversation_state.collected_info.get("duration", "")
        assert "美食" in sample_conversation_state.collected_info.get("interests", "")
        assert "購物" in sample_conversation_state.collected_info.get("interests", "")
        assert "中等" in sample_conversation_state.collected_info.get("budget", "")

    def test_generate_next_question_with_memory(self, mock_graph_nodes, sample_conversation_state):
        """測試使用記憶生成下一個問題"""
        # 設置部分收集的資訊
        sample_conversation_state.collected_info = {
            "destination": "台北",
            "duration": "3天"
        }
        
        result = mock_graph_nodes._generate_next_question_with_memory(sample_conversation_state)
        
        assert isinstance(result, str)
        assert len(result) > 0
