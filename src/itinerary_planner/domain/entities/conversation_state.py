from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime

class ConversationStateType(Enum):
    """對話狀態類型"""
    COLLECTING_INFO = "collecting_info"
    GENERATING_ITINERARY = "generating_itinerary"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class ConversationState:
    """對話狀態實體 - 支援單次對話記憶"""
    session_id: str
    state: ConversationStateType
    collected_info: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    is_complete: bool = False
    
    # 新增：單次對話記憶
    conversation_memory: Dict[str, Any] = field(default_factory=dict)
    context_summary: str = ""
    turn_count: int = 0
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_info(self, key: str, value: Any):
        """添加收集到的資訊"""
        self.collected_info[key] = value
        self.updated_at = datetime.now()
    
    def add_message(self, role: str, content: str):
        """添加對話訊息"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def add_context_memory(self, key: str, value: Any):
        """添加上下文記憶"""
        self.conversation_memory[key] = value
        self.updated_at = datetime.now()
    
    def get_context_summary(self) -> str:
        """獲取上下文摘要"""
        if not self.context_summary and self.conversation_history:
            # 生成簡短的上下文摘要
            recent_messages = self.conversation_history[-3:]
            summary_parts = []
            for msg in recent_messages:
                if msg["role"] == "user":
                    summary_parts.append(f"用戶: {msg['content'][:50]}...")
            self.context_summary = " | ".join(summary_parts)
        return self.context_summary
    
    def increment_turn(self):
        """增加對話輪次"""
        self.turn_count += 1
        self.updated_at = datetime.now()
    
    def set_state(self, new_state: ConversationStateType):
        """設置新的對話狀態"""
        self.state = new_state
        self.updated_at = datetime.now()
        
        # 如果狀態是完成，標記為完成
        if new_state == ConversationStateType.COMPLETED:
            self.is_complete = True
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "collected_info": self.collected_info,
            "conversation_history": self.conversation_history,
            "is_complete": self.is_complete,
            "conversation_memory": self.conversation_memory,
            "context_summary": self.context_summary,
            "turn_count": self.turn_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationState':
        """從字典創建實體"""
        return cls(
            session_id=data["session_id"],
            state=ConversationStateType(data["state"]),
            collected_info=data.get("collected_info", {}),
            conversation_history=data.get("conversation_history", []),
            is_complete=data.get("is_complete", False),
            conversation_memory=data.get("conversation_memory", {}),
            context_summary=data.get("context_summary", ""),
            turn_count=data.get("turn_count", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
