"""
統一對話引擎 - 簡化版本
只保留基本的 AI 對話功能，移除複雜的 RAG 搜尋
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """對話上下文"""
    session_id: str
    current_intent: Optional[str] = None
    extracted_entities: Dict[str, Any] = None
    conversation_history: List[Dict[str, str]] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.extracted_entities is None:
            self.extracted_entities = {}
        if self.conversation_history is None:
            self.conversation_history = []

class UnifiedConversationEngine:
    """統一對話引擎 - 簡化版本"""
    
    def __init__(self, db=None):
        """初始化引擎"""
        self.db = db
        self.llm_client = self._init_llm_client()
        logger.info("✅ 統一對話引擎初始化完成（簡化版本）")
    
    def _init_llm_client(self):
        """初始化 LLM 客戶端"""
        try:
            from ..llm_client import LLMClient
            return LLMClient()
        except Exception as e:
            logger.error(f"LLM 客戶端初始化失敗: {e}")
            return None
    
    async def process_message(self, session_id: str, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """處理用戶消息 - 簡化版本"""
        try:
            logger.info(f"Processing message for session {session_id}: {user_message[:50]}...")
            
            # 1. 檢測意圖
            intent = await self._detect_intent_simple(user_message)
            logger.info(f"Detected intent: {intent}")
            
            # 2. 根據意圖處理
            if intent == "greeting":
                return await self._handle_greeting_simple(session_id, user_message)
            elif intent == "provide_info":
                return await self._handle_info_simple(session_id, user_message)
            else:
                return await self._handle_general_simple(session_id, user_message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "message": "抱歉，我遇到了一些技術問題。請稍後再試。",
                "intent": "error",
                "suggestions": ["重新開始對話", "嘗試其他問題"],
                "collected_info": {},
                "is_complete": False
            }
    
    async def _detect_intent_simple(self, message: str) -> str:
        """簡單的意圖檢測"""
        message_lower = message.lower()
        
        # 問候語
        if any(word in message_lower for word in ["你好", "hi", "hello", "嗨"]):
            return "greeting"
        
        # 提供信息（包含旅遊相關關鍵字）
        if any(word in message_lower for word in ["旅遊", "旅行", "去", "台北", "台中", "高雄", "台南", "花蓮", "台東", "宜蘭"]):
            return "provide_info"
        
        return "general"
    
    async def _handle_greeting_simple(self, session_id: str, message: str) -> Dict[str, Any]:
        """處理問候語"""
        welcome_message = """
🎉 您好！我是您的 AI 旅遊助手！

我可以幫您規劃台灣各地的精彩行程，包括：
- 🏛️ 景點推薦
- 🍜 美食指南  
- 🏨 住宿建議
- 🚌 交通規劃

請告訴我您想去哪裡旅遊？比如：
- "我想去台北旅遊3天"
- "我想去花蓮看海"
- "我想去台中吃美食"
"""
        
        return {
            "message": welcome_message,
            "intent": "greeting",
            "suggestions": [
                "我想去台北旅遊",
                "我想去花蓮看海",
                "我想去台中吃美食",
                "我想去高雄看夜景"
            ],
            "collected_info": {},
            "is_complete": False,
            "session_id": session_id,
            "confidence_score": 0.8,
            "turn_count": 1,
            "timestamp": "2025-01-01T00:00:00"
        }
    
    async def _handle_info_simple(self, session_id: str, message: str) -> Dict[str, Any]:
        """處理旅遊信息"""
        # 簡單的實體提取
        entities = self._extract_entities_simple(message)
        
        destination = entities.get("destination", "台灣")
        duration = entities.get("duration", 3)
        interests = entities.get("interests", ["觀光"])
        
        interests_text = "、".join(interests) if interests else "一般觀光"
        
        # 生成簡單的行程建議
        response_message = f"""
🎉 太棒了！我已經為您規劃好了{destination}的{duration}天行程！

📋 行程概要：
- 目的地：{destination}
- 天數：{duration}天
- 興趣：{interests_text}

🏛️ 推薦景點：
- {destination}101觀景台
- 故宮博物院
- 中正紀念堂
- 西門町商圈

🍜 美食推薦：
- 士林夜市
- 饒河夜市
- 永康街美食
- 鼎泰豐小籠包

