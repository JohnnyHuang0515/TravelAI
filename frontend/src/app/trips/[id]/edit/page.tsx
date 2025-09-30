"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { TripTimeline } from "@/components/trip/TripTimeline";
import { Modal } from "@/components/ui";
import { Button } from "@/components/ui";
import { Input } from "@/components/ui";
import { Trip } from "@/lib/types/trip";

export default function EditTripPage() {
  const params = useParams();
  const router = useRouter();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingTitle, setEditingTitle] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{type: 'user' | 'ai', message: string}>>([]);

  useEffect(() => {
    loadTrip();
  }, [params.id]);

  const loadTrip = async () => {
    try {
      setLoading(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模擬行程資料
      const mockTrip: Trip = {
        id: params.id as string,
        user_id: "user123",
        title: "台北三日遊",
        description: "探索台北的經典景點，品嚐道地美食，體驗台灣文化",
        destination: "台北市",
        duration_days: 3,
        start_date: "2024-02-15",
        end_date: "2024-02-17",
        is_public: true,
        share_token: "abc123def456",
        view_count: 25,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-20T15:30:00Z",
        itinerary_data: {
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
                }
              ],
              accommodation: {
                name: "台北君悅酒店",
                address: "台北市信義區松仁路100號",
                rating: 4.5,
                price: 8000
              }
            }
          ]
        }
      };

      setTrip(mockTrip);
      setTitle(mockTrip.title);
      setDescription(mockTrip.description || '');
    } catch (error) {
      console.error("載入行程失敗:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert("行程已儲存！");
      router.push(`/trips/${params.id}`);
    } catch (error) {
      console.error("儲存失敗:", error);
      alert("儲存失敗，請稍後再試");
    } finally {
      setSaving(false);
    }
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    // 新增使用者訊息
    const userMessage = { type: 'user' as const, message: chatMessage };
    setChatHistory(prev => [...prev, userMessage]);

    // 模擬 AI 回應
    setTimeout(() => {
      const aiMessage = { type: 'ai' as const, message: "我了解您的需求，正在為您調整行程..." };
      setChatHistory(prev => [...prev, aiMessage]);
    }, 1000);

    setChatMessage("");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-slate-600 dark:text-slate-300">載入行程中...</p>
        </div>
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-slate-600 dark:text-slate-300">找不到此行程</p>
          <Button onClick={() => router.push('/trips')} className="mt-4">
            返回行程列表
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* 頁面標題和操作 */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex-1">
            {editingTitle ? (
              <div className="flex items-center space-x-3">
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-2xl font-bold"
                  onBlur={() => setEditingTitle(false)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      setEditingTitle(false);
                    }
                  }}
                  autoFocus
                />
              </div>
            ) : (
              <h1 
                className="text-3xl font-bold text-slate-900 dark:text-white cursor-pointer hover:text-primary-600 transition-colors"
                onClick={() => setEditingTitle(true)}
              >
                {title}
                <svg className="w-5 h-5 inline ml-2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </h1>
            )}
            <p className="text-slate-600 dark:text-slate-300 mt-2">
              {trip.destination} • {trip.duration_days} 天
            </p>
          </div>
          
          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => router.push(`/trips/${params.id}`)}
            >
              取消
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? '儲存中...' : '儲存變更'}
            </Button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* 左側：行程編輯 */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
              {/* 描述編輯 */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  行程描述
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="描述這個行程的特色和重點..."
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white resize-none"
                  rows={3}
                />
              </div>

              {/* 行程時間軸 */}
              <TripTimeline 
                days={trip.itinerary_data.days}
                editable={true}
                onModify={(dayIndex, visitIndex) => {
                  console.log(`修改第 ${dayIndex + 1} 天第 ${visitIndex + 1} 個景點`);
                  // 這裡可以開啟景點編輯模態框
                }}
              />
            </div>
          </div>

          {/* 右側：對話修改介面 */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 h-fit">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                對話修改行程
              </h2>
              
              {/* 對話歷史 */}
              <div className="h-64 overflow-y-auto mb-4 space-y-3 custom-scrollbar">
                {chatHistory.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      開始對話來修改您的行程
                    </p>
                  </div>
                ) : (
                  chatHistory.map((chat, index) => (
                    <div key={index} className={`flex ${chat.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                        chat.type === 'user' 
                          ? 'bg-primary-500 text-white' 
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white'
                      }`}>
                        {chat.message}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* 輸入框 */}
              <form onSubmit={handleChatSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="例如：我想增加一個美食景點"
                  className="flex-1 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <Button type="submit" size="sm">
                  發送
                </Button>
              </form>

              <div className="mt-4 text-xs text-slate-500 dark:text-slate-400">
                💡 提示：您可以要求調整景點、時間或增加新的活動
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
