from typing import Dict, List, Optional, Any
import logging
import json
import redis
from sqlalchemy.orm import Session

from ...domain.entities.conversation_state import ConversationState, ConversationStateType
from ...infrastructure.clients.gemini_llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)

class ConversationService:
    """對話式行程規劃服務"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.llm_client = GeminiLLMClient()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # 定義需要收集的資訊
        self.required_info = {
            "destination": "目的地",
            "duration": "旅遊天數", 
            "interests": "興趣類型",
            "budget": "預算範圍",
            "travel_style": "旅遊風格",
            "group_size": "人數"
        }
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """處理用戶訊息並返回回應"""
        
        # 獲取或創建對話狀態
        state = await self.get_conversation_state(session_id)
        if not state:
            state = ConversationState(session_id, ConversationStateType.COLLECTING_INFO)
        
        # 添加用戶訊息到歷史
        state.add_message("user", user_message)
        
        # 分析用戶訊息並更新收集的資訊
        await self._analyze_user_message(state, user_message)
        
        # 檢查是否收集足夠資訊
        if self._is_info_complete(state):
            # 生成行程
            return await self._generate_itinerary(state)
        else:
            # 繼續收集資訊
            return await self._ask_next_question(state)
    
    async def get_conversation_state(self, session_id: str) -> Optional[ConversationState]:
        """獲取對話狀態"""
        try:
            state_data = self.redis_client.get(f"conversation:{session_id}")
            if state_data:
                return ConversationState.from_dict(json.loads(state_data))
            return None
        except Exception as e:
            logger.error(f"Error getting conversation state: {e}")
            return None
    
    async def reset_conversation(self, session_id: str):
        """重置對話狀態"""
        try:
            self.redis_client.delete(f"conversation:{session_id}")
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")
    
    def _save_conversation_state(self, state: ConversationState):
        """保存對話狀態"""
        try:
            self.redis_client.setex(
                f"conversation:{state.session_id}", 
                3600,  # 1小時過期
                json.dumps(state.to_dict())
            )
        except Exception as e:
            logger.error(f"Error saving conversation state: {e}")
    
    async def _analyze_user_message(self, state: ConversationState, message: str):
        """分析用戶訊息並提取資訊"""
        
        # 使用 LLM 分析用戶訊息
        analysis_prompt = f"""
        分析用戶的訊息，提取旅遊規劃相關資訊。
        
        用戶訊息: {message}
        
        請從以下類別中識別並提取資訊：
        - destination: 目的地 (如: 宜蘭、台北、花蓮)
        - duration: 旅遊天數 (如: 1天、2天1夜、3天2夜)
        - interests: 興趣類型 (如: 美食、風景、文化、購物)
        - budget: 預算範圍 (如: 低、中、高)
        - travel_style: 旅遊風格 (如: 輕鬆、緊湊、深度)
        - group_size: 人數 (如: 1人、2人、家庭)
        
        請以 JSON 格式回應，只包含識別到的資訊：
        {{"destination": "宜蘭", "duration": "2天1夜", "interests": ["美食", "風景"]}}
        """
        
        try:
            analysis = await self.llm_client.generate_text(analysis_prompt)
            # 解析 JSON 回應
            extracted_info = json.loads(analysis)
            
            # 更新收集的資訊
            for key, value in extracted_info.items():
                if key in self.required_info:
                    state.add_info(key, value)
                    
        except Exception as e:
            logger.error(f"Error analyzing user message: {e}")
    
    def _is_info_complete(self, state: ConversationState) -> bool:
        """檢查是否收集足夠的資訊"""
        # 至少需要目的地和天數
        essential_keys = ["destination", "duration"]
        return all(key in state.collected_info for key in essential_keys)
    
    async def _ask_next_question(self, state: ConversationState) -> Dict[str, Any]:
        """生成下一個問題"""
        
        # 找出還需要收集的資訊
        missing_info = []
        for key, label in self.required_info.items():
            if key not in state.collected_info:
                missing_info.append(label)
        
        # 生成問題
        question_prompt = f"""
        基於已收集的資訊和對話歷史，生成一個自然的問題來收集更多旅遊規劃資訊。
        
        已收集的資訊: {json.dumps(state.collected_info, ensure_ascii=False)}
        還需要收集: {', '.join(missing_info)}
        對話歷史: {json.dumps(state.conversation_history[-3:], ensure_ascii=False)}  # 最近3條
        
        請生成一個友善、自然的問題，幫助收集旅遊規劃資訊。
        回應格式: 直接返回問題文字，不要其他內容。
        """
        
        try:
            question = await self.llm_client.generate_text(question_prompt)
            
            # 添加 AI 回應到歷史
            state.add_message("assistant", question)
            
            # 保存狀態
            self._save_conversation_state(state)
            
            return {
                "message": question,
                "conversation_state": state.state.value,
                "is_complete": False,
                "questions": missing_info
            }
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return {
                "message": "請告訴我您想去哪裡旅遊呢？",
                "conversation_state": state.state.value,
                "is_complete": False
            }
    
    async def _generate_itinerary(self, state: ConversationState) -> Dict[str, Any]:
        """生成最終行程"""
        
        try:
            # 設置狀態為生成行程中
            state.set_state(ConversationStateType.GENERATING_ITINERARY)
            
            # 構建行程規劃請求文字
            destination = state.collected_info.get("destination", "宜蘭")
            duration = state.collected_info.get("duration", "1天")
            interests = state.collected_info.get("interests", ["美食"])
            
            planning_text = f"我想要在{destination}進行{duration}的旅遊，包含{', '.join(interests)}"
            
            # 使用現有的行程規劃 API
            import requests
            response = requests.post('http://localhost:8002/v1/itinerary/propose', 
                                   json={'session_id': f'conv_{state.session_id}', 'text': planning_text})
            
            if response.status_code == 200:
                itinerary = response.json()
                
                # 生成完成訊息
                completion_message = f"""
                太好了！我已經為您規劃好了{destination}的行程！
                
                基於您的需求：
                - 旅遊天數：{duration}
                - 興趣類型：{', '.join(interests)}
                - 預算範圍：{state.collected_info.get('budget', '中等')}
                
                我為您精心安排了這個行程，希望您會喜歡！
                """
                
                # 添加完成訊息到歷史
                state.add_message("assistant", completion_message)
                
                # 設置為完成狀態
                state.set_state(ConversationStateType.COMPLETED)
                
                # 保存狀態
                self._save_conversation_state(state)
                
                return {
                    "message": completion_message,
                    "conversation_state": state.state.value,
                    "itinerary": itinerary,
                    "is_complete": True
                }
            else:
                raise Exception(f"Planning API failed: {response.status_code}")
            
        except Exception as e:
            logger.error(f"Error generating itinerary: {e}")
            state.set_state(ConversationStateType.ERROR)
            return {
                "message": "抱歉，生成行程時發生錯誤，請稍後再試。",
                "conversation_state": state.state.value,
                "is_complete": False
            }
    
    def _parse_duration(self, duration_str: str) -> int:
        """解析天數字串為數字"""
        if "1天" in duration_str or "一天" in duration_str:
            return 1
        elif "2天" in duration_str or "兩天" in duration_str:
            return 2
        elif "3天" in duration_str or "三天" in duration_str:
            return 3
        else:
            return 1  # 預設1天
