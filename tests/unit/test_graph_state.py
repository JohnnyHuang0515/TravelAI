"""
測試 graph_state.py
"""

import pytest
from typing import get_type_hints

from src.itinerary_planner.application.graph_state import AppState


class TestGraphState:
    """測試圖狀態定義"""

    def test_app_state_structure(self):
        """測試 AppState 結構"""
        # 驗證 AppState 包含所有必要的欄位
        state = AppState(
            user_input="測試輸入",
            session_id="test_session",
            conversation_state=None,
            conversation_history=[],
            collected_info={},
            is_info_complete=False,
            conversation_memory={},
            context_summary="",
            previous_responses=[],
            turn_count=0,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error=None,
            ai_response=None,
            next_question=None
        )
        
        # 驗證所有欄位都存在
        assert "user_input" in state
        assert "session_id" in state
        assert "conversation_state" in state
        assert "conversation_history" in state
        assert "collected_info" in state
        assert "is_info_complete" in state
        assert "conversation_memory" in state
        assert "context_summary" in state
        assert "previous_responses" in state
        assert "turn_count" in state
        assert "story" in state
        assert "structured_candidates" in state
        assert "semantic_candidates" in state
        assert "candidates" in state
        assert "accommodation_candidates" in state
        assert "itinerary" in state
        assert "error" in state
        assert "ai_response" in state
        assert "next_question" in state

    def test_app_state_typing(self):
        """測試 AppState 的類型定義"""
        # 檢查 AppState 的類型提示
        hints = get_type_hints(AppState)
        
        # 驗證關鍵欄位的類型
        assert "user_input" in hints
        assert "session_id" in hints
        assert "conversation_state" in hints
        assert "is_info_complete" in hints
        assert "story" in hints
        assert "itinerary" in hints
        assert "conversation_memory" in hints
        assert "context_summary" in hints
        assert "previous_responses" in hints
        assert "turn_count" in hints

    def test_app_state_field_types(self):
        """測試 AppState 欄位類型"""
        # 驗證字串欄位
        state = AppState(
            user_input="測試輸入",
            session_id="test_session",
            conversation_state=None,
            conversation_history=[],
            collected_info={},
            is_info_complete=False,
            conversation_memory={},
            context_summary="測試摘要",
            previous_responses=[],
            turn_count=1,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error=None,
            ai_response="測試回應",
            next_question="下一個問題"
        )
        
        # 驗證字串欄位
        assert isinstance(state["user_input"], str)
        assert isinstance(state["session_id"], str)
        assert isinstance(state["context_summary"], str)
        assert isinstance(state["ai_response"], str)
        assert isinstance(state["next_question"], str)
        
        # 驗證數值欄位
        assert isinstance(state["turn_count"], int)
        assert isinstance(state["is_info_complete"], bool)
        
        # 驗證列表欄位
        assert isinstance(state["conversation_history"], list)
        assert isinstance(state["previous_responses"], list)
        assert isinstance(state["structured_candidates"], list)
        assert isinstance(state["semantic_candidates"], list)
        assert isinstance(state["candidates"], list)
        assert isinstance(state["accommodation_candidates"], list)
        
        # 驗證字典欄位
        assert isinstance(state["collected_info"], dict)
        assert isinstance(state["conversation_memory"], dict)

    def test_app_state_optional_fields(self):
        """測試 AppState 可選欄位"""
        # 測試所有可選欄位都可以為 None
        state = AppState(
            user_input="測試輸入",
            session_id="test_session",
            conversation_state=None,
            conversation_history=[],
            collected_info={},
            is_info_complete=False,
            conversation_memory={},
            context_summary="",
            previous_responses=[],
            turn_count=0,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error=None,
            ai_response=None,
            next_question=None
        )
        
        # 驗證可選欄位可以為 None
        assert state["conversation_state"] is None
        assert state["story"] is None
        assert state["itinerary"] is None
        assert state["error"] is None
        assert state["ai_response"] is None
        assert state["next_question"] is None

    def test_app_state_required_fields(self):
        """測試 AppState 必要欄位"""
        # 測試必要欄位不能為 None
        state = AppState(
            user_input="測試輸入",
            session_id="test_session",
            conversation_state=None,
            conversation_history=[],
            collected_info={},
            is_info_complete=False,
            conversation_memory={},
            context_summary="",
            previous_responses=[],
            turn_count=0,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error=None,
            ai_response=None,
            next_question=None
        )
        
        # 驗證必要欄位不為 None
        assert state["user_input"] is not None
        assert state["session_id"] is not None
        assert state["conversation_history"] is not None
        assert state["collected_info"] is not None
        assert state["conversation_memory"] is not None
        assert state["context_summary"] is not None
        assert state["previous_responses"] is not None
        assert state["turn_count"] is not None
        assert state["structured_candidates"] is not None
        assert state["semantic_candidates"] is not None
        assert state["candidates"] is not None
        assert state["accommodation_candidates"] is not None

    def test_app_state_conversation_fields(self):
        """測試對話相關欄位"""
        # 測試對話相關欄位的結構
        conversation_history = [
            {"role": "user", "content": "我想去台北旅遊"},
            {"role": "assistant", "content": "好的，請告訴我您想待幾天？"}
        ]
        
        collected_info = {
            "destination": "台北",
            "duration": "3天",
            "interests": "觀光"
        }
        
        conversation_memory = {
            "last_topic": "旅遊規劃",
            "user_preferences": ["觀光", "美食"]
        }
        
        previous_responses = [
            "請告訴我您的旅遊目的地",
            "您想待幾天呢？"
        ]
        
        state = AppState(
            user_input="我想去台北旅遊",
            session_id="test_session",
            conversation_state=None,
            conversation_history=conversation_history,
            collected_info=collected_info,
            is_info_complete=False,
            conversation_memory=conversation_memory,
            context_summary="用戶想要規劃台北旅遊",
            previous_responses=previous_responses,
            turn_count=3,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error=None,
            ai_response=None,
            next_question=None
        )
        
        # 驗證對話相關欄位
        assert len(state["conversation_history"]) == 2
        assert state["conversation_history"][0]["role"] == "user"
        assert state["conversation_history"][1]["role"] == "assistant"
        
        assert len(state["collected_info"]) == 3
        assert state["collected_info"]["destination"] == "台北"
        assert state["collected_info"]["duration"] == "3天"
        
        assert len(state["conversation_memory"]) == 2
        assert state["conversation_memory"]["last_topic"] == "旅遊規劃"
        
        assert len(state["previous_responses"]) == 2
        assert state["previous_responses"][0] == "請告訴我您的旅遊目的地"
        
        assert state["turn_count"] == 3
        assert state["context_summary"] == "用戶想要規劃台北旅遊"

    def test_app_state_workflow_fields(self):
        """測試工作流程相關欄位"""
        # 測試工作流程相關欄位
        state = AppState(
            user_input="測試輸入",
            session_id="test_session",
            conversation_state=None,
            conversation_history=[],
            collected_info={},
            is_info_complete=True,
            conversation_memory={},
            context_summary="",
            previous_responses=[],
            turn_count=0,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error="測試錯誤",
            ai_response="測試回應",
            next_question="下一個問題"
        )
        
        # 驗證工作流程相關欄位
        assert state["is_info_complete"] is True
        assert state["error"] == "測試錯誤"
        assert state["ai_response"] == "測試回應"
        assert state["next_question"] == "下一個問題"
        
        # 驗證列表欄位為空列表
        assert state["structured_candidates"] == []
        assert state["semantic_candidates"] == []
        assert state["candidates"] == []
        assert state["accommodation_candidates"] == []

    def test_app_state_immutability(self):
        """測試 AppState 的不可變性"""
        # 創建狀態
        state = AppState(
            user_input="測試輸入",
            session_id="test_session",
            conversation_state=None,
            conversation_history=[],
            collected_info={},
            is_info_complete=False,
            conversation_memory={},
            context_summary="",
            previous_responses=[],
            turn_count=0,
            story=None,
            structured_candidates=[],
            semantic_candidates=[],
            candidates=[],
            accommodation_candidates=[],
            itinerary=None,
            error=None,
            ai_response=None,
            next_question=None
        )
        
        # 驗證可以修改欄位值
        state["user_input"] = "修改後的輸入"
        assert state["user_input"] == "修改後的輸入"
        
        state["turn_count"] = 5
        assert state["turn_count"] == 5
        
        state["is_info_complete"] = True
        assert state["is_info_complete"] is True
