"use client";

import { useState } from "react";
import { Card } from "@/components/ui";
import { Button } from "@/components/ui";

interface ItineraryPanelProps {
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
  } | null;
  isLoading?: boolean;
  onSaveItinerary?: () => void;
  onDownloadItinerary?: () => void;
}

export function ItineraryPanel({ 
  itinerary, 
  isLoading = false, 
  onSaveItinerary, 
  onDownloadItinerary 
}: ItineraryPanelProps) {
  const [expandedDay, setExpandedDay] = useState<number | null>(null);

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('zh-TW', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      month: 'short',
      day: 'numeric',
      weekday: 'short'
    });
  };

  if (isLoading) {
    return (
      <div className="h-full flex flex-col bg-white dark:bg-slate-800">
        {/* 標題列 */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            行程規劃
          </h2>
        </div>

        {/* 載入中內容 */}
        <div className="flex-1 p-4">
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-1/3 mb-3"></div>
                <div className="space-y-2">
                  <div className="h-16 bg-slate-200 dark:bg-slate-700 rounded"></div>
                  <div className="h-16 bg-slate-200 dark:bg-slate-700 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="h-full flex flex-col bg-white dark:bg-slate-800">
        {/* 標題列 */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            行程規劃
          </h2>
        </div>

        {/* 空狀態 */}
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-sm font-medium text-slate-900 dark:text-white mb-2">
              等待行程生成
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              設定您的偏好後，AI 將為您生成個人化行程
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-slate-800">
      {/* 標題列 */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            行程規劃
          </h2>
          <div className="flex space-x-2">
            {onSaveItinerary && (
              <Button size="sm" variant="outline" onClick={onSaveItinerary}>
                儲存
              </Button>
            )}
            {onDownloadItinerary && (
              <Button size="sm" variant="outline" onClick={onDownloadItinerary}>
                下載
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* 行程內容 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {itinerary.days.map((day) => (
          <Card key={day.day} className="p-4">
            {/* 日期標題 */}
            <button
              onClick={() => setExpandedDay(expandedDay === day.day ? null : day.day)}
              className="w-full flex items-center justify-between mb-3"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center text-sm font-medium">
                  {day.day}
                </div>
                <div className="text-left">
                  <div className="text-sm font-medium text-slate-900 dark:text-white">
                    第 {day.day} 天
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    {formatDate(day.date)}
                  </div>
                </div>
              </div>
              <svg 
                className={`w-4 h-4 text-slate-400 transition-transform ${
                  expandedDay === day.day ? 'rotate-180' : ''
                }`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* 行程詳情 */}
            {expandedDay === day.day && (
              <div className="space-y-3">
                {/* 景點列表 */}
                {day.visits.map((visit, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    {/* 時間點 */}
                    <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    
                    {/* 景點資訊 */}
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                        {visit.name}
                      </h4>
                      <div className="flex items-center space-x-4 text-xs text-slate-500 dark:text-slate-400">
                        <span>到達: {formatTime(visit.eta)}</span>
                        <span>離開: {formatTime(visit.etd)}</span>
                        <span>停留: {visit.stay_minutes} 分鐘</span>
                        {visit.travel_minutes > 0 && (
                          <span>交通: {visit.travel_minutes} 分鐘</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* 住宿資訊 */}
                {day.accommodation && (
                  <div className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 21v-4a2 2 0 012-2h4a2 2 0 012 2v4" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                        {day.accommodation.name}
                      </h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">
                        {day.accommodation.address}
                      </p>
                      <div className="flex items-center space-x-3 text-xs text-slate-500 dark:text-slate-400">
                        <div className="flex items-center space-x-1">
                          <svg className="w-3 h-3 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span>{day.accommodation.rating}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                          </svg>
                          <span>NT$ {day.accommodation.price}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
