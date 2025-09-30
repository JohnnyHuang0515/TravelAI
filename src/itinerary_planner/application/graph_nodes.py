from .graph_state import AppState
from ..infrastructure.clients.llm_client import llm_client
from ..infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
from ..infrastructure.repositories.postgres_accommodation_repo import PostgresAccommodationRepository
from .services.planning_service import greedy_planner
from ..infrastructure.clients.osrm_client import osrm_client
from ..infrastructure.persistence.database import SessionLocal
from ..infrastructure.persistence.orm_models import Place

from ..infrastructure.clients.embedding_client import embedding_client
from .services.rerank_service import rerank_service
from .services.accommodation_recommendation_service import accommodation_recommendation_service

# 新增對話相關導入
from ..domain.entities.conversation_state import ConversationState, ConversationStateType
from ..infrastructure.clients.gemini_llm_client import GeminiLLMClient
from typing import Optional
import redis
import json

class GraphNodes:
    """包含 LangGraph 中所有節點邏輯的類別 - 支援對話式規劃"""
    
    def __init__(self):
        """初始化對話相關服務"""
        self.gemini_client = GeminiLLMClient()
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

    def conversation_memory_manager(self, state: AppState) -> AppState:
        """節點：對話記憶管理"""
        print("=" * 80)
        print("🔍 **NODE: conversation_memory_manager**")
        print("=" * 80)
        print(f"📊 輸入狀態: {state}")
        
        session_id = state.get("session_id", "")
        user_input = state.get("user_input", "")
        
        print(f"🆔 Session ID: {session_id}")
        print(f"💬 User Input: {user_input}")
        
        # 獲取或創建對話狀態
        conversation_state = self._get_conversation_state(session_id)
        if not conversation_state:
            conversation_state = ConversationState(session_id, ConversationStateType.COLLECTING_INFO)
            print("🆕 創建新的對話狀態")
        else:
            print(f"📋 獲取現有對話狀態，已進行 {conversation_state.turn_count} 輪對話")
        
        # 增加對話輪次
        conversation_state.increment_turn()
        
        # 添加用戶訊息到歷史
        conversation_state.add_message("user", user_input)
        print(f"📝 添加用戶訊息到歷史")
        
        # 更新上下文記憶
        conversation_state.add_context_memory(f"turn_{conversation_state.turn_count}_user", user_input)
        
        # 生成上下文摘要
        context_summary = conversation_state.get_context_summary()
        
        # 分析用戶訊息並更新收集的資訊
        print("🔍 開始分析用戶訊息...")
        self._analyze_user_message_with_memory(conversation_state, user_input)
        print(f"📊 分析後的資訊: {conversation_state.collected_info}")
        
        # 檢查是否收集足夠資訊
        is_complete = self._is_info_complete(conversation_state)
        print(f"✅ 資訊完整性檢查: {is_complete}")
        
        # 保存狀態
        self._save_conversation_state(conversation_state)
        print("💾 保存對話狀態")
        
        result = {
            **state,
            "conversation_state": conversation_state,
            "conversation_history": conversation_state.conversation_history,
            "collected_info": conversation_state.collected_info,
            "conversation_memory": conversation_state.conversation_memory,
            "context_summary": context_summary,
            "turn_count": conversation_state.turn_count,
            "is_info_complete": is_complete
        }
        
        print(f"📊 當前對話記憶: {conversation_state.conversation_memory}")
        print(f"📝 上下文摘要: {context_summary}")
        print(f"📤 輸出狀態: {result}")
        print("=" * 80)
        
        return result

    def info_collector(self, state: AppState) -> AppState:
        """節點：收集用戶資訊"""
        print("=" * 80)
        print("🔍 **NODE: info_collector**")
        print("=" * 80)
        print(f"📊 輸入狀態: {state}")
        
        conversation_state = state.get("conversation_state")
        if not conversation_state:
            print("❌ 沒有找到對話狀態")
            return {**state, "error": "Conversation state not found."}
        
        print(f"📋 對話狀態: {conversation_state.state.value}")
        print(f"📊 收集的資訊: {conversation_state.collected_info}")
        
        # 如果資訊完整，直接返回
        if state.get("is_info_complete", False):
            print("✅ 資訊已完整，跳過問題生成")
            return state
        
        print("❓ 資訊不完整，生成下一個問題...")
        
        # 生成下一個問題
        next_question = self._generate_next_question_with_memory(conversation_state)
        print(f"🤖 生成的問題: {next_question}")
        
        # 添加 AI 回應到歷史
        conversation_state.add_message("assistant", next_question)
        print("📝 添加 AI 回應到歷史")
        
        # 保存狀態
        self._save_conversation_state(conversation_state)
        print("💾 保存對話狀態")
        
        result = {
            **state,
            "ai_response": next_question,
            "next_question": next_question,
            "conversation_state": conversation_state
        }
        
        print(f"📤 輸出狀態: {result}")
        print("=" * 80)
        
        return result

    def extract_story(self, state: AppState) -> AppState:
        """節點：從收集的資訊提取 Story"""
        print("=" * 80)
        print("🔍 **NODE: extract_story**")
        print("=" * 80)
        print(f"📊 輸入狀態: {state}")
        
        # 檢查是否資訊完整
        if not state.get("is_info_complete", False):
            print("❌ 資訊不完整，無法提取 Story")
            return {**state, "error": "Information not complete yet."}
        
        collected_info = state.get("collected_info", {})
        print(f"📊 收集的資訊: {collected_info}")
        
        # 基於收集的資訊構建 Story
        destination = collected_info.get("destination", "宜蘭")
        duration = collected_info.get("duration", "1天")
        interests = collected_info.get("interests", ["美食"])
        
        # 構建規劃文字
        planning_text = f"我想要在{destination}進行{duration}的旅遊，包含{', '.join(interests)}"
        print(f"📝 構建的規劃文字: {planning_text}")
        
        # 使用原有的 LLM 提取 Story
        print("🤖 開始提取 Story...")
        story = llm_client.extract_story_from_text(planning_text)
        print(f"📊 Story 解析結果: days={story.days}, start={story.daily_window.start if story.daily_window else 'None'}, end={story.daily_window.end if story.daily_window else 'None'}")
        
        if story.days == 0:
            print("❌ Story 天數為 0，資訊不足")
            return {**state, "error": "Information insufficient."}
        
        result = {**state, "story": story}
        print(f"📤 輸出狀態: {result}")
        print("=" * 80)
        
        return result

    def retrieve_places_structured(self, state: AppState) -> AppState:
        """節點：結構化檢索地點"""
        print("--- Node: retrieve_places_structured ---")
        story = state.get("story")
        if not story:
            return {**state, "error": "Story not found."}

        db = SessionLocal()
        repo = PostgresPlaceRepository(db)
        structured_results = repo.search(categories=story.preference.themes)
        db.close()
        
        print(f"Found {len(structured_results)} candidates from structured search.")
        return {**state, "structured_candidates": structured_results}

    def retrieve_places_semantic(self, state: AppState) -> AppState:
        """節點：語義化檢索地點"""
        print("--- Node: retrieve_places_semantic ---")
        story = state.get("story")
        if not story:
            return {**state, "error": "Story not found."}

        # 將偏好主題合併為一個查詢字串
        query_text = " ".join(story.preference.themes)
        query_embedding = embedding_client.get_embedding(query_text)

        db = SessionLocal()
        repo = PostgresPlaceRepository(db)
        semantic_results = repo.search_by_vector(query_embedding)
        db.close()

        print(f"Found {len(semantic_results)} candidates from semantic search.")
        return {**state, "semantic_candidates": semantic_results}

    def rank_and_merge(self, state: AppState) -> AppState:
        """節點：融合並重排序候選地點"""
        print("--- Node: rank_and_merge ---")
        story = state.get("story")
        structured = state.get("structured_candidates", [])
        semantic = state.get("semantic_candidates", [])

        if not story:
            return {**state, "error": "Story not found."}

        final_candidates = rerank_service.rerank(structured, semantic, story)
        print(f"Reranked and merged into {len(final_candidates)} final candidates.")
        return {**state, "candidates": final_candidates}

    def retrieve_accommodations(self, state: AppState) -> AppState:
        """節點：檢索住宿"""
        print("--- Node: retrieve_accommodations ---")
        story = state.get("story")
        if not story:
            return {**state, "error": "Story not found."}

        db = SessionLocal()
        repo = PostgresAccommodationRepository(db)
        
        # 根據 Story 中的住宿偏好檢索
        accommodations = repo.search(
            accommodation_type=story.accommodation.type,
            budget_range=story.accommodation.budget_range,
            eco_friendly="環保" in getattr(story, 'special_requirements', ''),
            min_rating=4.0  # 最低4星評分
        )
        
        db.close()
        
        print(f"Found {len(accommodations)} accommodation candidates.")
        return {**state, "accommodation_candidates": accommodations}

    def plan_itinerary(self, state: AppState) -> AppState:
        """節點：規劃行程"""
        print("--- Node: plan_itinerary ---")
        story = state.get("story")
        candidates = state.get("candidates")
        accommodation_candidates = state.get("accommodation_candidates", [])

        if not story or not candidates:
            return {**state, "error": "Story or candidates not found."}

        # 提取所有地點的座標
        from sqlalchemy import func
        db = SessionLocal()
        try:
            # 獲取所有候選地點的座標，確保順序與 candidates 一致
            place_ids = [str(p.id) for p in candidates]
            
            # 建立 ID 到座標的映射
            results = db.query(
                Place.id,
                func.ST_Y(Place.geom).label('lat'),
                func.ST_X(Place.geom).label('lon')
            ).filter(Place.id.in_(place_ids)).all()
            
            # 建立 ID 到座標的映射
            coord_map = {str(r.id): (r.lon, r.lat) for r in results}
            
            # 按照 candidates 的順序建立 locations
            locations = [coord_map[str(p.id)] for p in candidates if str(p.id) in coord_map]
            
            # 調試：打印候選景點順序
            print(f"🔍 **調試候選景點順序**")
            for i, p in enumerate(candidates):
                print(f"  {i}: {p.name} (ID: {p.id})")
            print()
            
            # 調試：打印座標順序
            print(f"🔍 **調試座標順序**")
            for i, (lon, lat) in enumerate(locations):
                place_name = candidates[i].name if i < len(candidates) else 'Unknown'
                print(f"  {i}: {place_name} ({lon}, {lat})")
            print()
        finally:
            db.close()
        import asyncio
        travel_matrix = asyncio.run(osrm_client.get_travel_time_matrix(locations))

        if not travel_matrix:
            return {**state, "error": "Failed to get travel time matrix."}

        itinerary = greedy_planner.plan(story, candidates, travel_matrix)
        
        # 添加住宿推薦
        if accommodation_candidates:
            itinerary.days = accommodation_recommendation_service.recommend_accommodations_for_days(
                itinerary.days, accommodation_candidates, story
            )
        
        print("Planning complete.")
        
        return {**state, "itinerary": itinerary}

    # 對話相關的輔助方法
    def _get_conversation_state(self, session_id: str) -> Optional[ConversationState]:
        """獲取對話狀態"""
        try:
            state_data = self.redis_client.get(f"conversation:{session_id}")
            if state_data:
                return ConversationState.from_dict(json.loads(state_data))
            return None
        except Exception as e:
            print(f"Error getting conversation state: {e}")
            return None
    
    def _save_conversation_state(self, state: ConversationState):
        """保存對話狀態"""
        try:
            self.redis_client.setex(
                f"conversation:{state.session_id}", 
                3600,  # 1小時過期
                json.dumps(state.to_dict())
            )
        except Exception as e:
            print(f"Error saving conversation state: {e}")
    
    def _analyze_user_message_with_memory(self, state: ConversationState, message: str):
        """基於記憶分析用戶訊息"""
        
        # 構建包含記憶的提示詞
        memory_context = ""
        if state.conversation_memory:
            memory_context = f"""
            對話記憶:
            {json.dumps(state.conversation_memory, ensure_ascii=False, indent=2)}
            """
        
        # 使用 LLM 分析用戶訊息
        analysis_prompt = f"""
        分析用戶的訊息，提取旅遊規劃相關資訊。
        
        {memory_context}
        
        用戶當前訊息: {message}
        
        請從以下類別中識別並提取資訊：
        - destination: 目的地 (如: 宜蘭、台北、花蓮)
        - duration: 旅遊天數 (如: 1天、2天1夜、3天2夜)
        - interests: 興趣類型 (如: 美食、風景、文化、購物)
        - budget: 預算範圍 (如: 低、中、高)
        - travel_style: 旅遊風格 (如: 輕鬆、緊湊、深度)
        - group_size: 人數 (如: 1人、2人、家庭)
        
        請以 JSON 格式回應，只包含識別到的資訊。如果沒有識別到任何資訊，請返回空的 JSON 物件 {{}}。
        範例: {{"destination": "宜蘭", "duration": "2天1夜", "interests": ["美食", "風景"]}}
        """
        
        try:
            analysis = self.gemini_client.generate_text(analysis_prompt)
            print(f"🔍 基於記憶的分析結果: {analysis}")
            
            # 嘗試解析 JSON 回應
            try:
                extracted_info = json.loads(analysis)
            except json.JSONDecodeError:
                # 如果 JSON 解析失敗，嘗試提取 JSON 部分
                import re
                # 處理 ```json 標記
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis, re.DOTALL)
                if json_match:
                    extracted_info = json.loads(json_match.group(1))
                else:
                    # 嘗試提取純 JSON
                    json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
                    if json_match:
                        extracted_info = json.loads(json_match.group())
                    else:
                        print(f"❌ 無法解析 JSON: {analysis}")
                        extracted_info = {}
            
            # 更新收集的資訊
            for key, value in extracted_info.items():
                if key in self.required_info:
                    state.add_info(key, value)
                    
        except Exception as e:
            print(f"Error analyzing user message with memory: {e}")
            # 備用方案：簡單關鍵字匹配
            self._fallback_keyword_analysis(state, message)
    
    def _fallback_keyword_analysis(self, state: ConversationState, message: str):
        """備用關鍵字分析"""
        if "宜蘭" in message:
            state.add_info("destination", "宜蘭")
        if "台北" in message:
            state.add_info("destination", "台北")
        if "花蓮" in message:
            state.add_info("destination", "花蓮")
        if "高雄" in message:
            state.add_info("destination", "高雄")
        if "1天" in message or "一天" in message:
            state.add_info("duration", "1天")
        if "2天" in message or "兩天" in message:
            state.add_info("duration", "2天1夜")
        if "3天" in message or "三天" in message:
            state.add_info("duration", "3天2夜")
        if "美食" in message:
            if "interests" not in state.collected_info:
                state.collected_info["interests"] = []
            if "美食" not in state.collected_info["interests"]:
                state.collected_info["interests"].append("美食")
        if "風景" in message or "自然" in message:
            if "interests" not in state.collected_info:
                state.collected_info["interests"] = []
            if "自然風景" not in state.collected_info["interests"]:
                state.collected_info["interests"].append("自然風景")
    
    def _is_info_complete(self, state: ConversationState) -> bool:
        """檢查是否收集足夠的資訊"""
        # 至少需要目的地和天數
        essential_keys = ["destination", "duration"]
        return all(key in state.collected_info for key in essential_keys)
    
    def _generate_next_question_with_memory(self, state: ConversationState) -> str:
        """基於記憶生成下一個問題"""
        
        # 構建記憶上下文
        memory_context = ""
        if state.conversation_memory:
            memory_context = f"""
            對話記憶:
            {json.dumps(state.conversation_memory, ensure_ascii=False, indent=2)}
            """
        
        # 找出還需要收集的資訊
        missing_info = []
        for key, label in self.required_info.items():
            if key not in state.collected_info:
                missing_info.append(label)
        
        # 生成問題
        question_prompt = f"""
        基於已收集的資訊、對話記憶和對話歷史，生成一個自然的問題來收集更多旅遊規劃資訊。
        
        {memory_context}
        
        已收集的資訊: {json.dumps(state.collected_info, ensure_ascii=False)}
        還需要收集: {', '.join(missing_info)}
        對話歷史: {json.dumps(state.conversation_history[-3:], ensure_ascii=False)}
        
        請生成一個友善、自然的問題，幫助收集旅遊規劃資訊。
        回應格式: 直接返回問題文字，不要其他內容。
        """
        
        try:
            question = self.gemini_client.generate_text(question_prompt)
            return question.strip()
            
        except Exception as e:
            print(f"Error generating question with memory: {e}")
            return "請告訴我您想去哪裡旅遊呢？"