🏨 住宿建議：
- 信義區商務飯店
- 西門町青年旅館
- {destination}車站附近酒店

您可以繼續與我對話來調整行程細節！
"""
        
        return {
            "message": response_message,
                    "intent": "itinerary_generated",
                    "suggestions": [
                        "查看行程詳情",
                        "調整某個景點",
                        "修改時間安排",
                "添加更多景點"
            ],
            "collected_info": entities,
            "is_complete": True,
            "itinerary": {
                "destination": destination,
                "duration": duration,
                "interests": interests,
                "status": "generated"
            },
            "session_id": session_id,
            "confidence_score": 0.9,
            "turn_count": 1,
            "timestamp": "2025-01-01T00:00:00"
        }
    
    async def _handle_general_simple(self, session_id: str, message: str) -> Dict[str, Any]:
        """處理一般對話"""
        return {
            "message": "我主要專精於台灣旅遊規劃。請告訴我您想去哪裡旅遊，我可以為您推薦景點、美食和住宿！",
            "intent": "general",
            "suggestions": [
                "我想去台北旅遊",
                "我想去花蓮看海",
                "我想去台中吃美食",
                "我想去高雄看夜景"
            ],
            "collected_info": {},
            "is_complete": False,
            "session_id": session_id,
            "confidence_score": 0.7,
            "turn_count": 1,
            "timestamp": "2025-01-01T00:00:00"
        }
    
    def _extract_entities_simple(self, message: str) -> Dict[str, Any]:
        """簡單的實體提取"""
        entities = {}
        message_lower = message.lower()
        
        # 台灣城市匹配
        taiwan_cities = {
            "台北": ["台北", "taipei", "台北市"],
            "台中": ["台中", "taichung", "台中市"],
            "高雄": ["高雄", "kaohsiung", "高雄市"],
            "台南": ["台南", "tainan", "台南市"],
            "花蓮": ["花蓮", "hualien", "花蓮縣"],
            "台東": ["台東", "taitung", "台東縣"],
            "宜蘭": ["宜蘭", "yilan", "宜蘭縣"],
            "新竹": ["新竹", "hsinchu", "新竹市", "新竹縣"],
            "嘉義": ["嘉義", "chiayi", "嘉義市", "嘉義縣"],
            "南投": ["南投", "nantou", "南投縣"]
        }
        
        for city, keywords in taiwan_cities.items():
            if any(keyword in message for keyword in keywords):
                entities["destination"] = city
                break
        
        # 天數匹配
        import re
        duration_match = re.search(r'(\d+)\s*天', message)
        if duration_match:
            entities["duration"] = int(duration_match.group(1))
        
        # 興趣匹配
        interests = []
        if any(word in message_lower for word in ["美食", "吃", "夜市", "小吃"]):
            interests.append("美食")
        if any(word in message_lower for word in ["文化", "歷史", "古蹟", "博物館"]):
            interests.append("文化")
        if any(word in message_lower for word in ["自然", "山", "海", "風景"]):
            interests.append("自然")
        if any(word in message_lower for word in ["購物", "買", "商圈"]):
            interests.append("購物")
        
        if interests:
            entities["interests"] = interests
        
        return entities
    
    async def get_conversation_state(self, session_id: str) -> Dict[str, Any]:
        """獲取對話狀態 - 簡化版本"""
        return {
            "session_id": session_id,
            "current_intent": None,
            "collected_info": {},
            "conversation_history": [],
            "confidence_score": 0.0,
            "timestamp": "2025-01-01T00:00:00"
        }
    
    async def get_suggestions(self, session_id: str) -> Dict[str, Any]:
        """獲取建議 - 簡化版本"""
        return {
            "session_id": session_id,
            "suggestions": [
                "我想去台北旅遊",
                "我想去花蓮看海", 
                "我想去台中吃美食",
                "我想去高雄看夜景"
            ],
            "context": None,
            "timestamp": "2025-01-01T00:00:00"
        }
    
    async def reset_conversation(self, session_id: str) -> Dict[str, Any]:
        """重置對話 - 簡化版本"""
        return {
            "session_id": session_id,
            "message": "對話已重置，請重新開始！",
            "status": "reset"
        }