from typing import Dict, List, Optional, Any, Tuple
import logging
import json
import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ...infrastructure.clients.gemini_llm_client import GeminiLLMClient

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """實體類型"""
    DESTINATION = "destination"
    DURATION = "duration"
    INTEREST = "interest"
    BUDGET = "budget"
    TRAVEL_STYLE = "travel_style"
    GROUP_SIZE = "group_size"
    DATE = "date"
    TIME = "time"
    LOCATION = "location"
    ACTIVITY = "activity"

@dataclass
class ExtractedEntity:
    """提取的實體"""
    type: EntityType
    value: Any
    confidence: float
    context: str
    start_pos: int
    end_pos: int

@dataclass
class ConversationContext:
    """對話上下文"""
    session_id: str
    user_profile: Dict[str, Any]
    conversation_memory: Dict[str, Any]
    recent_intents: List[str]
    extracted_entities: List[ExtractedEntity]
    conversation_history: List[Dict[str, Any]]
    last_activity: datetime

class IntelligentUnderstandingService:
    """智能對話理解服務"""
    
    def __init__(self):
        self.llm_client = GeminiLLMClient()
        
        # 預定義的實體模式
        self.entity_patterns = {
            EntityType.DESTINATION: [
                r"去(.+?)(?:旅遊|旅行|玩)",
                r"到(.+?)(?:旅遊|旅行|玩)",
                r"在(.+?)(?:旅遊|旅行|玩)",
                r"想去(.+?)$",
                r"(.+?)(?:市|縣|區|鎮|鄉)$"
            ],
            EntityType.DURATION: [
                r"(\d+)(?:天|日)",
                r"玩(\d+)(?:天|日)",
                r"待(\d+)(?:天|日)",
                r"(\d+)(?:個)?(?:星期|週)",
                r"(\d+)(?:個)?月"
            ],
            EntityType.INTEREST: [
                r"喜歡(.+?)(?:景點|地方)",
                r"對(.+?)(?:有興趣|感興趣)",
                r"想要(.+?)(?:體驗|參觀)",
                r"(.+?)(?:愛好|興趣|偏好)"
            ],
            EntityType.BUDGET: [
                r"(?:預算|花費|費用)(?:是|大概|約)?(.+?)",
                r"(?:經濟|便宜|省錢)",
                r"(?:中等|一般|普通)",
                r"(?:豪華|高檔|奢華)"
            ],
            EntityType.GROUP_SIZE: [
                r"(\d+)(?:個人|人|位)",
                r"(?:我們|我們家)(?:有)?(\d+)(?:個人|人|位)",
                r"(\d+)(?:個)?(?:朋友|家人|同伴)"
            ]
        }
        
        # 情感詞典
        self.sentiment_words = {
            "positive": ["喜歡", "愛", "想要", "希望", "期待", "興奮", "開心", "滿意"],
            "negative": ["不喜歡", "討厭", "不想", "拒絕", "失望", "不滿意", "討厭"],
            "neutral": ["可以", "還好", "一般", "普通", "無所謂"]
        }
        
        # 意圖關鍵詞
        self.intent_keywords = {
            "greeting": ["你好", "嗨", "hello", "hi", "開始", "請問"],
            "provide_info": ["我想", "我要", "我們要", "計劃", "打算", "想要"],
            "ask_question": ["什麼", "哪裡", "如何", "怎麼", "為什麼", "什麼時候"],
            "modify": ["修改", "改變", "調整", "換", "不要", "改成"],
            "confirm": ["是的", "對", "沒錯", "確認", "好的", "可以"],
            "reject": ["不要", "不行", "拒絕", "算了", "不用"]
        }
    
    async def analyze_message(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """分析用戶訊息"""
        
        # 1. 意圖識別
        intent = await self._recognize_intent(message, context)
        
        # 2. 實體提取
        entities = await self._extract_entities(message, context)
        
        # 3. 情感分析
        sentiment = await self._analyze_sentiment(message, context)
        
        # 4. 上下文理解
        contextual_info = await self._understand_context(message, context)
        
        # 5. 置信度計算
        confidence = self._calculate_confidence(intent, entities, sentiment)
        
        return {
            "intent": intent,
            "entities": entities,
            "sentiment": sentiment,
            "contextual_info": contextual_info,
            "confidence": confidence,
            "processed_at": datetime.now().isoformat()
        }
    
    async def _recognize_intent(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """識別對話意圖"""
        
        # 基於關鍵詞的快速識別
        quick_intent = self._quick_intent_recognition(message)
        
        # 使用LLM進行深度分析
        llm_intent = await self._llm_intent_analysis(message, context)
        
        # 結合兩種結果
        final_intent = self._combine_intent_results(quick_intent, llm_intent)
        
        return final_intent
    
    def _quick_intent_recognition(self, message: str) -> Dict[str, Any]:
        """快速意圖識別（基於關鍵詞）"""
        
        message_lower = message.lower()
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return {
                        "type": intent,
                        "confidence": 0.7,
                        "method": "keyword",
                        "matched_keyword": keyword
                    }
        
        return {
            "type": "unknown",
            "confidence": 0.3,
            "method": "keyword"
        }
    
    async def _llm_intent_analysis(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """使用LLM進行意圖分析"""
        
        # 構建上下文信息
        recent_context = self._build_context_summary(context)
        
        prompt = f"""
你是一個專業的對話意圖分析專家。請分析用戶的對話意圖。

對話歷史：
{recent_context}

當前用戶訊息：{message}

請分析用戶的意圖，並提供以下信息：
1. 意圖類型：greeting, provide_info, ask_question, modify, confirm, reject, unknown
2. 置信度：0-1之間的數值
3. 關鍵證據：支撐判斷的關鍵詞或短語
4. 子意圖：更具體的意圖描述（如果適用）

請以JSON格式返回結果：
{{
    "type": "意圖類型",
    "confidence": 置信度數值,
    "evidence": "關鍵證據",
    "sub_intent": "子意圖描述"
}}
"""
        
        try:
            response = await self.llm_client.generate_response(prompt)
            result = json.loads(response)
            
            return {
                "type": result.get("type", "unknown"),
                "confidence": float(result.get("confidence", 0.5)),
                "method": "llm",
                "evidence": result.get("evidence", ""),
                "sub_intent": result.get("sub_intent", "")
            }
            
        except Exception as e:
            logger.error(f"Error in LLM intent analysis: {e}")
            return {
                "type": "unknown",
                "confidence": 0.3,
                "method": "llm_error"
            }
    
    def _combine_intent_results(
        self, 
        quick_result: Dict[str, Any], 
        llm_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """結合快速識別和LLM分析的結果"""
        
        # 如果兩種方法結果一致，提高置信度
        if quick_result["type"] == llm_result["type"]:
            combined_confidence = min(0.95, (quick_result["confidence"] + llm_result["confidence"]) / 2 + 0.1)
            return {
                "type": quick_result["type"],
                "confidence": combined_confidence,
                "method": "combined",
                "quick_result": quick_result,
                "llm_result": llm_result
            }
        
        # 如果結果不一致，選擇置信度較高的
        if llm_result["confidence"] > quick_result["confidence"]:
            return {
                **llm_result,
                "method": "combined",
                "quick_result": quick_result
            }
        else:
            return {
                **quick_result,
                "method": "combined",
                "llm_result": llm_result
            }
    
    async def _extract_entities(
        self, 
        message: str, 
        context: ConversationContext
    ) -> List[ExtractedEntity]:
        """提取實體"""
        
        entities = []
        
        # 1. 基於正則表達式的實體提取
        regex_entities = self._extract_entities_by_regex(message)
        entities.extend(regex_entities)
        
        # 2. 使用LLM進行實體提取
        llm_entities = await self._extract_entities_by_llm(message, context)
        entities.extend(llm_entities)
        
        # 3. 去重和合併
        merged_entities = self._merge_entities(entities)
        
        return merged_entities
    
    def _extract_entities_by_regex(self, message: str) -> List[ExtractedEntity]:
        """基於正則表達式提取實體"""
        
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message)
                for match in matches:
                    entity = ExtractedEntity(
                        type=entity_type,
                        value=match.group(1) if match.groups() else match.group(0),
                        confidence=0.8,
                        context=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    entities.append(entity)
        
        return entities
    
    async def _extract_entities_by_llm(
        self, 
        message: str, 
        context: ConversationContext
    ) -> List[ExtractedEntity]:
        """使用LLM提取實體"""
        
        prompt = f"""
你是一個專業的命名實體識別專家。請從用戶訊息中提取旅遊相關的實體。

用戶訊息：{message}

請提取以下類型的實體：
1. destination: 目的地（城市、地區、景點名稱）
2. duration: 時間長度（天數、週數等）
3. interest: 興趣類型（美食、文化、自然等）
4. budget: 預算信息（經濟、中等、豪華等）
5. travel_style: 旅遊風格（悠閒、緊湊等）
6. group_size: 人數
7. date: 日期（出發日期、特定日期）
8. location: 具體地點（餐廳、酒店、景點）
9. activity: 活動類型

對於每個提取的實體，請提供：
- 實體類型
- 實體值
- 置信度（0-1）
- 在原文中的位置（開始和結束字符位置）

請以JSON格式返回：
{{
    "entities": [
        {{
            "type": "實體類型",
            "value": "實體值",
            "confidence": 置信度,
            "start_pos": 開始位置,
            "end_pos": 結束位置
        }}
    ]
}}
"""
        
        try:
            response = await self.llm_client.generate_response(prompt)
            result = json.loads(response)
            
            entities = []
            for entity_data in result.get("entities", []):
                try:
                    entity = ExtractedEntity(
                        type=EntityType(entity_data["type"]),
                        value=entity_data["value"],
                        confidence=float(entity_data["confidence"]),
                        context=message[entity_data["start_pos"]:entity_data["end_pos"]],
                        start_pos=entity_data["start_pos"],
                        end_pos=entity_data["end_pos"]
                    )
                    entities.append(entity)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid entity data: {entity_data}, error: {e}")
                    continue
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in LLM entity extraction: {e}")
            return []
    
    def _merge_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """合併重複的實體"""
        
        # 按類型分組
        grouped_entities = {}
        for entity in entities:
            if entity.type not in grouped_entities:
                grouped_entities[entity.type] = []
            grouped_entities[entity.type].append(entity)
        
        merged_entities = []
        
        for entity_type, entity_list in grouped_entities.items():
            # 如果只有一個實體，直接添加
            if len(entity_list) == 1:
                merged_entities.append(entity_list[0])
                continue
            
            # 選擇置信度最高的實體
            best_entity = max(entity_list, key=lambda e: e.confidence)
            
            # 如果有重疊的實體，選擇覆蓋範圍最大的
            if len(entity_list) > 1:
                overlapping = self._find_overlapping_entities(entity_list)
                if overlapping:
                    best_entity = max(overlapping, key=lambda e: e.confidence)
            
            merged_entities.append(best_entity)
        
        return merged_entities
    
    def _find_overlapping_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """找到重疊的實體"""
        
        overlapping = []
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                if self._entities_overlap(entity1, entity2):
                    overlapping.extend([entity1, entity2])
        
        # 使用索引來去重，因為ExtractedEntity不可哈希
        unique_overlapping = []
        seen_indices = set()
        for entity in overlapping:
            entity_index = entities.index(entity) if entity in entities else -1
            if entity_index not in seen_indices:
                unique_overlapping.append(entity)
                seen_indices.add(entity_index)
        
        return unique_overlapping
    
    def _entities_overlap(self, entity1: ExtractedEntity, entity2: ExtractedEntity) -> bool:
        """檢查兩個實體是否重疊"""
        
        return not (entity1.end_pos <= entity2.start_pos or entity2.end_pos <= entity1.start_pos)
    
    async def _analyze_sentiment(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """分析情感"""
        
        # 基於詞典的情感分析
        lexicon_sentiment = self._lexicon_sentiment_analysis(message)
        
        # 使用LLM進行情感分析
        llm_sentiment = await self._llm_sentiment_analysis(message, context)
        
        # 結合兩種結果
        combined_sentiment = self._combine_sentiment_results(lexicon_sentiment, llm_sentiment)
        
        return combined_sentiment
    
    def _lexicon_sentiment_analysis(self, message: str) -> Dict[str, Any]:
        """基於詞典的情感分析"""
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for sentiment, words in self.sentiment_words.items():
            for word in words:
                if word in message:
                    if sentiment == "positive":
                        positive_count += 1
                    elif sentiment == "negative":
                        negative_count += 1
                    else:
                        neutral_count += 1
        
        total = positive_count + negative_count + neutral_count
        
        if total == 0:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
            }
        
        scores = {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": neutral_count / total
        }
        
        dominant_sentiment = max(scores, key=scores.get)
        
        return {
            "sentiment": dominant_sentiment,
            "confidence": scores[dominant_sentiment],
            "scores": scores,
            "method": "lexicon"
        }
    
    async def _llm_sentiment_analysis(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """使用LLM進行情感分析"""
        
        prompt = f"""
你是一個專業的情感分析專家。請分析用戶訊息的情感傾向。

用戶訊息：{message}

請分析以下情感維度：
1. 整體情感：positive（正面）、negative（負面）、neutral（中性）
2. 情感強度：weak（弱）、moderate（中等）、strong（強）
3. 具體情感：開心、滿意、失望、憤怒、困惑等

請以JSON格式返回：
{{
    "sentiment": "整體情感",
    "intensity": "情感強度",
    "emotions": ["具體情感1", "具體情感2"],
    "confidence": 置信度數值
}}
"""
        
        try:
            response = await self.llm_client.generate_response(prompt)
            result = json.loads(response)
            
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "intensity": result.get("intensity", "moderate"),
                "emotions": result.get("emotions", []),
                "confidence": float(result.get("confidence", 0.7)),
                "method": "llm"
            }
            
        except Exception as e:
            logger.error(f"Error in LLM sentiment analysis: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "method": "llm_error"
            }
    
    def _combine_sentiment_results(
        self, 
        lexicon_result: Dict[str, Any], 
        llm_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """結合情感分析結果"""
        
        # 如果兩種方法結果一致，提高置信度
        if lexicon_result["sentiment"] == llm_result["sentiment"]:
            combined_confidence = min(0.95, (lexicon_result["confidence"] + llm_result["confidence"]) / 2 + 0.1)
            return {
                "sentiment": lexicon_result["sentiment"],
                "confidence": combined_confidence,
                "method": "combined",
                "lexicon_result": lexicon_result,
                "llm_result": llm_result
            }
        
        # 如果結果不一致，選擇置信度較高的
        if llm_result["confidence"] > lexicon_result["confidence"]:
            return {
                **llm_result,
                "method": "combined",
                "lexicon_result": lexicon_result
            }
        else:
            return {
                **lexicon_result,
                "method": "combined",
                "llm_result": llm_result
            }
    
    async def _understand_context(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """理解對話上下文"""
        
        # 分析對話主題
        topic = await self._identify_topic(message, context)
        
        # 分析對話階段
        stage = self._identify_conversation_stage(context)
        
        # 分析用戶需求變化
        needs_change = self._analyze_needs_change(message, context)
        
        # 分析對話連貫性
        coherence = self._analyze_coherence(message, context)
        
        return {
            "topic": topic,
            "stage": stage,
            "needs_change": needs_change,
            "coherence": coherence,
            "context_quality": self._calculate_context_quality(context)
        }
    
    async def _identify_topic(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """識別對話主題"""
        
        topic_keywords = {
            "planning": ["規劃", "計劃", "安排", "行程", "旅遊"],
            "destination": ["目的地", "去哪裡", "城市", "景點"],
            "accommodation": ["住宿", "酒店", "民宿", "房間"],
            "transportation": ["交通", "飛機", "火車", "汽車", "走路"],
            "activities": ["活動", "景點", "參觀", "體驗", "遊玩"],
            "budget": ["預算", "花費", "費用", "價格", "錢"],
            "timing": ["時間", "日期", "天數", "什麼時候"]
        }
        
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            dominant_topic = max(topic_scores, key=topic_scores.get)
            return {
                "primary": dominant_topic,
                "scores": topic_scores,
                "confidence": min(0.9, max(topic_scores.values()) / len(topic_keywords[dominant_topic]))
            }
        
        return {
            "primary": "general",
            "scores": {},
            "confidence": 0.3
        }
    
    def _identify_conversation_stage(self, context: ConversationContext) -> str:
        """識別對話階段"""
        
        if not context.conversation_history:
            return "initial"
        
        # 分析已收集的信息
        collected_info = context.extracted_entities
        has_destination = any(e.type == EntityType.DESTINATION for e in collected_info)
        has_duration = any(e.type == EntityType.DURATION for e in collected_info)
        has_interests = any(e.type == EntityType.INTEREST for e in collected_info)
        
        if not has_destination:
            return "collecting_destination"
        elif not has_duration:
            return "collecting_duration"
        elif not has_interests:
            return "collecting_interests"
        elif len(collected_info) < 4:
            return "collecting_details"
        else:
            return "ready_for_planning"
    
    def _analyze_needs_change(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """分析用戶需求變化"""
        
        change_indicators = ["不要", "改成", "換成", "修改", "調整", "改變"]
        
        has_change = any(indicator in message for indicator in change_indicators)
        
        if has_change:
            # 嘗試識別具體要改變的內容
            changed_items = []
            for indicator in change_indicators:
                if indicator in message:
                    # 提取改變的內容
                    parts = message.split(indicator)
                    if len(parts) > 1:
                        changed_items.append(parts[1].strip())
            
            return {
                "has_change": True,
                "changed_items": changed_items,
                "confidence": 0.8
            }
        
        return {
            "has_change": False,
            "changed_items": [],
            "confidence": 0.9
        }
    
    def _analyze_coherence(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """分析對話連貫性"""
        
        if not context.conversation_history:
            return {
                "is_coherent": True,
                "coherence_score": 1.0,
                "issues": []
            }
        
        # 檢查是否與之前的對話相關
        recent_messages = context.conversation_history[-3:]
        relevant_topics = set()
        
        for msg in recent_messages:
            if msg["role"] == "user":
                # 提取關鍵詞
                words = msg["content"].split()
                relevant_topics.update(words)
        
        current_words = set(message.split())
        overlap = len(relevant_topics.intersection(current_words))
        
        coherence_score = overlap / max(len(current_words), 1)
        
        issues = []
        if coherence_score < 0.2:
            issues.append("low_topic_relevance")
        
        return {
            "is_coherent": coherence_score > 0.3,
            "coherence_score": coherence_score,
            "issues": issues
        }
    
    def _calculate_context_quality(self, context: ConversationContext) -> float:
        """計算上下文質量"""
        
        # 基於多個因素計算質量分數
        factors = {
            "history_length": min(1.0, len(context.conversation_history) / 10),
            "entity_count": min(1.0, len(context.extracted_entities) / 5),
            "recency": 1.0 if (datetime.now() - context.last_activity).seconds < 300 else 0.5,
            "diversity": min(1.0, len(set(e.type for e in context.extracted_entities)) / 6)
        }
        
        return sum(factors.values()) / len(factors)
    
    def _calculate_confidence(
        self, 
        intent: Dict[str, Any], 
        entities: List[ExtractedEntity], 
        sentiment: Dict[str, Any]
    ) -> float:
        """計算整體置信度"""
        
        intent_confidence = intent.get("confidence", 0.5)
        
        entity_confidence = 0.5
        if entities:
            entity_confidence = sum(e.confidence for e in entities) / len(entities)
        
        sentiment_confidence = sentiment.get("confidence", 0.5)
        
        # 加權平均
        weights = {"intent": 0.4, "entities": 0.4, "sentiment": 0.2}
        
        overall_confidence = (
            intent_confidence * weights["intent"] +
            entity_confidence * weights["entities"] +
            sentiment_confidence * weights["sentiment"]
        )
        
        return min(0.95, max(0.1, overall_confidence))
    
    def _build_context_summary(self, context: ConversationContext) -> str:
        """構建上下文摘要"""
        
        if not context.conversation_history:
            return "這是對話的開始。"
        
        recent_messages = context.conversation_history[-5:]  # 最近5條消息
        
        summary_parts = []
        for msg in recent_messages:
            role = "用戶" if msg["role"] == "user" else "助手"
            summary_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(summary_parts)
