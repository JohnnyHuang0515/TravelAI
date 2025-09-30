from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from ....infrastructure.persistence.database import get_db
from ....application.services.conversation_service import ConversationService
from ....domain.entities.conversation_state import ConversationState

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    """聊天訊息模型"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    """聊天請求模型"""
    session_id: str
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    """聊天回應模型"""
    message: str
    conversation_state: str  # "collecting_info", "generating_itinerary", "completed"
    itinerary: Optional[Dict[str, Any]] = None
    questions: Optional[List[str]] = None
    is_complete: bool = False

class ItineraryCard(BaseModel):
    """行程卡片模型"""
    day: int
    date: str
    activities: List[Dict[str, Any]]
    total_duration: str
    theme: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    與 AI 進行對話式行程規劃
    """
    try:
        logger.info(f"Chat request for session {request.session_id}: {request.message}")
        
        # 初始化對話服務
        conversation_service = ConversationService(db)
        
        # 處理用戶訊息
        response = await conversation_service.process_message(
            session_id=request.session_id,
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/state/{session_id}")
async def get_conversation_state(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    獲取對話狀態
    """
    try:
        conversation_service = ConversationService(db)
        state = await conversation_service.get_conversation_state(session_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        return {
            "session_id": session_id,
            "state": state.state,
            "collected_info": state.collected_info,
            "is_complete": state.is_complete
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation state: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get conversation state: {str(e)}")

@router.post("/reset/{session_id}")
async def reset_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    重置對話狀態
    """
    try:
        conversation_service = ConversationService(db)
        await conversation_service.reset_conversation(session_id)
        
        return {"message": "Conversation reset successfully"}
        
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset conversation: {str(e)}")
