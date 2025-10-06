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

// 發送聊天訊息
export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await axios.post(`${API_BASE_URL}/v1/chat/message`, request, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

// 取得聊天歷史
export const getChatHistory = async (sessionId: string): Promise<ChatMessage[]> => {
  const response = await axios.get(`${API_BASE_URL}/v1/chat/history/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 取得會話狀態
export const getSessionStatus = async (sessionId: string): Promise<SessionStatus> => {
  const response = await axios.get(`${API_BASE_URL}/v1/chat/session/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 重置會話
export const resetSession = async (sessionId: string): Promise<void> => {
  await axios.post(`${API_BASE_URL}/v1/chat/reset/${sessionId}`, {}, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });
};

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
