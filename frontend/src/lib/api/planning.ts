import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface PlanningRequest {
  destination: string;
  start_date: string;
  days: number;
  travelers: number;
  interests: string[];
  budget: "budget" | "medium" | "luxury";
  pace: "relaxed" | "moderate" | "intensive";
  user_id?: string;
}

export interface PlanningResponse {
  itinerary: {
    days: Array<{
      day: number;
      date: string;
      visits: Array<{
        place_id: string;
        name: string;
        eta: string;
        etd: string;
        travel_minutes: number;
        stay_minutes: number;
      }>;
      accommodation?: {
        name: string;
        address: string;
        rating: number;
        price: number;
      };
    }>;
  };
  session_id: string;
  total_cost_estimate: number;
  total_travel_time: number;
}

export interface ChatMessage {
  id: string;
  type: "user" | "ai" | "system";
  content: string;
  timestamp: string;
  suggestions?: string[];
}

export interface ChatRequest {
  message: string;
  session_id: string;
  user_id?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  updated_itinerary?: PlanningResponse["itinerary"];
  suggestions?: string[];
}

export interface FeedbackRequest {
  session_id: string;
  feedback_type: "positive" | "negative" | "neutral";
  feedback_text?: string;
  user_id?: string;
}

export interface SessionStatus {
  session_id: string;
  status: "active" | "completed" | "expired";
  created_at: string;
  last_activity: string;
  message_count: number;
  user_id?: string;
}

// 生成行程
export const generateItinerary = async (request: PlanningRequest): Promise<PlanningResponse> => {
  const response = await axios.post(`${API_BASE_URL}/v1/itinerary/propose`, request, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

// 舊的對話 API 已移除，請使用 unifiedChat 或 sendUnifiedMessage

// 統一對話引擎API
export interface UnifiedConversationRequest {
  session_id: string;
  message: string;
  conversation_history?: Array<{role: string; content: string}>;
  user_preferences?: Record<string, any>;
  context?: Record<string, any>;
}

export interface UnifiedConversationResponse {
  session_id: string;
  message: string;
  intent: string;
  suggestions: string[];
  collected_info: Record<string, any>;
  is_complete: boolean;
  itinerary?: any;
  confidence_score: number;
  turn_count: number;
  timestamp: string;
  error?: string;
}

export interface ConversationStateResponse {
  session_id: string;
  current_intent?: string;
  collected_info: Record<string, any>;
  conversation_history: Array<{role: string; content: string; timestamp: string}>;
  confidence_score: number;
  last_activity: string;
  turn_count: number;
}

// 統一對話聊天
export const unifiedChat = async (request: UnifiedConversationRequest): Promise<UnifiedConversationResponse> => {
  const response = await axios.post(`${API_BASE_URL}/v1/conversation/chat`, request, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

// 發送單一訊息
export const sendUnifiedMessage = async (sessionId: string, message: string, metadata?: Record<string, any>): Promise<UnifiedConversationResponse> => {
  const response = await axios.post(`${API_BASE_URL}/v1/conversation/message`, {
    session_id: sessionId,
    message,
    metadata
  }, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

// 獲取對話狀態
export const getUnifiedConversationState = async (sessionId: string): Promise<ConversationStateResponse> => {
  const response = await axios.get(`${API_BASE_URL}/v1/conversation/state/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 重置對話
export const resetUnifiedConversation = async (sessionId: string): Promise<void> => {
  await axios.post(`${API_BASE_URL}/v1/conversation/reset/${sessionId}`, {}, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });
};

// 獲取智能建議
export const getUnifiedSuggestions = async (sessionId: string, context?: string): Promise<{session_id: string; suggestions: string[]; context?: string; timestamp: string}> => {
  const response = await axios.get(`${API_BASE_URL}/v1/conversation/suggestions/${sessionId}`, {
    params: { context },
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 獲取會話統計
export const getUnifiedSessionStats = async (sessionId: string): Promise<{
  session_id: string;
  turn_count: number;
  collected_info_count: number;
  confidence_score: number;
  last_activity: string;
  conversation_duration?: number;
  completion_rate: number;
  timestamp: string;
}> => {
  const response = await axios.get(`${API_BASE_URL}/v1/conversation/stats/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 舊的 getChatHistory, getSessionStatus, resetSession 已移除
// 請使用統一對話引擎的對應方法：
// - getUnifiedConversationState
// - resetUnifiedConversation

// 提交回饋
export const submitFeedback = async (request: FeedbackRequest): Promise<void> => {
  await axios.post(`${API_BASE_URL}/v1/itinerary/feedback`, request, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });
};

// 儲存行程到我的行程
export const saveItineraryToTrips = async (
  sessionId: string,
  title: string
): Promise<{ trip_id: string }> => {
  const response = await axios.post(
    `${API_BASE_URL}/v1/trips/save-from-session`,
    {
      session_id: sessionId,
      title,
    },
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    }
  );

  return response.data;
};
