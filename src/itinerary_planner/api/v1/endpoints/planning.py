from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from ....domain.models.itinerary import Itinerary
from ....application.services.feedback_parser import feedback_parser
from ....application.services.planning_service import greedy_planner
from ....infrastructure.persistence.orm_models import User
from ....infrastructure.repositories.user_repository import UserPreferenceRepository
from ....infrastructure.persistence.database import get_db
from ..dependencies.auth import get_current_user_optional
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

class ProposeRequest(BaseModel):
    session_id: str
    text: str

class FeedbackRequest(BaseModel):
    session_id: str
    itinerary: Itinerary
    feedback_text: str

@router.post("/propose")
async def propose_itinerary(
    request: ProposeRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    根據使用者的自然語言輸入，生成一份行程草案。
    支援對話式規劃，會自動收集必要資訊。
    
    **會員專屬功能**：
    - 自動套用使用者偏好（興趣、節奏、預算）
    - 自動設定預設時間窗
    - 記錄行程規劃歷史
    """
    from ....application.graph import app_graph
    
    # 如果是會員，讀取偏好設定
    user_preferences = None
    if current_user:
        pref_repo = UserPreferenceRepository(db)
        user_preferences = pref_repo.get_by_user_id(str(current_user.id))
        logger.info(f"會員 {current_user.email} 使用個性化設定規劃行程")
    
    # 使用 LangGraph 處理請求 - 支援單次對話記憶
    initial_state = {
        "user_input": request.text,
        "session_id": request.session_id,
        "user_id": str(current_user.id) if current_user else None,  # 新增：記錄使用者 ID
        "user_preferences": {  # 新增：使用者偏好
            "favorite_themes": user_preferences.favorite_themes if user_preferences else None,
            "travel_pace": user_preferences.travel_pace if user_preferences else "moderate",
            "budget_level": user_preferences.budget_level if user_preferences else "moderate",
            "default_daily_start": str(user_preferences.default_daily_start) if user_preferences else "09:00",
            "default_daily_end": str(user_preferences.default_daily_end) if user_preferences else "18:00"
        } if current_user else None,
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
        "next_question": None
    }
    
    try:
        result = await app_graph.ainvoke(initial_state)
        
        # 檢查是否有錯誤
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        # 檢查是否還在收集資訊
        if not result.get("is_info_complete", False):
            # 返回需要更多資訊的回應
            return {
                "session_id": result["session_id"],
                "message": result.get("ai_response", "請提供更多資訊"),
                "is_complete": False,
                "next_question": result.get("next_question"),
                "collected_info": result.get("collected_info", {}),
                "days": []
            }
        
        # 返回完整的行程
        itinerary = result.get("itinerary")
        if itinerary is None:
            raise HTTPException(status_code=500, detail="Failed to generate itinerary")
        
        return itinerary
        
    except Exception as e:
        logger.error(f"Error in propose_itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback", response_model=Itinerary)
def handle_itinerary_feedback(request: FeedbackRequest):
    """
    接收使用者對行程的修改指令，並返回一個更新後的行程。
    """
    # 1. 解析回饋文本為 DSL
    dsl = feedback_parser.parse(request.feedback_text)
    if not dsl:
        raise HTTPException(status_code=400, detail="Could not understand the feedback.")

    # 2. 呼叫服務層處理 DSL
    updated_itinerary = greedy_planner.handle_feedback(request.itinerary, dsl)

    return updated_itinerary