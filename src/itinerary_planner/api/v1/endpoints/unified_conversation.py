from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from ....infrastructure.persistence.database import get_db
from ....application.services.unified_conversation_engine import UnifiedConversationEngine
from ....application.services.intelligent_understanding import IntelligentUnderstandingService, ConversationContext
from ....application.services.performance_optimizer import PerformanceOptimizer
from ....domain.entities.conversation_state import ConversationStateType
from ....infrastructure.persistence.orm_models import User
from ..dependencies.auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()

# 請求模型
class ConversationMessage(BaseModel):
    """對話訊息模型"""
    message: str = Field(..., description="用戶訊息", min_length=1, max_length=1000)
    session_id: str = Field(..., description="會話ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="額外的元數據")

class ConversationRequest(BaseModel):
    """對話請求模型"""
    session_id: str = Field(..., description="會話ID")
    message: str = Field(..., description="用戶訊息", min_length=1, max_length=1000)
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="對話歷史")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用戶偏好")
    context: Optional[Dict[str, Any]] = Field(None, description="額外上下文")

class ConversationResponse(BaseModel):
    """對話回應模型"""
    session_id: str
    message: str
    intent: str
    suggestions: List[str]
    collected_info: Dict[str, Any]
    is_complete: bool
    itinerary: Optional[Dict[str, Any]] = None
    confidence_score: float
    turn_count: int
    timestamp: str
    error: Optional[str] = None

class ConversationStateResponse(BaseModel):
    """對話狀態回應模型"""
    session_id: str
    current_intent: Optional[str]
    collected_info: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    confidence_score: float
    last_activity: str
    turn_count: int

class PerformanceReportResponse(BaseModel):
    """性能報告回應模型"""
    summary: Dict[str, Any]
    operation_stats: Dict[str, Any]
    cache_stats: Dict[str, Any]
    generated_at: str

class HealthCheckResponse(BaseModel):
    """健康檢查回應模型"""
    timestamp: str
    status: str
    components: Dict[str, Any]

# 全域服務實例（在實際應用中應該使用依賴注入）
_conversation_engine: Optional[UnifiedConversationEngine] = None
_intelligent_understanding: Optional[IntelligentUnderstandingService] = None
_performance_optimizer: Optional[PerformanceOptimizer] = None

def get_conversation_engine(db: Session = Depends(get_db)) -> UnifiedConversationEngine:
    """獲取對話引擎實例"""
    global _conversation_engine
    if _conversation_engine is None:
        _conversation_engine = UnifiedConversationEngine(db)
    return _conversation_engine

def get_intelligent_understanding() -> IntelligentUnderstandingService:
    """獲取智能理解服務實例"""
    global _intelligent_understanding
    if _intelligent_understanding is None:
        _intelligent_understanding = IntelligentUnderstandingService()
    return _intelligent_understanding

def get_performance_optimizer(db: Session = Depends(get_db)) -> PerformanceOptimizer:
    """獲取性能優化器實例"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer(db)
    return _performance_optimizer

@router.post("/chat", response_model=ConversationResponse)
async def chat_with_ai(
    request: ConversationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    與AI進行對話式行程規劃
    """
    try:
        logger.info(f"Chat request for session {request.session_id}: {request.message[:100]}...")
        
        # 獲取服務實例
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 使用性能測量裝飾器
        @performance_optimizer.measure_performance("conversation_chat")
        async def process_conversation():
            return await conversation_engine.process_message(
                session_id=request.session_id,
                user_message=request.message,
                conversation_history=request.conversation_history
            )
        
        # 處理對話
        response_data = await process_conversation()
        
        # 在後台任務中進行性能優化
        background_tasks.add_task(performance_optimizer.optimize_memory_usage)
        
        # 返回統一格式的回應
        return ConversationResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/message", response_model=ConversationResponse)
