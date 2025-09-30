"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui";
import { Card } from "@/components/ui";

interface UserPreference {
  favorite_themes: string[];
  travel_pace: 'relaxed' | 'moderate' | 'packed';
  budget_level: 'budget' | 'moderate' | 'luxury';
  default_daily_start: string;
  default_daily_end: string;
}

const themeOptions = [
  { id: 'food', label: '美食', icon: '🍽️' },
  { id: 'nature', label: '自然景觀', icon: '🌲' },
  { id: 'culture', label: '文化歷史', icon: '🏛️' },
  { id: 'shopping', label: '購物', icon: '🛍️' },
  { id: 'adventure', label: '冒險活動', icon: '🏔️' },
  { id: 'relaxation', label: '放鬆休閒', icon: '🏖️' },
  { id: 'nightlife', label: '夜生活', icon: '🌃' },
  { id: 'family', label: '親子活動', icon: '👨‍👩‍👧‍👦' }
];

const paceOptions = [
  { 
    id: 'relaxed', 
    label: '悠閒', 
    description: '每天 2-3 個景點，有充足的休息時間',
    icon: '🐌'
  },
  { 
    id: 'moderate', 
    label: '適中', 
    description: '每天 4-5 個景點，平衡的行程安排',
    icon: '🚶'
  },
  { 
    id: 'packed', 
    label: '緊湊', 
    description: '每天 6+ 個景點，充分利用時間',
    icon: '🏃'
  }
];

const budgetOptions = [
  { 
    id: 'budget', 
    label: '經濟型', 
    description: '每日預算 < $50',
    icon: '💰'
  },
  { 
    id: 'moderate', 
    label: '中等', 
    description: '每日預算 $50-150',
    icon: '💳'
  },
  { 
    id: 'luxury', 
    label: '豪華型', 
    description: '每日預算 > $150',
    icon: '💎'
  }
];

export default function PreferencesPage() {
  const router = useRouter();
  const [preferences, setPreferences] = useState<UserPreference>({
    favorite_themes: [],
    travel_pace: 'moderate',
    budget_level: 'moderate',
    default_daily_start: '09:00',
    default_daily_end: '18:00'
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 模擬使用者偏好資料
      const mockPreferences: UserPreference = {
        favorite_themes: ['food', 'culture', 'nature'],
        travel_pace: 'moderate',
        budget_level: 'moderate',
        default_daily_start: '09:00',
        default_daily_end: '18:00'
      };

      setPreferences(mockPreferences);
    } catch (error) {
      console.error("載入偏好設定失敗:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleThemeChange = (themeId: string) => {
    setPreferences(prev => ({
      ...prev,
      favorite_themes: prev.favorite_themes.includes(themeId)
        ? prev.favorite_themes.filter(id => id !== themeId)
        : [...prev.favorite_themes, themeId]
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      alert("偏好設定已儲存！");
    } catch (error) {
      console.error("儲存失敗:", error);
      alert("儲存失敗，請稍後再試");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-slate-600 dark:text-slate-300">載入偏好設定中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* 頁面標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            偏好設定
          </h1>
          <p className="text-slate-600 dark:text-slate-300">
            設定您的旅遊偏好，讓我們為您推薦更符合需求的行程
          </p>
        </div>

        <div className="space-y-6">
          {/* 興趣主題 */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
              興趣主題
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-6">
              選擇您感興趣的主題，我們會優先推薦相關景點
            </p>
            
            <div className="grid grid-cols-4 gap-3">
              {themeOptions.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => handleThemeChange(theme.id)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    preferences.favorite_themes.includes(theme.id)
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-2xl mb-2">{theme.icon}</div>
                    <div className="text-sm font-medium text-slate-900 dark:text-white">
                      {theme.label}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* 旅遊節奏 */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
              旅遊節奏
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-6">
              選擇您偏好的行程安排節奏
            </p>
            
            <div className="space-y-3">
              {paceOptions.map((pace) => (
                <label
                  key={pace.id}
                  className={`flex items-start space-x-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    preferences.travel_pace === pace.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
                >
                  <input
                    type="radio"
                    name="travel_pace"
                    value={pace.id}
                    checked={preferences.travel_pace === pace.id}
                    onChange={(e) => setPreferences(prev => ({ ...prev, travel_pace: e.target.value as any }))}
                    className="w-4 h-4 text-primary-600 mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-lg">{pace.icon}</span>
                      <span className="font-medium text-slate-900 dark:text-white">
                        {pace.label}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300">
                      {pace.description}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          </Card>

          {/* 預算等級 */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
              預算等級
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-6">
              選擇您的預算範圍，我們會推薦適合的景點和住宿
            </p>
            
            <div className="space-y-3">
              {budgetOptions.map((budget) => (
                <label
                  key={budget.id}
                  className={`flex items-start space-x-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    preferences.budget_level === budget.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
                >
                  <input
                    type="radio"
                    name="budget_level"
                    value={budget.id}
                    checked={preferences.budget_level === budget.id}
                    onChange={(e) => setPreferences(prev => ({ ...prev, budget_level: e.target.value as any }))}
                    className="w-4 h-4 text-primary-600 mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-lg">{budget.icon}</span>
                      <span className="font-medium text-slate-900 dark:text-white">
                        {budget.label}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-300">
                      {budget.description}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          </Card>

          {/* 預設時間 */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
              預設時間設定
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-6">
              設定每日行程的開始和結束時間
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  每日開始時間
                </label>
                <input
                  type="time"
                  value={preferences.default_daily_start}
                  onChange={(e) => setPreferences(prev => ({ ...prev, default_daily_start: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  每日結束時間
                </label>
                <input
                  type="time"
                  value={preferences.default_daily_end}
                  onChange={(e) => setPreferences(prev => ({ ...prev, default_daily_end: e.target.value }))}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
                />
              </div>
            </div>
          </Card>

          {/* 儲存按鈕 */}
          <div className="flex justify-end space-x-4">
            <Button
              variant="outline"
              onClick={() => router.back()}
            >
              取消
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? '儲存中...' : '儲存設定'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
