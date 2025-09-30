"use client";

import { useState } from "react";
import { Card } from "@/components/ui";
import { Button } from "@/components/ui";

interface TripSummary {
  id: string;
  title: string;
  description: string | null;
  destination: string;
  duration_days: number;
  start_date: string;
  end_date: string;
  is_public: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
}

interface TripCardProps {
  trip: TripSummary;
  onView?: () => void;
  onEdit?: () => void;
  onShare?: () => void;
  onDelete?: () => void;
}

export function TripCard({ trip, onView, onEdit, onShare, onDelete }: TripCardProps) {
  const [showActions, setShowActions] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getDaysAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '昨天';
    if (diffDays < 7) return `${diffDays} 天前`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} 週前`;
    return `${Math.ceil(diffDays / 30)} 個月前`;
  };

  return (
    <Card className="p-6 hover:shadow-lg transition-all duration-300 cursor-pointer group">
      <div 
        className="space-y-4"
        onMouseEnter={() => setShowActions(true)}
        onMouseLeave={() => setShowActions(false)}
      >
        {/* 標題和狀態 */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-1 group-hover:text-primary-600 transition-colors">
              {trip.title}
            </h3>
            {trip.description && (
              <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2">
                {trip.description}
              </p>
            )}
          </div>
          
          {/* 公開狀態標籤 */}
          {trip.is_public && (
            <span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full text-xs font-medium">
              公開
            </span>
          )}
        </div>

        {/* 行程資訊 */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-slate-600 dark:text-slate-300">{trip.destination}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-slate-600 dark:text-slate-300">{trip.duration_days} 天</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-slate-600 dark:text-slate-300">
              {formatDate(trip.start_date)} - {formatDate(trip.end_date)}
            </span>
          </div>
          
          {trip.is_public && (
            <div className="flex items-center space-x-2">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span className="text-slate-600 dark:text-slate-300">{trip.view_count} 次瀏覽</span>
            </div>
          )}
        </div>

        {/* 時間戳記 */}
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>建立於 {getDaysAgo(trip.created_at)}</span>
          {trip.updated_at !== trip.created_at && (
            <span>更新於 {getDaysAgo(trip.updated_at)}</span>
          )}
        </div>

        {/* 操作按鈕 */}
        <div className={`flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700 transition-opacity duration-200 ${
          showActions ? 'opacity-100' : 'opacity-0'
        }`}>
          <div className="flex space-x-2">
            <Button 
              size="sm" 
              variant="outline"
              onClick={onView}
              className="text-xs"
            >
              查看
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={onEdit}
              className="text-xs"
            >
              編輯
            </Button>
          </div>
          
          <div className="flex space-x-2">
            <Button 
              size="sm" 
              variant="outline"
              onClick={onShare}
              className="text-xs"
            >
              分享
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={onDelete}
              className="text-xs text-red-600 hover:text-red-700 hover:border-red-300"
            >
              刪除
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}
