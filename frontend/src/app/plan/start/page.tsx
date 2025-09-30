"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Input, Card } from "@/components/ui";
import { AppLayout } from "@/components/layout";

export default function PlanningStartPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    destination: "",
    startDate: "",
    days: 1,
    travelers: 1,
    interests: [] as string[],
    budget: "medium",
    pace: "moderate"
  });

  const interestOptions = [
    { id: "food", label: "美食", icon: "🍽️" },
    { id: "nature", label: "自然景觀", icon: "🌲" },
    { id: "culture", label: "文化歷史", icon: "🏛️" },
    { id: "shopping", label: "購物", icon: "🛍️" },
    { id: "adventure", label: "冒險活動", icon: "🏔️" },
    { id: "relaxation", label: "放鬆休閒", icon: "🏖️" }
  ];

  const budgetOptions = [
    { id: "budget", label: "經濟型", description: "每日預算 < $50", icon: "💰" },
    { id: "medium", label: "中等", description: "每日預算 $50-150", icon: "💳" },
    { id: "luxury", label: "豪華型", description: "每日預算 > $150", icon: "💎" }
  ];

  const paceOptions = [
    { id: "relaxed", label: "悠閒", description: "每天 2-3 個景點", icon: "🐌" },
    { id: "moderate", label: "適中", description: "每天 4-5 個景點", icon: "🚶" },
    { id: "intensive", label: "緊湊", description: "每天 6+ 個景點", icon: "🏃" }
  ];

  const handleInterestChange = (interestId: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interestId)
        ? prev.interests.filter(id => id !== interestId)
        : [...prev.interests, interestId]
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 儲存表單資料到 localStorage 或狀態管理
    localStorage.setItem("planningForm", JSON.stringify(formData));
    router.push("/plan/result");
  };

  return (
    <AppLayout showFooter={false}>

      {/* 主要內容 */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* 標題區域 */}
        <div className="text-center mb-12">
          <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 dark:text-white mb-4">
            開始規劃您的旅程
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            告訴我們您的需求，AI 將為您量身打造完美行程
          </p>
        </div>

        {/* 進度指示器 */}
        <div className="flex items-center justify-center mb-12">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                1
              </div>
              <span className="text-sm font-medium text-slate-900 dark:text-white">基本資料</span>
            </div>
            <div className="w-16 h-1 bg-slate-300 dark:bg-slate-600 rounded-full"></div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-slate-300 dark:bg-slate-600 text-slate-600 dark:text-slate-300 rounded-full flex items-center justify-center text-sm font-medium">
                2
              </div>
              <span className="text-sm text-slate-500 dark:text-slate-400">生成行程</span>
            </div>
          </div>
        </div>

        {/* 表單區域 */}
        <div className="grid xl:grid-cols-4 gap-12">
          {/* 左側：表單 */}
          <div className="xl:col-span-3">
            <Card className="p-8">
              <form onSubmit={handleSubmit} className="space-y-8">
                {/* 基本資訊 */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white border-b border-slate-200 dark:border-slate-700 pb-3">
                    基本資訊
                  </h3>
                  
                  <div className="grid lg:grid-cols-2 xl:grid-cols-4 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        目的地
                      </label>
                      <Input
                        type="text"
                        placeholder="請輸入城市或景點名稱"
                        value={formData.destination}
                        onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        出發日期
                      </label>
                      <Input
                        type="date"
                        value={formData.startDate}
                        onChange={(e) => setFormData(prev => ({ ...prev, startDate: e.target.value }))}
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        旅遊天數
                      </label>
                      <select
                        className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        value={formData.days}
                        onChange={(e) => setFormData(prev => ({ ...prev, days: parseInt(e.target.value) }))}
                      >
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(day => (
                          <option key={day} value={day}>{day} 天</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        旅遊人數
                      </label>
                      <select
                        className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        value={formData.travelers}
                        onChange={(e) => setFormData(prev => ({ ...prev, travelers: parseInt(e.target.value) }))}
                      >
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                          <option key={num} value={num}>{num} 人</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* 興趣偏好 */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white border-b border-slate-200 dark:border-slate-700 pb-3">
                    興趣偏好
                  </h3>
                  <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {interestOptions.map(option => (
                      <label key={option.id} className="flex items-center space-x-3 cursor-pointer p-4 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-primary-300 dark:hover:border-primary-600 transition-all">
                        <input
                          type="checkbox"
                          checked={formData.interests.includes(option.id)}
                          onChange={() => handleInterestChange(option.id)}
                          className="w-4 h-4 text-primary-600 border-slate-300 rounded focus:ring-primary-500"
                        />
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{option.icon}</span>
                          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {option.label}
                          </span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* 預算等級 */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white border-b border-slate-200 dark:border-slate-700 pb-3">
                    預算等級
                  </h3>
                  <div className="grid lg:grid-cols-3 gap-4">
                    {budgetOptions.map(option => (
                      <label key={option.id} className="flex items-center space-x-3 cursor-pointer p-4 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-primary-300 dark:hover:border-primary-600 transition-all">
                        <input
                          type="radio"
                          name="budget"
                          value={option.id}
                          checked={formData.budget === option.id}
                          onChange={(e) => setFormData(prev => ({ ...prev, budget: e.target.value }))}
                          className="w-4 h-4 text-primary-600"
                        />
                        <div className="flex items-center space-x-3">
                          <span className="text-xl">{option.icon}</span>
                          <div>
                            <div className="text-sm font-medium text-slate-900 dark:text-white">{option.label}</div>
                            <div className="text-xs text-slate-500 dark:text-slate-400">{option.description}</div>
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* 旅遊節奏 */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-white border-b border-slate-200 dark:border-slate-700 pb-3">
                    旅遊節奏
                  </h3>
                  <div className="grid lg:grid-cols-3 gap-4">
                    {paceOptions.map(option => (
                      <label key={option.id} className="flex items-center space-x-3 cursor-pointer p-4 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-primary-300 dark:hover:border-primary-600 transition-all">
                        <input
                          type="radio"
                          name="pace"
                          value={option.id}
                          checked={formData.pace === option.id}
                          onChange={(e) => setFormData(prev => ({ ...prev, pace: e.target.value }))}
                          className="w-4 h-4 text-primary-600"
                        />
                        <div className="flex items-center space-x-3">
                          <span className="text-xl">{option.icon}</span>
                          <div>
                            <div className="text-sm font-medium text-slate-900 dark:text-white">{option.label}</div>
                            <div className="text-xs text-slate-500 dark:text-slate-400">{option.description}</div>
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* 提交按鈕 */}
                <div className="pt-6">
                  <Button type="submit" size="lg" className="w-full">
                    生成我的行程
                  </Button>
                </div>
              </form>
            </Card>
          </div>

          {/* 右側：預覽/提示 */}
          <div className="xl:col-span-1">
            <div className="sticky top-8">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                  行程預覽
                </h3>
                
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-sm text-slate-600 dark:text-slate-400 mb-2">目的地</div>
                    <div className="text-sm font-medium text-slate-900 dark:text-white">
                      {formData.destination || "請輸入目的地"}
                    </div>
                  </div>
                  
                  <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-sm text-slate-600 dark:text-slate-400 mb-2">行程天數</div>
                    <div className="text-sm font-medium text-slate-900 dark:text-white">
                      {formData.days} 天
                    </div>
                  </div>
                  
                  <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-sm text-slate-600 dark:text-slate-400 mb-2">旅遊人數</div>
                    <div className="text-sm font-medium text-slate-900 dark:text-white">
                      {formData.travelers} 人
                    </div>
                  </div>
                  
                  <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-sm text-slate-600 dark:text-slate-400 mb-2">興趣偏好</div>
                    <div className="text-sm font-medium text-slate-900 dark:text-white">
                      {formData.interests.length > 0 
                        ? formData.interests.map(id => 
                            interestOptions.find(opt => opt.id === id)?.label
                          ).join(", ")
                        : "請選擇興趣偏好"
                      }
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                  <div className="flex items-center space-x-2 mb-3">
                    <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium text-primary-900 dark:text-primary-100">提示</span>
                  </div>
                  <p className="text-sm text-primary-700 dark:text-primary-200 leading-relaxed">
                    填寫完基本資料後，AI 將根據您的偏好生成個人化行程，您可以在下一步中進行調整。
                  </p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
