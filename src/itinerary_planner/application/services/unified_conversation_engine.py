from typing import Dict, List, Optional, Any, Union
import logging
import json
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import redis
from sqlalchemy.orm import Session

from ...domain.entities.conversation_state import ConversationState, ConversationStateType
from ...infrastructure.clients.gemini_llm_client import GeminiLLMClient
from ...infrastructure.clients.embedding_client import embedding_client
from ...domain.models.story import Story
from ...domain.models.itinerary import Itinerary
from ..graph_nodes import GraphNodes
from ...infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
from ...infrastructure.repositories.postgres_accommodation_repo import PostgresAccommodationRepository
from ...infrastructure.persistence.database import SessionLocal

logger = logging.getLogger(__name__)

class ConversationIntent(Enum):
    """對話意圖類型"""
    GREETING = "greeting"
    PROVIDE_INFO = "provide_info"
    ASK_QUESTION = "ask_question"
    MODIFY_REQUEST = "modify_request"
    CONFIRM = "confirm"
    REJECT = "reject"
    UNKNOWN = "unknown"

class ConversationContext:
    """對話上下文管理"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_intent: Optional[ConversationIntent] = None
        self.extracted_entities: Dict[str, Any] = {}
        self.user_preferences: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, Any]] = []
        self.last_activity = datetime.now()
        self.confidence_score: float = 0.0
        self.search_context: Dict[str, Any] = {}  # 搜尋上下文
        self.previous_searches: List[Dict[str, Any]] = []  # 之前的搜尋記錄
        
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加對話訊息到歷史"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.last_activity = datetime.now()
        
    def get_recent_context(self, limit: int = 5) -> str:
        """獲取最近的對話上下文"""
        recent_messages = self.conversation_history[-limit:]
        context_parts = []
        for msg in recent_messages:
            role = "用戶" if msg["role"] == "user" else "AI"
            context_parts.append(f"{role}: {msg['content']}")
        return "\n".join(context_parts)
        
    def update_entities(self, entities: Dict[str, Any]):
        """更新實體信息"""
        self.extracted_entities.update(entities)
        
    def update_preferences(self, preferences: Dict[str, Any]):
        """更新用戶偏好"""
        self.user_preferences.update(preferences)

class UnifiedConversationEngine:
    """統一對話引擎 - 整合所有對話功能"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.llm_client = GeminiLLMClient()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # 初始化圖形節點（用於行程規劃）
        self.graph_nodes = GraphNodes()
        
        # 定義需要收集的核心資訊
        self.core_info_fields = {
            "destination": {"required": True, "type": "string", "description": "目的地"},
            "duration": {"required": True, "type": "number", "description": "旅遊天數"},
            "interests": {"required": True, "type": "list", "description": "興趣類型"},
            "budget": {"required": False, "type": "string", "description": "預算範圍"},
            "travel_style": {"required": False, "type": "string", "description": "旅遊風格"},
            "group_size": {"required": False, "type": "number", "description": "人數"},
            "start_date": {"required": False, "type": "date", "description": "出發日期"}
        }
        
        # 意圖識別提示詞
        self.intent_prompts = {
            ConversationIntent.GREETING: "用戶正在打招呼或開始對話",
            ConversationIntent.PROVIDE_INFO: "用戶正在提供旅遊相關信息",
            ConversationIntent.ASK_QUESTION: "用戶正在詢問問題",
            ConversationIntent.MODIFY_REQUEST: "用戶想要修改現有行程",
            ConversationIntent.CONFIRM: "用戶正在確認某個選擇",
            ConversationIntent.REJECT: "用戶正在拒絕某個建議"
        }
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """處理用戶訊息的主入口"""
        
        try:
            # 獲取或創建對話上下文
            context = await self._get_or_create_context(session_id)
            
            # 添加用戶訊息到上下文
            context.add_message("user", user_message)
            
            # 1. 智能意圖識別
            intent = await self._analyze_intent(user_message, context)
            context.current_intent = intent
            
            logger.info(f"Detected intent: {intent.value} for session {session_id}")
            
            # 2. 根據意圖處理訊息
            response = await self._handle_intent(intent, user_message, context)
            
            # 3. 添加AI回應到上下文
            context.add_message("assistant", response.get("message", ""))
            
            # 4. 保存上下文狀態
            await self._save_context(context)
            
            # 5. 返回統一格式的回應
            return self._format_response(response, context)
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {e}")
            return self._create_error_response(str(e))
    
    async def _get_or_create_context(self, session_id: str) -> ConversationContext:
        """獲取或創建對話上下文"""
        
        # 嘗試從Redis獲取上下文
        context_data = self.redis_client.get(f"conversation_context:{session_id}")
        
        if context_data:
            try:
                data = json.loads(context_data)
                context = ConversationContext(session_id)
                context.current_intent = ConversationIntent(data.get("current_intent")) if data.get("current_intent") else None
                context.extracted_entities = data.get("extracted_entities", {})
                context.user_preferences = data.get("user_preferences", {})
                context.conversation_history = data.get("conversation_history", [])
                context.confidence_score = data.get("confidence_score", 0.0)
                return context
            except Exception as e:
                logger.warning(f"Failed to deserialize context for session {session_id}: {e}")
        
        # 創建新上下文
        return ConversationContext(session_id)
    
    async def _analyze_intent(self, message: str, context: ConversationContext) -> ConversationIntent:
        """使用LLM分析用戶意圖"""
        
        # 構建意圖分析提示詞
        recent_context = context.get_recent_context(3)
        collected_info = json.dumps(context.extracted_entities, ensure_ascii=False)
        
        prompt = f"""
你是一個專業的旅遊助手，需要分析用戶的對話意圖。

對話歷史：
{recent_context}

已收集的信息：
{collected_info}

當前用戶訊息：{message}

請分析用戶的意圖，並從以下選項中選擇最合適的一個：
1. greeting - 用戶正在打招呼或開始對話
2. provide_info - 用戶正在提供旅遊相關信息（如目的地、天數、興趣、偏好等）
3. ask_question - 用戶正在詢問問題
4. modify_request - 用戶想要修改現有行程或需求
5. confirm - 用戶正在確認某個選擇
6. reject - 用戶正在拒絕某個建議
7. unknown - 無法確定意圖

特別注意：
- 如果用戶提到旅遊相關的詞彙（如地名、天數、興趣類型如"美食"、"文化"、"自然"等），通常是provide_info
- 如果用戶在回答問題或補充信息，通常是provide_info
- 如果用戶問"什麼"、"怎麼"、"哪裡"等疑問詞，通常是ask_question

請只返回意圖名稱，不要其他內容。
"""
        
        try:
            response = self.llm_client.generate_text(prompt)
            intent_name = response.strip().lower()
            
            # 映射到意圖枚舉
            intent_mapping = {
                "greeting": ConversationIntent.GREETING,
                "provide_info": ConversationIntent.PROVIDE_INFO,
                "ask_question": ConversationIntent.ASK_QUESTION,
                "modify_request": ConversationIntent.MODIFY_REQUEST,
                "confirm": ConversationIntent.CONFIRM,
                "reject": ConversationIntent.REJECT,
                "unknown": ConversationIntent.UNKNOWN
            }
            
            return intent_mapping.get(intent_name, ConversationIntent.UNKNOWN)
            
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return ConversationIntent.UNKNOWN
    
    async def _handle_intent(
        self, 
        intent: ConversationIntent, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """根據意圖處理用戶訊息"""
        
        if intent == ConversationIntent.GREETING:
            return await self._handle_greeting(message, context)
        elif intent == ConversationIntent.PROVIDE_INFO:
            return await self._handle_provide_info(message, context)
        elif intent == ConversationIntent.ASK_QUESTION:
            return await self._handle_ask_question(message, context)
        elif intent == ConversationIntent.MODIFY_REQUEST:
            return await self._handle_modify_request(message, context)
        elif intent == ConversationIntent.CONFIRM:
            return await self._handle_confirm(message, context)
        elif intent == ConversationIntent.REJECT:
            return await self._handle_reject(message, context)
        else:
            return await self._handle_unknown(message, context)
    
    async def _handle_greeting(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理打招呼意圖"""
        
        # 檢查是否已經有基本信息
        has_basic_info = any(
            context.extracted_entities.get(field) 
            for field in ["destination", "duration", "interests"]
        )
        
        if has_basic_info:
            response_message = "您好！我看到您已經提供了一些旅遊信息。有什麼我可以幫您調整或補充的嗎？"
        else:
            response_message = "您好！我是您的專屬旅遊助手，可以幫您規劃完美的旅程。請告訴我您想去哪裡旅遊呢？"
        
        return {
            "message": response_message,
            "intent": ConversationIntent.GREETING.value,
            "suggestions": self._generate_suggestions(context),
            "collected_info": context.extracted_entities,
            "is_complete": False
        }
    
    async def _handle_provide_info(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理提供信息意圖"""
        
        # 提取實體信息
        entities = await self._extract_entities(message, context)
        context.update_entities(entities)
        
        # 檢查信息完整性
        is_complete = self._is_info_complete(context.extracted_entities)
        
        if is_complete:
            # 信息完整，開始生成行程
            return await self._generate_itinerary(context)
        else:
            # 繼續收集信息
            next_question = await self._generate_next_question(context)
            return {
                "message": next_question,
                "intent": ConversationIntent.PROVIDE_INFO.value,
                "suggestions": self._generate_suggestions(context),
                "collected_info": context.extracted_entities,
                "is_complete": False
            }
    
    async def _handle_ask_question(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理詢問意圖"""
        
        # 使用LLM回答用戶問題
        response_message = await self._answer_question(message, context)
        
        return {
            "message": response_message,
            "intent": ConversationIntent.ASK_QUESTION.value,
            "suggestions": self._generate_suggestions(context),
            "collected_info": context.extracted_entities,
            "is_complete": False
        }
    
    async def _handle_modify_request(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理修改請求意圖"""
        
        # 解析修改請求
        modifications = await self._parse_modifications(message, context)
        
        # 更新實體信息
        for key, value in modifications.items():
            context.extracted_entities[key] = value
        
        response_message = "好的，我已經記錄您的修改需求。讓我為您重新規劃行程。"
        
        # 如果信息完整，重新生成行程
        if self._is_info_complete(context.extracted_entities):
            itinerary_result = await self._generate_itinerary(context)
            response_message += f"\n\n{itinerary_result['message']}"
            return {
                **itinerary_result,
                "message": response_message,
                "intent": ConversationIntent.MODIFY_REQUEST.value
            }
        
        return {
            "message": response_message,
            "intent": ConversationIntent.MODIFY_REQUEST.value,
            "suggestions": self._generate_suggestions(context),
            "collected_info": context.extracted_entities,
            "is_complete": False
        }
    
    async def _handle_confirm(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理確認意圖"""
        
        # 確認用戶的選擇
        response_message = "好的，我確認您的選擇。"
        
        # 如果信息完整，生成行程
        if self._is_info_complete(context.extracted_entities):
            return await self._generate_itinerary(context)
        
        return {
            "message": response_message,
            "intent": ConversationIntent.CONFIRM.value,
            "suggestions": self._generate_suggestions(context),
            "collected_info": context.extracted_entities,
            "is_complete": False
        }
    
    async def _handle_reject(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理拒絕意圖"""
        
        # 了解用戶的拒絕原因並提供替代方案
        response_message = "我理解您的想法。讓我為您提供其他選項。"
        
        # 生成替代建議
        alternatives = await self._generate_alternatives(message, context)
        
        return {
            "message": response_message,
            "intent": ConversationIntent.REJECT.value,
            "suggestions": alternatives,
            "collected_info": context.extracted_entities,
            "is_complete": False
        }
    
    async def _handle_unknown(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """處理未知意圖"""
        
        # 即使意圖不明確，也要嘗試提取實體信息
        entities = await self._extract_entities(message, context)
        if entities:
            context.update_entities(entities)
            
            # 如果有實體信息，當作提供信息處理
            if context.extracted_entities:
                return await self._handle_provide_info(message, context)
        
        # 如果確實無法理解，根據已有信息給出智能回應
        if context.extracted_entities:
            response_message = self._generate_contextual_response(context)
        else:
            response_message = "抱歉，我沒有完全理解您的意思。您是想提供旅遊信息、詢問問題，還是有其他需求呢？"
        
        return {
            "message": response_message,
            "intent": ConversationIntent.UNKNOWN.value,
            "suggestions": self._generate_suggestions(context),
            "collected_info": context.extracted_entities,
            "is_complete": False
        }
    
    async def _extract_entities(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """提取實體信息"""
        
        prompt = f"""
你是一個專業的旅遊信息提取助手。請從用戶的訊息中提取旅遊相關信息。

用戶訊息：{message}

請提取以下信息（如果有的話）：
- destination: 目的地（城市或地區名稱）
- duration: 旅遊天數（數字）
- interests: 興趣類型（列表，如美食、文化、自然等）
- budget: 預算範圍（經濟、中等、豪華）
- travel_style: 旅遊風格（悠閒、適中、緊湊）
- group_size: 人數（數字）
- start_date: 出發日期（YYYY-MM-DD格式）

請以JSON格式返回，只包含實際提取到的信息。如果沒有提取到任何信息，返回空對象 {{}}。

範例格式：
{{"destination": "台北", "duration": 3, "interests": ["美食", "文化"]}}

請只返回JSON格式，不要其他文字：
"""
        
        try:
            response = self.llm_client.generate_text(prompt)
            # 嘗試解析JSON響應
            entities = json.loads(response)
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    def _is_info_complete(self, entities: Dict[str, Any]) -> bool:
        """檢查信息是否完整"""
        
        required_fields = [field for field, config in self.core_info_fields.items() 
                          if config["required"]]
        
        return all(entities.get(field) for field in required_fields)
    
    async def _generate_next_question(self, context: ConversationContext) -> str:
        """生成下一個問題"""
        
        missing_fields = []
        for field, config in self.core_info_fields.items():
            if config["required"] and not context.extracted_entities.get(field):
                missing_fields.append(config["description"])
        
        if not missing_fields:
            return "還有其他信息需要補充嗎？"
        
        # 使用LLM生成自然的問題
        prompt = f"""
你是一個友善的旅遊助手。用戶已經提供了以下信息：
{json.dumps(context.extracted_entities, ensure_ascii=False, indent=2)}

還需要收集的信息：{', '.join(missing_fields)}

請生成一個自然、友善的問題來收集缺失的信息。問題應該：
1. 語氣友善親切
2. 針對最重要的缺失信息
3. 提供一些選項或例子
4. 簡潔明了

請只返回問題內容，不要其他文字。
"""
        
        try:
            return self.llm_client.generate_text(prompt)
        except Exception as e:
            logger.error(f"Error generating next question: {e}")
            return f"請告訴我{missing_fields[0]}？"
    
    async def _generate_itinerary(self, context: ConversationContext) -> Dict[str, Any]:
        """生成行程 - 整合 RAG 搜尋"""
        
        try:
            # 1. 使用 RAG 搜尋相關景點
            places = await self._rag_search_places(context)
            
            # 2. 使用 RAG 搜尋住宿
            accommodations = await self._rag_search_accommodations(context)
            
            # 3. 構建行程規劃請求（包含 RAG 搜尋結果）
            planning_request = self._build_planning_request_with_rag(
                context.extracted_entities, places, accommodations
            )
            
            # 4. 使用現有的行程規劃API
            import requests
            response = requests.post(
                'http://localhost:8002/v1/itinerary/propose',
                json={
                    'session_id': f'unified_{context.session_id}',
                    'text': planning_request
                }
            )
            
            if response.status_code == 200:
                itinerary_data = response.json()
                
                # 5. 生成推薦解釋
                explanation = await self._generate_recommendation_explanation(
                    context, places, accommodations
                )
                
                return {
                    "message": f"太棒了！我已經為您規劃好了行程。{explanation}您可以查看詳細安排，也可以繼續對話來調整行程。",
                    "intent": "itinerary_generated",
                    "itinerary": itinerary_data,
                    "collected_info": context.extracted_entities,
                    "is_complete": True,
                    "rag_results": {
                        "places": [{"name": p.name, "reason": getattr(p, 'recommendation_reason', '')} for p in places[:5]],
                        "accommodations": [{"name": a.name, "reason": getattr(a, 'recommendation_reason', '')} for a in accommodations[:3]]
                    },
                    "suggestions": [
                        "查看行程詳情",
                        "調整某個景點",
                        "修改時間安排",
                        "添加更多景點",
                        "了解推薦理由"
                    ]
                }
            else:
                return {
                    "message": "抱歉，生成行程時遇到了一些問題。請稍後再試，或者提供更多信息。",
                    "intent": "error",
                    "collected_info": context.extracted_entities,
                    "is_complete": False
                }
                
        except Exception as e:
            logger.error(f"Error generating itinerary: {e}")
            return {
                "message": "抱歉，生成行程時遇到了技術問題。請稍後再試。",
                "intent": "error",
                "collected_info": context.extracted_entities,
                "is_complete": False
            }
    
    def _build_planning_request(self, entities: Dict[str, Any]) -> str:
        """構建行程規劃請求文字"""
        
        destination = entities.get("destination", "某個地方")
        duration = entities.get("duration", "幾天")
        interests = entities.get("interests", [])
        
        if isinstance(interests, list):
            interests_text = "、".join(interests)
        else:
            interests_text = str(interests)
        
        return f"我想要在{destination}進行{duration}天的旅遊，興趣包括{interests_text}。"
    
    def _generate_suggestions(self, context: ConversationContext) -> List[str]:
        """生成智能建議"""
        
        suggestions = []
        entities = context.extracted_entities
        
        if not entities.get("destination"):
            suggestions.append("告訴我您想去哪裡旅遊")
        elif not entities.get("duration"):
            suggestions.append("告訴我您計劃旅遊幾天")
        elif not entities.get("interests"):
            suggestions.append("告訴我您的興趣偏好")
        else:
            suggestions.extend([
                "我想調整行程",
                "推薦附近景點",
                "修改預算安排",
                "查看詳細行程"
            ])
        
        return suggestions[:4]  # 最多返回4個建議
    
    async def _answer_question(self, question: str, context: ConversationContext) -> str:
        """回答用戶問題"""
        
        # 構建回答問題的提示詞
        context_info = json.dumps(context.extracted_entities, ensure_ascii=False, indent=2)
        
        prompt = f"""
你是一個專業的旅遊助手，擁有豐富的旅遊知識。

當前對話上下文：
{context_info}

用戶問題：{question}

請提供專業、準確、有用的回答。回答應該：
1. 直接回答問題
2. 提供實用的建議
3. 語氣友善專業
4. 適當提及相關的旅遊信息

請只返回回答內容，不要其他文字。
"""
        
        try:
            return self.llm_client.generate_text(prompt)
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "抱歉，我暫時無法回答這個問題。請嘗試換一種方式提問。"
    
    async def _parse_modifications(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """解析修改請求"""
        
        prompt = f"""
你是一個專業的旅遊信息解析助手。用戶想要修改旅遊計劃。

當前信息：
{json.dumps(context.extracted_entities, ensure_ascii=False, indent=2)}

用戶修改請求：{message}

請解析用戶想要修改的具體信息，並以JSON格式返回修改後的字段：
- destination: 目的地
- duration: 天數
- interests: 興趣列表
- budget: 預算
- travel_style: 旅遊風格
- group_size: 人數
- start_date: 出發日期

只返回實際修改的字段，格式：{{"field_name": "new_value"}}
"""
        
        try:
            response = self.llm_client.generate_text(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parsing modifications: {e}")
            return {}
    
    async def _generate_alternatives(self, message: str, context: ConversationContext) -> List[str]:
        """生成替代建議"""
        
        # 根據拒絕的內容生成替代方案
        alternatives = []
        
        if "預算" in message or "價格" in message:
            alternatives.extend(["調整預算範圍", "尋找經濟選項", "推薦免費景點"])
        
        if "景點" in message or "地方" in message:
            alternatives.extend(["推薦其他景點", "改變興趣偏好", "調整行程路線"])
        
        if "時間" in message or "天數" in message:
            alternatives.extend(["調整旅遊天數", "修改出發時間", "優化時間安排"])
        
        # 默認建議
        if not alternatives:
            alternatives.extend([
                "提供其他選項",
                "重新規劃行程",
                "調整旅遊偏好"
            ])
        
        return alternatives[:3]
    
    async def _rag_search_places(self, context: ConversationContext) -> List[Any]:
        """使用 RAG 搜尋相關景點 - 動態檢索策略"""
        
        try:
            entities = context.extracted_entities
            
            # 1. 動態調整搜尋策略
            search_strategy = self._determine_search_strategy(context)
            
            # 2. 根據策略調整搜尋參數
            search_params = self._adjust_search_parameters(entities, search_strategy, context)
            
            # 3. 執行搜尋
            places = await self._execute_dynamic_search(search_params, context)
            
            # 4. 記錄搜尋結果到上下文
            self._update_search_context(context, search_strategy, places)
            
            return places
            
        except Exception as e:
            logger.error(f"Error in RAG search places: {e}")
            return []
    
    def _determine_search_strategy(self, context: ConversationContext) -> Dict[str, Any]:
        """根據對話上下文確定搜尋策略"""
        
        entities = context.extracted_entities
        conversation_turn = len(context.conversation_history)
        previous_searches = context.previous_searches
        
        strategy = {
            "method": "hybrid",  # hybrid, structured, semantic
            "weight_structured": 0.6,
            "weight_semantic": 0.4,
            "diversity_boost": 0.1,
            "radius": 50000,  # 50公里
            "min_rating": 3.0,
            "max_results": 20
        }
        
        # 根據對話輪數調整策略
        if conversation_turn <= 2:
            # 初期：更重視語義搜尋，探索性更強
            strategy["weight_semantic"] = 0.7
            strategy["weight_structured"] = 0.3
            strategy["diversity_boost"] = 0.2
        elif conversation_turn <= 5:
            # 中期：平衡搜尋
            strategy["weight_structured"] = 0.5
            strategy["weight_semantic"] = 0.5
        else:
            # 後期：更重視結構化搜尋，精確性更強
            strategy["weight_structured"] = 0.7
            strategy["weight_semantic"] = 0.3
            strategy["diversity_boost"] = 0.0
        
        # 根據用戶偏好調整
        if entities.get("travel_style") == "緊湊":
            strategy["radius"] = 30000  # 縮小搜尋範圍
            strategy["min_rating"] = 4.0  # 提高評分要求
        elif entities.get("travel_style") == "悠閒":
            strategy["radius"] = 80000  # 擴大搜尋範圍
            strategy["diversity_boost"] = 0.3  # 增加多樣性
        
        # 根據之前的搜尋結果調整
        if previous_searches:
            last_search = previous_searches[-1]
            if last_search.get("result_count", 0) < 5:
                # 如果上次搜尋結果太少，增加語義搜尋權重
                strategy["weight_semantic"] = min(0.8, strategy["weight_semantic"] + 0.2)
                strategy["radius"] = min(100000, strategy["radius"] + 20000)
        
        return strategy
    
    def _adjust_search_parameters(self, entities: Dict[str, Any], strategy: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
        """根據策略調整搜尋參數"""
        
        params = {
            "destination": entities.get("destination", ""),
            "interests": entities.get("interests", []),
            "budget": entities.get("budget", ""),
            "travel_style": entities.get("travel_style", ""),
            "radius": strategy["radius"],
            "min_rating": strategy["min_rating"],
            "max_results": strategy["max_results"],
            "search_method": strategy["method"]
        }
        
        # 根據預算調整搜尋範圍
        budget = entities.get("budget", "")
        if budget == "經濟":
            params["min_rating"] = max(3.0, params["min_rating"] - 0.5)
        elif budget == "豪華":
            params["min_rating"] = max(4.0, params["min_rating"] + 0.5)
        
        # 根據興趣多樣性調整
        interests = entities.get("interests", [])
        if len(interests) > 3:
            # 興趣多樣，增加結果數量
            params["max_results"] = min(30, params["max_results"] + 10)
        
        return params
    
    async def _execute_dynamic_search(self, search_params: Dict[str, Any], context: ConversationContext) -> List[Any]:
        """執行動態搜尋"""
        
        if not search_params.get("destination") and not search_params.get("interests"):
            return []
        
        # 創建資料庫會話
        db = SessionLocal()
        try:
            place_repo = PostgresPlaceRepository(db)
            
            structured_results = []
            semantic_results = []
            
            # 執行結構化搜尋
            if search_params.get("interests"):
                structured_results = place_repo.search(
                    categories=search_params["interests"],
                    radius=search_params["radius"],
                    min_rating=search_params["min_rating"]
                )
            
            # 執行語義搜尋
            search_query = self._build_search_query(search_params)
            if search_query:
                query_embedding = embedding_client.get_embedding(search_query)
                semantic_results = place_repo.search_by_vector(query_embedding)
            
            # 根據策略權重融合結果
            strategy = self._determine_search_strategy(context)
            all_places = self._weighted_merge_search_results(
                structured_results, 
                semantic_results, 
                strategy["weight_structured"],
                strategy["weight_semantic"]
            )
            
            # 應用多樣性增強
            if strategy["diversity_boost"] > 0:
                all_places = self._apply_diversity_boost(all_places, strategy["diversity_boost"])
            
            # 為每個景點添加推薦理由
            for place in all_places:
                place.recommendation_reason = await self._generate_place_recommendation_reason(
                    place, search_params
                )
            
            return all_places[:search_params["max_results"]]
            
        finally:
            db.close()
    
    def _weighted_merge_search_results(self, structured_results: List[Any], semantic_results: List[Any], 
                                     weight_structured: float, weight_semantic: float) -> List[Any]:
        """根據權重合併搜尋結果"""
        
        all_results = {}
        
        # 添加結構化結果（帶權重）
        for i, result in enumerate(structured_results):
            score = weight_structured * (1.0 - i * 0.05)  # 排名越前分數越高
            all_results[str(result.id)] = (result, score)
        
        # 添加語義結果（帶權重）
        for i, result in enumerate(semantic_results):
            score = weight_semantic * (1.0 - i * 0.05)  # 排名越前分數越高
            result_id = str(result.id)
            if result_id in all_results:
                # 如果已存在，取較高分數
                existing_result, existing_score = all_results[result_id]
                all_results[result_id] = (existing_result, max(existing_score, score))
            else:
                all_results[result_id] = (result, score)
        
        # 按分數排序
        sorted_results = sorted(all_results.values(), key=lambda x: x[1], reverse=True)
        return [result for result, score in sorted_results]
    
    def _apply_diversity_boost(self, places: List[Any], diversity_boost: float) -> List[Any]:
        """應用多樣性增強"""
        
        if len(places) <= 5:
            return places
        
        # 簡單的多樣性策略：確保不同類別的景點都有代表
        categorized_places = {}
        for place in places:
            categories = getattr(place, 'categories', [])
            if categories:
                category = categories[0]  # 取第一個分類
                if category not in categorized_places:
                    categorized_places[category] = []
                categorized_places[category].append(place)
        
        # 從每個類別中選取代表性景點
        diverse_places = []
        for category, category_places in categorized_places.items():
            # 每個類別至少選一個，最多選兩個
            max_per_category = max(1, int(len(category_places) * diversity_boost))
            diverse_places.extend(category_places[:max_per_category])
        
        return diverse_places
    
    def _update_search_context(self, context: ConversationContext, strategy: Dict[str, Any], results: List[Any]):
        """更新搜尋上下文"""
        
        search_record = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "result_count": len(results),
            "entities": context.extracted_entities.copy()
        }
        
        context.previous_searches.append(search_record)
        
        # 只保留最近5次搜尋記錄
        if len(context.previous_searches) > 5:
            context.previous_searches = context.previous_searches[-5:]
        
        # 更新搜尋上下文
        context.search_context = {
            "last_search_strategy": strategy,
            "last_result_count": len(results),
            "search_frequency": len(context.previous_searches)
        }
    
    async def _rag_search_accommodations(self, context: ConversationContext) -> List[Any]:
        """使用 RAG 搜尋相關住宿"""
        
        try:
            entities = context.extracted_entities
            destination = entities.get("destination", "")
            budget = entities.get("budget", "")
            travel_style = entities.get("travel_style", "")
            
            if not destination:
                return []
            
            # 構建搜尋查詢
            search_query = self._build_accommodation_search_query(entities)
            
            # 創建資料庫會話
            db = SessionLocal()
            try:
                acc_repo = PostgresAccommodationRepository(db)
                
                # 結構化搜尋
                structured_results = acc_repo.search(
                    accommodation_type=None,  # 可以根據需求調整
                    min_rating=3.0
                )
                
                # 語義搜尋
                semantic_results = []
                if search_query:
                    query_embedding = embedding_client.get_embedding(search_query)
                    semantic_results = acc_repo.search_by_vector(query_embedding)
                
                # 融合結果
                all_accommodations = self._merge_search_results(structured_results, semantic_results)
                
                # 為每個住宿添加推薦理由
                for acc in all_accommodations:
                    acc.recommendation_reason = await self._generate_accommodation_recommendation_reason(
                        acc, entities
                    )
                
                return all_accommodations[:10]  # 返回前10個結果
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in RAG search accommodations: {e}")
            return []
    
    def _build_search_query(self, entities: Dict[str, Any]) -> str:
        """構建搜尋查詢文字"""
        
        query_parts = []
        
        destination = entities.get("destination", "")
        if destination:
            query_parts.append(f"在{destination}")
        
        interests = entities.get("interests", [])
        if interests:
            if isinstance(interests, list):
                interests_text = "、".join(interests)
            else:
                interests_text = str(interests)
            query_parts.append(f"喜歡{interests_text}")
        
        travel_style = entities.get("travel_style", "")
        if travel_style:
            query_parts.append(f"{travel_style}風格")
        
        return " ".join(query_parts)
    
    def _build_accommodation_search_query(self, entities: Dict[str, Any]) -> str:
        """構建住宿搜尋查詢文字"""
        
        query_parts = []
        
        destination = entities.get("destination", "")
        if destination:
            query_parts.append(f"{destination}住宿")
        
        budget = entities.get("budget", "")
        if budget:
            query_parts.append(f"{budget}預算")
        
        travel_style = entities.get("travel_style", "")
        if travel_style:
            query_parts.append(f"{travel_style}風格住宿")
        
        return " ".join(query_parts)
    
    def _merge_search_results(self, structured_results: List[Any], semantic_results: List[Any]) -> List[Any]:
        """融合結構化和語義搜尋結果"""
        
        # 簡單的融合策略：去重並合併
        all_results = {}
        
        # 添加結構化結果
        for result in structured_results:
            all_results[str(result.id)] = result
        
        # 添加語義結果（如果不存在）
        for result in semantic_results:
            if str(result.id) not in all_results:
                all_results[str(result.id)] = result
        
        return list(all_results.values())
    
    async def _generate_place_recommendation_reason(self, place: Any, entities: Dict[str, Any]) -> str:
        """生成景點推薦理由"""
        
        try:
            interests = entities.get("interests", [])
            travel_style = entities.get("travel_style", "")
            
            # 構建推薦理由提示詞
            prompt = f"""
根據以下信息生成景點推薦理由：

景點名稱：{place.name}
景點分類：{getattr(place, 'categories', [])}
用戶興趣：{interests}
旅遊風格：{travel_style}

請生成一個簡短的推薦理由（1-2句話），說明為什麼推薦這個景點給用戶。
"""
            
            reason = self.llm_client.generate_text(prompt)
            return reason.strip()
            
        except Exception as e:
            logger.error(f"Error generating place recommendation reason: {e}")
            return "根據您的興趣推薦"
    
    async def _generate_accommodation_recommendation_reason(self, accommodation: Any, entities: Dict[str, Any]) -> str:
        """生成住宿推薦理由"""
        
        try:
            budget = entities.get("budget", "")
            travel_style = entities.get("travel_style", "")
            
            # 構建推薦理由提示詞
            prompt = f"""
根據以下信息生成住宿推薦理由：

住宿名稱：{accommodation.name}
住宿類型：{getattr(accommodation, 'accommodation_type', '')}
評分：{getattr(accommodation, 'rating', '')}
用戶預算：{budget}
旅遊風格：{travel_style}

請生成一個簡短的推薦理由（1-2句話），說明為什麼推薦這個住宿給用戶。
"""
            
            reason = self.llm_client.generate_text(prompt)
            return reason.strip()
            
        except Exception as e:
            logger.error(f"Error generating accommodation recommendation reason: {e}")
            return "根據您的需求推薦"
    
    async def _generate_recommendation_explanation(self, context: ConversationContext, places: List[Any], accommodations: List[Any]) -> str:
        """生成整體推薦解釋"""
        
        try:
            entities = context.extracted_entities
            destination = entities.get("destination", "")
            interests = entities.get("interests", [])
            
            if not places:
                return ""
            
            # 構建解釋提示詞
            prompt = f"""
根據以下信息生成行程推薦解釋：

目的地：{destination}
用戶興趣：{interests}
找到的景點數量：{len(places)}
找到的住宿數量：{len(accommodations)}

請生成一個簡短的解釋（2-3句話），說明我根據您的偏好找到了哪些類型的景點和住宿。
"""
            
            explanation = self.llm_client.generate_text(prompt)
            return explanation.strip() + " "
            
        except Exception as e:
            logger.error(f"Error generating recommendation explanation: {e}")
            return ""
    
    async def _generate_detailed_explanation(self, item_name: str, item_type: str, context: ConversationContext) -> str:
        """生成詳細的推薦解釋"""
        
        try:
            entities = context.extracted_entities
            
            # 構建詳細解釋提示詞
            prompt = f"""
根據以下信息為用戶生成詳細的推薦解釋：

{item_type}名稱：{item_name}
用戶目的地：{entities.get('destination', '')}
用戶興趣：{entities.get('interests', [])}
旅遊風格：{entities.get('travel_style', '')}
預算：{entities.get('budget', '')}
旅遊天數：{entities.get('duration', '')}

請生成一個詳細的解釋（3-4句話），包括：
1. 為什麼推薦這個{item_type}
2. 它如何符合用戶的偏好
3. 具體的優勢或特色
4. 與用戶需求的匹配度

語氣要友善、專業且具說服力。
"""
            
            explanation = self.llm_client.generate_text(prompt)
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Error generating detailed explanation: {e}")
            return f"這個{item_name}很適合您的旅遊需求，根據您的偏好精心推薦。"
    
    def _build_planning_request_with_rag(self, entities: Dict[str, Any], places: List[Any], accommodations: List[Any]) -> str:
        """構建包含 RAG 結果的行程規劃請求"""
        
        base_request = self._build_planning_request(entities)
        
        # 添加 RAG 搜尋結果
        if places:
            place_names = [place.name for place in places[:5]]
            base_request += f" 我已經為您找到了這些相關景點：{', '.join(place_names)}。"
        
        if accommodations:
            acc_names = [acc.name for acc in accommodations[:3]]
            base_request += f" 推薦住宿：{', '.join(acc_names)}。"
        
        return base_request
    
    def _generate_contextual_response(self, context: ConversationContext) -> str:
        """根據已有信息生成上下文相關的回應"""
        
        entities = context.extracted_entities
        destination = entities.get("destination")
        duration = entities.get("duration")
        interests = entities.get("interests", [])
        
        # 根據已有信息生成智能回應
        if destination and duration:
            if isinstance(interests, list) and interests:
                interests_text = "、".join(interests)
                return f"太好了！您想去{destination}進行{duration}天的旅遊，興趣包括{interests_text}。還有什麼其他需求嗎？比如預算範圍、旅遊風格或人數？"
            else:
                return f"很好！您想去{destination}進行{duration}天的旅遊。請告訴我您的興趣偏好，比如美食、文化、自然風景等？"
        elif destination:
            return f"知道了！您想去{destination}旅遊。請告訴我您計劃去幾天？"
        elif duration:
            return f"了解！您計劃{duration}天的旅遊。請告訴我您想去哪裡？"
        else:
            return "請告訴我更多關於您旅遊計劃的信息，比如目的地、天數或興趣偏好？"
    
    async def _save_context(self, context: ConversationContext):
        """保存對話上下文"""
        
        try:
            context_data = {
                "current_intent": context.current_intent.value if context.current_intent else None,
                "extracted_entities": context.extracted_entities,
                "user_preferences": context.user_preferences,
                "conversation_history": context.conversation_history,
                "confidence_score": context.confidence_score,
                "last_activity": context.last_activity.isoformat()
            }
            
            # 保存到Redis，設置24小時過期
            self.redis_client.setex(
                f"conversation_context:{context.session_id}",
                86400,  # 24小時
                json.dumps(context_data, ensure_ascii=False)
            )
            
        except Exception as e:
            logger.error(f"Error saving context: {e}")
    
    def _format_response(self, response: Dict[str, Any], context: ConversationContext) -> Dict[str, Any]:
        """格式化統一回應"""
        
        return {
            "session_id": context.session_id,
            "message": response.get("message", ""),
            "intent": response.get("intent", "unknown"),
            "suggestions": response.get("suggestions", []),
            "collected_info": response.get("collected_info", {}),
            "is_complete": response.get("is_complete", False),
            "itinerary": response.get("itinerary"),
            "confidence_score": context.confidence_score,
            "turn_count": len(context.conversation_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """創建錯誤回應"""
        
        return {
            "message": "抱歉，處理您的請求時遇到了一些問題。請稍後再試。",
            "intent": "error",
            "suggestions": ["重新開始對話", "聯繫客服"],
            "collected_info": {},
            "is_complete": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_conversation_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """獲取對話狀態"""
        
        context = await self._get_or_create_context(session_id)
        
        return {
            "session_id": session_id,
            "current_intent": context.current_intent.value if context.current_intent else None,
            "collected_info": context.extracted_entities,
            "conversation_history": context.conversation_history,
            "confidence_score": context.confidence_score,
            "last_activity": context.last_activity.isoformat(),
            "turn_count": len(context.conversation_history)
        }
    
    async def reset_conversation(self, session_id: str) -> bool:
        """重置對話狀態"""
        
        try:
            # 刪除Redis中的上下文
            self.redis_client.delete(f"conversation_context:{session_id}")
            return True
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")
            return False
