"use client";

import { useState } from "react";
import { TripCard } from "./TripCard";
import { EmptyState } from "./EmptyState";
import { Pagination } from "@/components/ui/Pagination";
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

interface TripListProps {
  trips: TripSummary[];
  loading?: boolean;
  currentPage?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onViewTrip?: (tripId: string) => void;
  onEditTrip?: (tripId: string) => void;
  onShareTrip?: (tripId: string) => void;
  onDeleteTrip?: (tripId: string) => void;
  onCreateTrip?: () => void;
}

export function TripList({
  trips,
  loading = false,
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  onViewTrip,
  onEditTrip,
  onShareTrip,
  onDeleteTrip,
  onCreateTrip
}: TripListProps) {
  const [sortBy, setSortBy] = useState<'created_at' | 'updated_at' | 'start_date' | 'title'>('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterPublic, setFilterPublic] = useState<'all' | 'public' | 'private'>('all');

  // 篩選和排序
  const filteredTrips = trips
    .filter(trip => {
      if (filterPublic === 'public') return trip.is_public;
      if (filterPublic === 'private') return !trip.is_public;
      return true;
    })
    .sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'start_date':
          aValue = new Date(a.start_date);
          bValue = new Date(b.start_date);
          break;
        case 'created_at':
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          break;
        case 'updated_at':
        default:
          aValue = new Date(a.updated_at);
          bValue = new Date(b.updated_at);
          break;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  if (loading) {
    return (
      <div className="space-y-6">
        {/* 載入中的骨架 */}
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white dark:bg-slate-800 rounded-xl p-6 animate-pulse">
            <div className="space-y-4">
              <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded"></div>
                <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (filteredTrips.length === 0) {
    return (
      <EmptyState
        title="還沒有任何行程"
        description="開始規劃您的第一個旅程，或從現有的規劃結果中儲存行程"
        actionText="開始規劃行程"
        onAction={onCreateTrip}
        icon={
          <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* 篩選和排序控制 */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between bg-white dark:bg-slate-800 rounded-xl p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          {/* 排序 */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
              排序：
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-1 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white text-sm"
            >
              <option value="updated_at">最近更新</option>
              <option value="created_at">建立時間</option>
              <option value="start_date">出發日期</option>
              <option value="title">標題</option>
            </select>
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded"
            >
              <svg className={`w-4 h-4 transition-transform ${sortOrder === 'desc' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
              </svg>
            </button>
          </div>

          {/* 篩選 */}
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
              篩選：
            </label>
            <select
              value={filterPublic}
              onChange={(e) => setFilterPublic(e.target.value as any)}
              className="px-3 py-1 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white text-sm"
            >
              <option value="all">全部</option>
              <option value="public">公開</option>
              <option value="private">私人</option>
            </select>
          </div>
        </div>

        {/* 統計資訊 */}
        <div className="text-sm text-slate-600 dark:text-slate-300">
          共 {filteredTrips.length} 個行程
        </div>
      </div>

      {/* 行程列表 */}
      <div className="grid gap-6">
        {filteredTrips.map((trip) => (
          <TripCard
            key={trip.id}
            trip={trip}
            onView={() => onViewTrip?.(trip.id)}
            onEdit={() => onEditTrip?.(trip.id)}
            onShare={() => onShareTrip?.(trip.id)}
            onDelete={() => onDeleteTrip?.(trip.id)}
          />
        ))}
      </div>

      {/* 分頁 */}
      {totalPages > 1 && onPageChange && (
        <div className="flex justify-center pt-6">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={onPageChange}
          />
        </div>
      )}
    </div>
  );
}
