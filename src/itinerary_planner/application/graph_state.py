from typing import TypedDict, List, Optional, Dict, Any
from ..domain.models.story import Story
from ..domain.models.itinerary import Itinerary
from ..infrastructure.persistence.orm_models import Place
from ..domain.entities.conversation_state import ConversationState, ConversationStateType

class AppState(TypedDict):
    """LangGraph 的狀態 - 支援單次對話記憶"""
    # 基本輸入
    user_input: str
    session_id: str
    
    # 對話狀態
    conversation_state: Optional[ConversationState]
    conversation_history: List[Dict[str, str]]
    collected_info: Dict[str, Any]
    is_info_complete: bool
    
    # 新增：單次對話記憶
    conversation_memory: Dict[str, Any]  # 會話級別的記憶
    context_summary: str  # 上下文摘要
    previous_responses: List[str]  # 之前的AI回應
    turn_count: int  # 對話輪次
    
    # 原有狀態
    story: Optional[Story]
    structured_candidates: List[Place]
    semantic_candidates: List[Place]
    candidates: List[Place] # 融合後的最終列表
    accommodation_candidates: List[Any]
    itinerary: Optional[Itinerary]
    error: Optional[str]
    
    # 對話回應
    ai_response: Optional[str]
    next_question: Optional[str]
