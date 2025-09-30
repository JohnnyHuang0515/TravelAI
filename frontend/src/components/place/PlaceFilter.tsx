"use client";

import { useState } from "react";
import { Button } from "@/components/ui";
import { PlaceFilter as FilterType } from "@/lib/types/place";

interface PlaceFilterProps {
  filters: FilterType;
  onChange: (filters: FilterType) => void;
}

const categoryOptions = [
  { id: 'food', label: '美食', icon: '🍽️' },
  { id: 'nature', label: '自然景觀', icon: '🌲' },
  { id: 'culture', label: '文化歷史', icon: '🏛️' },
  { id: 'shopping', label: '購物', icon: '🛍️' },
  { id: 'entertainment', label: '娛樂', icon: '🎭' },
  { id: 'accommodation', label: '住宿', icon: '🏨' },
  { id: 'transport', label: '交通', icon: '🚗' },
  { id: 'health', label: '健康', icon: '🏥' }
];

export function PlaceFilter({ filters, onChange }: PlaceFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCategoryChange = (categoryId: string) => {
    const newCategories = filters.categories.includes(categoryId)
      ? filters.categories.filter(id => id !== categoryId)
      : [...filters.categories, categoryId];
    
    onChange({
      ...filters,
      categories: newCategories
    });
  };

  const handleRadiusChange = (radius: number) => {
    onChange({
      ...filters,
      radius
    });
  };

  const handleRatingChange = (minRating: number) => {
    onChange({
      ...filters,
      min_rating: minRating
    });
  };

  const handleSortChange = (sortBy: FilterType['sort_by']) => {
    onChange({
      ...filters,
      sort_by: sortBy
    });
  };

  const resetFilters = () => {
    onChange({
      categories: [],
      radius: 5000,
      min_rating: 0,
      max_price: null,
      sort_by: 'distance',
      sort_order: 'asc'
    });
  };

  const hasActiveFilters = filters.categories.length > 0 || 
                          filters.radius !== 5000 || 
                          filters.min_rating > 0;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-4 space-y-4">
      {/* 標題和展開按鈕 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          篩選條件
        </h3>
        <div className="flex items-center space-x-2">
          {hasActiveFilters && (
            <Button
              size="sm"
              variant="outline"
              onClick={resetFilters}
              className="text-xs"
            >
              清除
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs"
          >
            {isExpanded ? '收起' : '展開'}
          </Button>
        </div>
      </div>

      {/* 快速篩選 */}
      <div className="space-y-3">
        {/* 類別篩選 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            類別
          </label>
          <div className="grid grid-cols-4 gap-2">
            {categoryOptions.map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategoryChange(category.id)}
                className={`p-2 rounded-lg text-xs transition-colors ${
                  filters.categories.includes(category.id)
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 border border-primary-300 dark:border-primary-700'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                <div className="text-center">
                  <div className="text-sm mb-1">{category.icon}</div>
                  <div>{category.label}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 展開的篩選選項 */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            {/* 距離範圍 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                搜尋範圍: {filters.radius < 1000 ? `${filters.radius}m` : `${(filters.radius / 1000).toFixed(1)}km`}
              </label>
              <input
                type="range"
                min="500"
                max="20000"
                step="500"
                value={filters.radius}
                onChange={(e) => handleRadiusChange(Number(e.target.value))}
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1">
                <span>500m</span>
                <span>20km</span>
              </div>
            </div>

            {/* 最低評分 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                最低評分: {filters.min_rating > 0 ? `${filters.min_rating}+` : '不限'}
              </label>
              <div className="flex space-x-2">
                {[0, 3, 4, 4.5].map((rating) => (
                  <button
                    key={rating}
                    onClick={() => handleRatingChange(rating)}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      filters.min_rating === rating
                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    {rating === 0 ? '不限' : `${rating}+`}
                  </button>
                ))}
              </div>
            </div>

            {/* 排序方式 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                排序方式
              </label>
              <div className="flex space-x-2">
                {[
                  { value: 'distance', label: '距離' },
                  { value: 'rating', label: '評分' },
                  { value: 'name', label: '名稱' }
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSortChange(option.value as FilterType['sort_by'])}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      filters.sort_by === option.value
                        ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 篩選結果統計 */}
      {hasActiveFilters && (
        <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
          <div className="flex flex-wrap gap-2">
            {filters.categories.length > 0 && (
              <span className="bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-2 py-1 rounded text-xs">
                {filters.categories.length} 個類別
              </span>
            )}
            {filters.radius !== 5000 && (
              <span className="bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-2 py-1 rounded text-xs">
                範圍 {filters.radius < 1000 ? `${filters.radius}m` : `${(filters.radius / 1000).toFixed(1)}km`}
              </span>
            )}
            {filters.min_rating > 0 && (
              <span className="bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-2 py-1 rounded text-xs">
                評分 {filters.min_rating}+
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
