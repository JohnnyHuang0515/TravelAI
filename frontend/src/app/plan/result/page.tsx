"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ItineraryPanel } from "@/components/planning";
import { UnifiedChatPanel } from "@/components/conversation/UnifiedChatPanel";
import { AppLayout } from "@/components/layout";


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
    destination: "",
    startDate: "",
    endDate: "",
    duration: 1,
    interests: [],
    budget: "moderate",
    pace: "moderate"
  });
  
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 從 localStorage 載入用戶偏好
    loadUserPreferences();
  }, []);

  const loadUserPreferences = async () => {
    try {
      setIsLoading(true);
      
      // 從 localStorage 獲取規劃表單數據
      const planningFormData = localStorage.getItem("planningForm");
      if (planningFormData) {
        const formData = JSON.parse(planningFormData);
        setPreferences({
          destination: formData.destination || "",
          startDate: formData.startDate || "",
          endDate: formData.endDate || "",
          duration: formData.days || 1,
          interests: formData.interests || [],
          budget: formData.budget || "moderate",
          pace: formData.pace || "moderate"
        });
        
        // 載入偏好後生成初始行程
        await generateInitialItinerary(formData);
      } else {
        // 如果沒有偏好數據，重定向到規劃頁面
        router.push("/plan/start");
        return;
      }
    } catch (error) {
      console.error("載入用戶偏好失敗:", error);
      router.push("/plan/start");
    } finally {
      setIsLoading(false);
    }
  };

  const generateInitialItinerary = async (formData?: any) => {
    if (!formData && !preferences.destination) {
      return;
    }

    const userPrefs = formData || preferences;
    setIsGenerating(true);
    
    try {
      // 初始化歡迎訊息將在 UnifiedChatPanel 中處理

      // 調用統一對話引擎生成初始行程
      const sessionId = `unified_${Date.now()}`;
      const initialMessage = `我想去${userPrefs.destination}旅遊${userPrefs.days}天，我的興趣是${userPrefs.interests.join('、')}，預算等級是${userPrefs.budget}，行程節奏希望${userPrefs.pace}。請為我規劃一個完整的行程。`;
      
      // 這裡可以調用統一對話 API 來生成真實的行程
      // 暫時使用模擬數據，但會根據用戶偏好調整
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockItinerary = generateMockItineraryBasedOnPreferences(userPrefs);
      setItinerary(mockItinerary);
      
    } catch (error) {
      console.error("生成初始行程失敗:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateMockItineraryBasedOnPreferences = (prefs: any): Itinerary => {
    // 根據用戶偏好生成模擬行程
    const days = [];
    const startDate = new Date(prefs.startDate);
    
    for (let i = 0; i < prefs.days; i++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + i);
      
      const visits = [];
      
      // 根據興趣生成景點
      if (prefs.interests.includes('food')) {
        visits.push({
          place_id: `${i}-1`,
          name: `${prefs.destination}美食街`,
          eta: "12:00",
          etd: "14:00",
          travel_minutes: 0,
          stay_minutes: 120
        });
      }
      
      if (prefs.interests.includes('culture')) {
        visits.push({
          place_id: `${i}-2`,
          name: `${prefs.destination}文化景點`,
          eta: "09:00",
          etd: "11:30",
          travel_minutes: 0,
          stay_minutes: 150
        });
      }
      
      if (prefs.interests.includes('nature')) {
        visits.push({
          place_id: `${i}-3`,
          name: `${prefs.destination}自然景觀`,
          eta: "15:00",
          etd: "17:30",
          travel_minutes: 30,
          stay_minutes: 150
        });
      }
      
      if (prefs.interests.includes('shopping')) {
        visits.push({
          place_id: `${i}-4`,
          name: `${prefs.destination}購物中心`,
          eta: "18:00",
          etd: "20:00",
          travel_minutes: 15,
          stay_minutes: 120
        });
      }
      
      // 如果沒有選擇興趣，添加預設景點
      if (visits.length === 0) {
        visits.push({
          place_id: `${i}-default`,
          name: `${prefs.destination}著名景點`,
          eta: "10:00",
          etd: "16:00",
          travel_minutes: 0,
          stay_minutes: 360
        });
      }
      
      const dayItinerary = {
        day: i + 1,
        date: currentDate.toISOString().split('T')[0],
        visits: visits,
        accommodation: i === 0 ? {
          name: `${prefs.destination}精選酒店`,
          address: `${prefs.destination}市中心`,
          rating: prefs.budget === 'luxury' ? 4.8 : prefs.budget === 'budget' ? 4.2 : 4.5,
          price: prefs.budget === 'luxury' ? 12000 : prefs.budget === 'budget' ? 3000 : 6000
        } : undefined
      };
      
      days.push(dayItinerary);
    }

    return { days };
  };


  // 載入狀態顯示
  if (isLoading) {
    return (
      <AppLayout showFooter={false} className="h-screen">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-slate-600 dark:text-slate-400">正在載入您的行程偏好...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

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
              AI 旅遊助手
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
        {/* 左側：行程摘要面板 */}
        <div className="w-80 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-6">
          <div className="space-y-6">
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
                <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <div className="text-sm text-slate-600 dark:text-slate-400">行程節奏</div>
                  <div className="text-sm font-medium text-slate-900 dark:text-white">
                    {preferences.pace === 'relaxed' ? '悠閒' : 
                     preferences.pace === 'moderate' ? '適中' : '緊湊'}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <div className="text-sm text-slate-600 dark:text-slate-400">興趣偏好</div>
                  <div className="text-sm font-medium text-slate-900 dark:text-white">
                    {preferences.interests.length > 0 ? 
                      preferences.interests.map(interest => {
                        const labels: {[key: string]: string} = {
                          'food': '美食',
                          'nature': '自然',
                          'culture': '文化',
                          'shopping': '購物',
                          'adventure': '冒險',
                          'relaxation': '放鬆'
                        };
                        return labels[interest] || interest;
                      }).join('、') : 
                      '未設定'
                    }
                  </div>
                </div>
              </div>
            </div>

            {/* 快速操作 */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                快速操作
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => router.push("/plan/start")}
                  className="w-full text-left px-3 py-2 bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 text-sm rounded-lg hover:bg-primary-200 dark:hover:bg-primary-900/30 transition-colors"
                >
                  ✏️ 重新設定偏好
                </button>
                <button
                  onClick={handleSaveItinerary}
                  className="w-full text-left px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 text-sm rounded-lg transition-colors"
                >
                  💾 儲存行程
                </button>
                <button
                  onClick={handleDownloadItinerary}
                  className="w-full text-left px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 text-sm rounded-lg transition-colors"
                >
                  📄 下載行程
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 中間：對話面板 */}
        <div className="flex-1 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700">
          <UnifiedChatPanel
            sessionId={`unified_${Date.now()}`}
            onItineraryGenerated={(itinerary) => {
              setItinerary(itinerary);
              console.log('Generated itinerary:', itinerary);
            }}
            onError={(error) => {
              console.error('Chat error:', error);
            }}
            className="h-full"
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