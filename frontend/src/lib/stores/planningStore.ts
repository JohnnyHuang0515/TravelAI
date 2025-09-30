import { create } from "zustand";
import { persist } from "zustand/middleware";
import { PlanningRequest, PlanningResponse, ChatMessage } from "@/lib/api/planning";

interface PlanningState {
  // 表單資料
  formData: PlanningRequest | null;
  
  // 行程資料
  itinerary: PlanningResponse | null;
  
  // 聊天相關
  messages: ChatMessage[];
  sessionId: string | null;
  isGenerating: boolean;
  isChatLoading: boolean;
  
  // 關鍵詞和摘要
  keywords: string[];
  conversationSummary: string;
  smartSuggestions: string[];
  
  // 錯誤狀態
  error: string | null;

  // Actions
  setFormData: (data: PlanningRequest) => void;
  setItinerary: (itinerary: PlanningResponse | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  setSessionId: (sessionId: string | null) => void;
  setGenerating: (generating: boolean) => void;
  setChatLoading: (loading: boolean) => void;
  setKeywords: (keywords: string[]) => void;
  addKeywords: (newKeywords: string[]) => void;
  setConversationSummary: (summary: string) => void;
  setSmartSuggestions: (suggestions: string[]) => void;
  setError: (error: string | null) => void;
  
  // 重置狀態
  reset: () => void;
  resetChat: () => void;
}

const initialState = {
  formData: null,
  itinerary: null,
  messages: [],
  sessionId: null,
  isGenerating: false,
  isChatLoading: false,
  keywords: [],
  conversationSummary: "",
  smartSuggestions: [],
  error: null,
};

export const usePlanningStore = create<PlanningState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setFormData: (data) => set({ formData: data }),
      
      setItinerary: (itinerary) => set({ itinerary }),
      
      setMessages: (messages) => set({ messages }),
      
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),
      
      setSessionId: (sessionId) => set({ sessionId }),
      
      setGenerating: (generating) => set({ isGenerating: generating }),
      
      setChatLoading: (loading) => set({ isChatLoading: loading }),
      
      setKeywords: (keywords) => set({ keywords }),
      
      addKeywords: (newKeywords) =>
        set((state) => {
          const combined = [...state.keywords, ...newKeywords];
          return {
            keywords: Array.from(new Set(combined)), // 去重
          };
        }),
      
      setConversationSummary: (summary) => set({ conversationSummary: summary }),
      
      setSmartSuggestions: (suggestions) => set({ smartSuggestions: suggestions }),
      
      setError: (error) => set({ error }),

      reset: () => set(initialState),
      
      resetChat: () =>
        set({
          messages: [],
          sessionId: null,
          isGenerating: false,
          isChatLoading: false,
          keywords: [],
          conversationSummary: "",
          smartSuggestions: [],
          error: null,
        }),
    }),
    {
      name: "planning-store",
      partialize: (state) => ({
        formData: state.formData,
        itinerary: state.itinerary,
        sessionId: state.sessionId,
        keywords: state.keywords,
        conversationSummary: state.conversationSummary,
        smartSuggestions: state.smartSuggestions,
      }),
    }
  )
);
