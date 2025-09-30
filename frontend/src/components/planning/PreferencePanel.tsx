"use client";

import { useState } from "react";
import { Card } from "@/components/ui";
import { Button } from "@/components/ui";

interface PreferencePanelProps {
  preferences: {
    destination: string;
    startDate: string;
    endDate: string;
    duration: number;
    interests: string[];
    budget: string;
    pace: string;
  };
  onPreferenceChange: (key: string, value: any) => void;
  onGenerateItinerary: () => void;
}

const interestTags = [
  { id: 'food', label: '美食', icon: '🍽️', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' },
  { id: 'nature', label: '自然景觀', icon: '🌲', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
  { id: 'culture', label: '文化歷史', icon: '🏛️', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
  { id: 'shopping', label: '購物', icon: '🛍️', color: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200' },
  { id: 'adventure', label: '冒險活動', icon: '🏔️', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
  { id: 'relaxation', label: '放鬆休閒', icon: '🏖️', color: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200' },
  { id: 'nightlife', label: '夜生活', icon: '🌃', color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200' },
  { id: 'family', label: '親子活動', icon: '👨‍👩‍👧‍👦', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' }
];

const budgetOptions = [
  { id: 'budget', label: '經濟型', description: '每日 < $50' },
  { id: 'moderate', label: '中等', description: '每日 $50-150' },
  { id: 'luxury', label: '豪華型', description: '每日 > $150' }
];

const paceOptions = [
  { id: 'relaxed', label: '悠閒', description: '每天 2-3 個景點' },
  { id: 'moderate', label: '適中', description: '每天 4-5 個景點' },
  { id: 'packed', label: '緊湊', description: '每天 6+ 個景點' }
];

export function PreferencePanel({ preferences, onPreferenceChange, onGenerateItinerary }: PreferencePanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleInterestToggle = (interestId: string) => {
    const newInterests = preferences.interests.includes(interestId)
      ? preferences.interests.filter(id => id !== interestId)
      : [...preferences.interests, interestId];
    onPreferenceChange('interests', newInterests);
  };

  return (
    <div className="h-full flex flex-col">
      {/* 標題列 */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          旅遊偏好設定
        </h2>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded"
        >
          <svg className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* 內容區域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {isExpanded && (
          <>
            {/* 基本資訊 */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">基本資訊</h3>
              
              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  目的地
                </label>
                <input
                  type="text"
                  value={preferences.destination}
                  onChange={(e) => onPreferenceChange('destination', e.target.value)}
                  placeholder="請輸入目的地"
                  className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                    出發日期
                  </label>
                  <input
                    type="date"
                    value={preferences.startDate}
                    onChange={(e) => onPreferenceChange('startDate', e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                    結束日期
                  </label>
                  <input
                    type="date"
                    value={preferences.endDate}
                    onChange={(e) => onPreferenceChange('endDate', e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  天數
                </label>
                <select
                  value={preferences.duration}
                  onChange={(e) => onPreferenceChange('duration', parseInt(e.target.value))}
                  className="w-full px-3 py-2 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(days => (
                    <option key={days} value={days}>{days} 天</option>
                  ))}
                </select>
              </div>
            </div>

            {/* 興趣標籤 */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">興趣標籤</h3>
              <div className="grid grid-cols-2 gap-2">
                {interestTags.map((tag) => (
                  <button
                    key={tag.id}
                    onClick={() => handleInterestToggle(tag.id)}
                    className={`p-2 rounded-lg text-xs font-medium transition-all ${
                      preferences.interests.includes(tag.id)
                        ? `${tag.color} ring-2 ring-primary-500`
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    <div className="flex items-center space-x-1">
                      <span>{tag.icon}</span>
                      <span>{tag.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* 預算等級 */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">預算等級</h3>
              <div className="space-y-2">
                {budgetOptions.map((option) => (
                  <label
                    key={option.id}
                    className={`flex items-center space-x-3 p-2 rounded-lg cursor-pointer transition-colors ${
                      preferences.budget === option.id
                        ? 'bg-primary-50 dark:bg-primary-900/20 border border-primary-300 dark:border-primary-700'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="budget"
                      value={option.id}
                      checked={preferences.budget === option.id}
                      onChange={(e) => onPreferenceChange('budget', e.target.value)}
                      className="w-3 h-3 text-primary-600"
                    />
                    <div className="flex-1">
                      <div className="text-xs font-medium text-slate-900 dark:text-white">
                        {option.label}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {option.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* 旅遊節奏 */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300">旅遊節奏</h3>
              <div className="space-y-2">
                {paceOptions.map((option) => (
                  <label
                    key={option.id}
                    className={`flex items-center space-x-3 p-2 rounded-lg cursor-pointer transition-colors ${
                      preferences.pace === option.id
                        ? 'bg-primary-50 dark:bg-primary-900/20 border border-primary-300 dark:border-primary-700'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-700'
                    }`}
                  >
                    <input
                      type="radio"
                      name="pace"
                      value={option.id}
                      checked={preferences.pace === option.id}
                      onChange={(e) => onPreferenceChange('pace', e.target.value)}
                      className="w-3 h-3 text-primary-600"
                    />
                    <div className="flex-1">
                      <div className="text-xs font-medium text-slate-900 dark:text-white">
                        {option.label}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {option.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* 底部操作 */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        <Button
          onClick={onGenerateItinerary}
          className="w-full"
          size="sm"
        >
          生成行程
        </Button>
      </div>
    </div>
  );
}