async def send_message(
    message: ConversationMessage,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    發送單一訊息（簡化版API）
    """
    try:
        logger.info(f"Message request for session {message.session_id}")
        
        # 轉換為完整請求
        request = ConversationRequest(
            session_id=message.session_id,
            message=message.message,
            metadata=message.metadata
        )
        
        # 使用chat端點處理
        return await chat_with_ai(request, background_tasks, db)
        
    except Exception as e:
        logger.error(f"Error in message endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Message processing failed: {str(e)}")

@router.get("/state/{session_id}", response_model=ConversationStateResponse)
async def get_conversation_state(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    獲取對話狀態
    """
    try:
        logger.info(f"Getting conversation state for session {session_id}")
        
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 使用快取獲取狀態
        cache_key = f"conversation_state:{session_id}"
        cached_state = performance_optimizer.get_cached_result("conversation_context", cache_key)
        
        if cached_state:
            return ConversationStateResponse(**cached_state)
        
        # 從引擎獲取狀態
        state_data = await conversation_engine.get_conversation_state(session_id)
        
        if not state_data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 快取狀態
        performance_optimizer.cache_result("conversation_context", cache_key, state_data, ttl=300)
        
        return ConversationStateResponse(**state_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation state: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get conversation state: {str(e)}")

@router.post("/reset/{session_id}")
async def reset_conversation(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    重置對話狀態
    """
    try:
        logger.info(f"Resetting conversation for session {session_id}")
        
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 重置對話
        success = await conversation_engine.reset_conversation(session_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset conversation")
        
        # 在後台清理相關快取
        background_tasks.add_task(
            performance_optimizer.invalidate_cache, 
            "conversation_context", 
            session_id
        )
        
        return {"message": "Conversation reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset conversation: {str(e)}")

@router.post("/analyze")
async def analyze_message(
    message: ConversationMessage,
    db: Session = Depends(get_db)
):
    """
    分析訊息（用於測試和調試）
    """
    try:
        logger.info(f"Analyzing message for session {message.session_id}")
        
        intelligent_understanding = get_intelligent_understanding()
        performance_optimizer = get_performance_optimizer(db)
        
        # 創建對話上下文
        context = ConversationContext(
            session_id=message.session_id,
            user_profile={},
            conversation_memory={},
            recent_intents=[],
            extracted_entities=[],
            conversation_history=[],
            last_activity=datetime.now()
        )
        
        # 使用性能測量
        @performance_optimizer.measure_performance("message_analysis")
        async def analyze():
            return await intelligent_understanding.analyze_message(message.message, context)
        
        analysis_result = await analyze()
        
        return {
            "session_id": message.session_id,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Message analysis failed: {str(e)}")

@router.get("/performance", response_model=PerformanceReportResponse)
async def get_performance_report(
    db: Session = Depends(get_db)
):
    """
    獲取性能報告
    """
    try:
        logger.info("Generating performance report")
        
        performance_optimizer = get_performance_optimizer(db)
        report = performance_optimizer.get_performance_report()
        
        return PerformanceReportResponse(**report)
        
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate performance report: {str(e)}")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    db: Session = Depends(get_db)
):
    """
    健康檢查
    """
    try:
        performance_optimizer = get_performance_optimizer(db)
        health_status = await performance_optimizer.health_check()
        
        return HealthCheckResponse(**health_status)
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}", exc_info=True)
        return HealthCheckResponse(
            timestamp=datetime.now().isoformat(),
            status="unhealthy",
            components={"error": str(e)}
        )

@router.post("/cache/invalidate")
async def invalidate_cache(
    cache_type: str,
    key: Optional[str] = None,
    tags: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    使快取失效
    """
    try:
        logger.info(f"Invalidating cache for type: {cache_type}, key: {key}")
        
        performance_optimizer = get_performance_optimizer(db)
        
        # 在後台任務中執行快取失效
        if background_tasks:
            background_tasks.add_task(
                performance_optimizer.invalidate_cache,
                cache_type,
                key,
                tags
            )
        else:
            performance_optimizer.invalidate_cache(cache_type, key, tags)
        
        return {"message": "Cache invalidation scheduled"}
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to invalidate cache: {str(e)}")

@router.post("/cache/cleanup")
async def cleanup_cache(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    清理過期快取
    """
    try:
        logger.info("Cleaning up expired cache")
        
        performance_optimizer = get_performance_optimizer(db)
        
        # 在後台任務中清理快取
        background_tasks.add_task(performance_optimizer.cleanup_expired_cache)
        
        return {"message": "Cache cleanup scheduled"}
        
    except Exception as e:
        logger.error(f"Error cleaning up cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to cleanup cache: {str(e)}")

@router.get("/suggestions/{session_id}")
async def get_suggestions(
    session_id: str,
    context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    獲取智能建議
    """
    try:
        logger.info(f"Getting suggestions for session {session_id}")
        
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 獲取對話狀態
        state_data = await conversation_engine.get_conversation_state(session_id)
        
        if not state_data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 根據狀態生成建議
        suggestions = []
        collected_info = state_data.get("collected_info", {})
        
        if not collected_info.get("destination"):
            suggestions.append("告訴我您想去哪裡旅遊")
        elif not collected_info.get("duration"):
            suggestions.append("告訴我您計劃旅遊幾天")
        elif not collected_info.get("interests"):
            suggestions.append("告訴我您的興趣偏好")
        else:
            suggestions.extend([
                "我想調整行程",
                "推薦附近景點",
                "修改預算安排",
                "查看詳細行程"
            ])
        
        # 快取建議
        cache_key = f"suggestions:{session_id}"
        performance_optimizer.cache_result("suggestions", cache_key, suggestions, ttl=300)
        
        return {
            "session_id": session_id,
            "suggestions": suggestions,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@router.get("/stats/{session_id}")
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    獲取會話統計信息
    """
    try:
        logger.info(f"Getting stats for session {session_id}")
        
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 獲取對話狀態
        state_data = await conversation_engine.get_conversation_state(session_id)
        
        if not state_data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 計算統計信息
        stats = {
            "session_id": session_id,
            "turn_count": state_data.get("turn_count", 0),
            "collected_info_count": len(state_data.get("collected_info", {})),
            "confidence_score": state_data.get("confidence_score", 0.0),
            "last_activity": state_data.get("last_activity"),
            "conversation_duration": None,
            "completion_rate": 0.0
        }
        
        # 計算完成率
        required_fields = ["destination", "duration", "interests"]
        collected_fields = [k for k in required_fields if state_data.get("collected_info", {}).get(k)]
        stats["completion_rate"] = len(collected_fields) / len(required_fields)
        
        # 計算對話持續時間
        if state_data.get("conversation_history"):
            first_message = state_data["conversation_history"][0]
            last_message = state_data["conversation_history"][-1]
            
            try:
                first_time = datetime.fromisoformat(first_message["timestamp"].replace('Z', '+00:00'))
                last_time = datetime.fromisoformat(last_message["timestamp"].replace('Z', '+00:00'))
                duration = (last_time - first_time).total_seconds()
                stats["conversation_duration"] = duration
            except Exception as e:
                logger.warning(f"Error parsing timestamps: {e}")
        
        return {
            **stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get session stats: {str(e)}")

@router.get("/search/{session_id}")
async def search_places(
    session_id: str,
    query: Optional[str] = None,
    search_type: str = "hybrid",  # hybrid, structured, semantic
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """RAG 搜尋景點"""
    
    try:
        logger.info(f"RAG search for session {session_id}, query: {query}")
        
        conversation_engine = get_conversation_engine(db)
        context = await conversation_engine._get_or_create_context(session_id)
        
        # 如果提供了查詢，更新上下文
        if query:
            # 提取實體信息
            entities = await conversation_engine._extract_entities(query, context)
            context.update_entities(entities)
        
        # 執行 RAG 搜尋
        places = await conversation_engine._rag_search_places(context)
        accommodations = await conversation_engine._rag_search_accommodations(context)
        
        return {
            "session_id": session_id,
            "search_type": search_type,
            "places": [
                {
                    "name": place.name,
                    "categories": getattr(place, 'categories', []),
                    "rating": getattr(place, 'rating', 0),
                    "recommendation_reason": getattr(place, 'recommendation_reason', ''),
                    "location": {
                        "lat": getattr(place, 'latitude', 0),
                        "lng": getattr(place, 'longitude', 0)
                    }
                } for place in places
            ],
            "accommodations": [
                {
                    "name": acc.name,
                    "type": getattr(acc, 'accommodation_type', ''),
                    "rating": getattr(acc, 'rating', 0),
                    "recommendation_reason": getattr(acc, 'recommendation_reason', ''),
                    "location": {
                        "lat": getattr(acc, 'latitude', 0),
                        "lng": getattr(acc, 'longitude', 0)
                    }
                } for acc in accommodations
            ],
            "search_context": context.search_context,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching places for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explanation/{session_id}")
async def get_recommendation_explanation(
    session_id: str,
    item_name: str,
    item_type: str,  # place, accommodation
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """獲取推薦解釋"""
    
    try:
        logger.info(f"Getting explanation for {item_name} ({item_type}) in session {session_id}")
        
        conversation_engine = get_conversation_engine(db)
        context = await conversation_engine._get_or_create_context(session_id)
        
        # 生成詳細的推薦解釋
        explanation = await conversation_engine._generate_detailed_explanation(
            item_name, item_type, context
        )
        
        return {
            "session_id": session_id,
            "item_name": item_name,
            "item_type": item_type,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting explanation for {item_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 批量操作端點
@router.post("/batch/chat")
async def batch_chat(
    requests: List[ConversationRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    批量處理對話請求
    """
    try:
        logger.info(f"Processing batch chat with {len(requests)} requests")
        
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 批量處理
        async def process_single_request(request):
            return await conversation_engine.process_message(
                session_id=request.session_id,
                user_message=request.message,
                conversation_history=request.conversation_history
            )
        
        results = await performance_optimizer.batch_process(
            requests,
            process_single_request,
            batch_size=5,
            max_concurrent=3
        )
        
        # 在後台優化內存
        background_tasks.add_task(performance_optimizer.optimize_memory_usage)
        
        return {
            "results": results,
            "total_processed": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch chat processing failed: {str(e)}")

@router.post("/batch/reset")
async def batch_reset_conversations(
    session_ids: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    批量重置對話
    """
    try:
        logger.info(f"Batch resetting {len(session_ids)} conversations")
        
        conversation_engine = get_conversation_engine(db)
        performance_optimizer = get_performance_optimizer(db)
        
        # 批量重置
        async def reset_single_session(session_id):
            return await conversation_engine.reset_conversation(session_id)
        
        results = await performance_optimizer.batch_process(
            session_ids,
            reset_single_session,
            batch_size=10
        )
        
        # 在後台清理快取
        background_tasks.add_task(performance_optimizer.cleanup_expired_cache)
        
        successful_count = sum(1 for result in results if result is True)
        
        return {
            "total_requested": len(session_ids),
            "successful_resets": successful_count,
            "failed_resets": len(session_ids) - successful_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch reset: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch reset failed: {str(e)}")
