"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatPanel, ItineraryPanel } from "@/components/planning";
import { AppLayout } from "@/components/layout";

interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  suggestions?: string[];
}

interface Preferences {
  destination: string;
  startDate: string;
  endDate: string;
  duration: number;
  interests: string[];
  budget: string;
  pace: string;
}

interface Itinerary {
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
}

export default function PlanResultPage() {
  const router = useRouter();
  const [preferences, setPreferences] = useState<Preferences>({
    destination: "台北市",
    startDate: "2024-02-15",
    endDate: "2024-02-17",
    duration: 3,
    interests: ["food", "culture"],
    budget: "moderate",
    pace: "moderate"
  });
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [conversationSummary, setConversationSummary] = useState<string>("");
  const [smartSuggestions, setSmartSuggestions] = useState<string[]>([]);

  useEffect(() => {
    // 初始化歡迎訊息
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'ai',
      content: '您好！我是您的 AI 旅遊助手。我已經根據您的偏好開始規劃行程，您可以隨時告訴我任何調整需求。',
      timestamp: new Date(),
      suggestions: [
        "我想增加一個美食景點",
        "調整行程時間",
        "推薦附近的住宿"
      ]
    };
    setMessages([welcomeMessage]);

    // 模擬生成初始行程
    generateInitialItinerary();
  }, []);

  const generateInitialItinerary = async () => {
    setIsGenerating(true);
    
    // 模擬 API 呼叫
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const mockItinerary: Itinerary = {
      days: [
        {
          day: 1,
          date: "2024-02-15",
          visits: [
            {
              place_id: "1",
              name: "台北101",
              eta: "09:00",
              etd: "11:00",
              travel_minutes: 0,
              stay_minutes: 120
            },
            {
              place_id: "2",
              name: "信義商圈",
              eta: "11:30",
              etd: "14:30",
              travel_minutes: 30,
              stay_minutes: 180
            },
            {
              place_id: "3",
              name: "松山文創園區",
              eta: "15:00",
              etd: "17:00",
              travel_minutes: 30,
              stay_minutes: 120
            }
          ],
          accommodation: {
            name: "台北君悅酒店",
            address: "台北市信義區松仁路100號",
            rating: 4.5,
            price: 8000
          }
        },
        {
          day: 2,
          date: "2024-02-16",
          visits: [
            {
              place_id: "4",
              name: "故宮博物院",
              eta: "09:00",
              etd: "12:00",
              travel_minutes: 0,
              stay_minutes: 180
            },
            {
              place_id: "5",
              name: "士林夜市",
              eta: "18:00",
              etd: "21:00",
              travel_minutes: 60,
              stay_minutes: 180
            }
          ],
          accommodation: {
            name: "台北君悅酒店",
            address: "台北市信義區松仁路100號",
            rating: 4.5,
            price: 8000
          }
        },
        {
          day: 3,
          date: "2024-02-17",
          visits: [
            {
              place_id: "6",
              name: "九份老街",
              eta: "09:00",
              etd: "15:00",
              travel_minutes: 0,
              stay_minutes: 360
            }
          ]
        }
      ]
    };

    setItinerary(mockItinerary);
    setIsGenerating(false);
  };


  const handleGenerateItinerary = async () => {
    setIsGenerating(true);
    
    // 新增系統訊息
    const systemMessage: ChatMessage = {
      id: `system-${Date.now()}`,
      type: 'system',
      content: '正在根據您的偏好重新生成行程...',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);

    // 模擬 API 呼叫
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 重新生成行程
    await generateInitialItinerary();
    
    // 新增完成訊息
    const completeMessage: ChatMessage = {
      id: `ai-${Date.now()}`,
      type: 'ai',
      content: '行程已重新生成！請查看右側的詳細安排，有任何需要調整的地方請告訴我。',
      timestamp: new Date(),
      suggestions: [
        "我想增加一個美食景點",
        "調整某個景點的時間",
        "推薦更好的住宿選項"
      ]
    };
    setMessages(prev => [...prev, completeMessage]);
  };

  const extractKeywords = (text: string): string[] => {
    // 簡單的關鍵詞提取邏輯，可以根據需要擴展
    const commonKeywords = ['美食', '文化', '購物', '自然', '歷史', '夜市', '博物館', '公園', '寺廟', '餐廳', '咖啡廳', '酒吧', '溫泉', '海邊', '山區', '古蹟', '藝術', '音樂', '運動', '冒險', '放鬆'];
    const extracted = commonKeywords.filter(keyword => text.includes(keyword));
    return extracted;
  };

  const updateConversationSummary = (newMessage: string) => {
    // 簡單的對話摘要更新邏輯
    const userMessages = messages.filter(msg => msg.type === 'user');
    if (userMessages.length >= 2) {
      setConversationSummary("您已提出多項需求，AI 正在為您整合最佳行程方案");
    } else if (userMessages.length === 1) {
      setConversationSummary("您已開始與 AI 討論行程細節");
    } else {
      setConversationSummary("歡迎開始與 AI 討論您的行程需求");
    }
  };

  const generateSmartSuggestions = (keywords: string[]) => {
    // 基於關鍵詞生成智能建議
    const suggestions: string[] = [];
    
    if (keywords.includes('美食')) {
      suggestions.push("推薦當地特色餐廳");
    }
    if (keywords.includes('文化')) {
      suggestions.push("安排博物館參觀");
    }
    if (keywords.includes('自然')) {
      suggestions.push("規劃戶外景點");
    }
    if (keywords.includes('夜市')) {
      suggestions.push("安排夜市美食之旅");
    }
    if (keywords.includes('溫泉')) {
      suggestions.push("加入溫泉放鬆行程");
    }
    
    // 預設建議
    if (suggestions.length === 0) {
      suggestions.push("調整行程時間安排", "推薦附近景點", "優化交通路線");
    }
    
    return suggestions.slice(0, 3); // 最多顯示3個建議
  };

  const handleSendMessage = async (message: string) => {
    // 新增使用者訊息
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsChatLoading(true);

    // 提取關鍵詞
    const newKeywords = extractKeywords(message);
    if (newKeywords.length > 0) {
      setKeywords(prev => {
        const combined = [...prev, ...newKeywords];
        return Array.from(new Set(combined)); // 去重
      });
    }

    // 更新對話摘要
    updateConversationSummary(message);

    // 生成智能建議
    const updatedKeywords = [...keywords, ...newKeywords];
    const suggestions = generateSmartSuggestions(updatedKeywords);
    setSmartSuggestions(suggestions);

    // 模擬 AI 回應
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const aiMessage: ChatMessage = {
      id: `ai-${Date.now()}`,
      type: 'ai',
      content: '我了解您的需求，正在為您調整行程。請稍等片刻，我會為您提供最佳的解決方案。',
      timestamp: new Date(),
      suggestions: [
        "查看調整後的行程",
        "還有其他需求嗎？",
        "儲存這個行程"
      ]
    };
    setMessages(prev => [...prev, aiMessage]);
    setIsChatLoading(false);
  };

  const handleSaveItinerary = () => {
    alert("行程儲存功能開發中...");
  };

  const handleDownloadItinerary = () => {
    alert("行程下載功能開發中...");
  };

  return (
    <AppLayout showFooter={false} className="h-screen">
      {/* 頂部導航 */}
      <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.back()}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
              AI 行程規劃助手
            </h1>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-sm text-slate-500 dark:text-slate-400">
              {preferences.destination} • {preferences.duration} 天行程
            </div>
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-xs text-green-600 dark:text-green-400">AI 在線</span>
          </div>
        </div>
      </div>

      {/* 主要內容區域 */}
      <div className="flex-1 flex overflow-hidden">
        {/* 左側：對話摘要面板 */}
        <div className="w-80 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-6">
          <div className="space-y-6">
            {/* 對話摘要 */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                對話摘要
              </h3>
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {conversationSummary || "歡迎開始與 AI 討論您的行程需求"}
                </p>
              </div>
            </div>

            {/* 對話關鍵詞 */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                對話關鍵詞
              </h3>
              <div className="space-y-3">
                {keywords.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {keywords.map((keyword, index) => (
                      <button
                        key={index}
                        onClick={() => handleSendMessage(`我想了解更多關於${keyword}的資訊`)}
                        className="px-3 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 text-sm rounded-full hover:bg-primary-200 dark:hover:bg-primary-900/30 transition-colors cursor-pointer"
                      >
                        {keyword}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-slate-500 dark:text-slate-400 italic">
                    開始對話後，關鍵詞會自動出現在這裡
                  </div>
                )}
              </div>
            </div>

            {/* 智能建議 */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                智能建議
              </h3>
              <div className="space-y-2">
                {smartSuggestions.length > 0 ? (
                  smartSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(suggestion)}
                      className="w-full text-left px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 text-sm rounded-lg transition-colors"
                    >
                      💡 {suggestion}
                    </button>
                  ))
                ) : (
                  <div className="text-sm text-slate-500 dark:text-slate-400 italic">
                    基於您的對話內容提供建議
                  </div>
                )}
              </div>
            </div>

            {/* 行程摘要 */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                行程摘要
              </h3>
              <div className="space-y-3">
                <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <div className="text-sm text-slate-600 dark:text-slate-400">目的地</div>
                  <div className="text-sm font-medium text-slate-900 dark:text-white">{preferences.destination}</div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <div className="text-sm text-slate-600 dark:text-slate-400">行程天數</div>
                  <div className="text-sm font-medium text-slate-900 dark:text-white">{preferences.duration} 天</div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <div className="text-sm text-slate-600 dark:text-slate-400">預算等級</div>
                  <div className="text-sm font-medium text-slate-900 dark:text-white">
                    {preferences.budget === 'budget' ? '經濟型' : 
                     preferences.budget === 'medium' ? '中等' : '豪華型'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 中間：對話面板 */}
        <div className="flex-1 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700">
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isChatLoading}
          />
        </div>

        {/* 右側：行程面板 */}
        <div className="w-96 bg-white dark:bg-slate-800">
          <ItineraryPanel
            itinerary={itinerary}
            isLoading={isGenerating}
            onSaveItinerary={handleSaveItinerary}
            onDownloadItinerary={handleDownloadItinerary}
          />
        </div>
      </div>
    </AppLayout>
  );
}