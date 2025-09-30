"use client";

import { useEffect, useRef, useState } from "react";
import { Place, UserLocation } from "@/lib/types/place";

interface PlaceMapProps {
  places: Place[];
  userLocation?: UserLocation;
  selectedPlaceId?: string;
  onPlaceClick?: (placeId: string) => void;
  className?: string;
}

export function PlaceMap({ 
  places, 
  userLocation, 
  selectedPlaceId, 
  onPlaceClick,
  className = "h-96 w-full"
}: PlaceMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    // 模擬地圖載入
    const timer = setTimeout(() => {
      setMapLoaded(true);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (!mapLoaded) {
    return (
      <div className={`${className} bg-slate-200 dark:bg-slate-700 rounded-lg flex items-center justify-center`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
          <p className="text-sm text-slate-600 dark:text-slate-300">載入地圖中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className} bg-slate-100 dark:bg-slate-800 rounded-lg relative overflow-hidden`}>
      {/* 模擬地圖背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20">
        {/* 模擬地圖網格 */}
        <div className="absolute inset-0 opacity-20">
          <svg width="100%" height="100%" className="text-slate-400">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {/* 使用者位置 */}
        {userLocation && (
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow-lg animate-pulse"></div>
            <div className="absolute -top-1 -left-1 w-6 h-6 bg-blue-500/20 rounded-full animate-ping"></div>
          </div>
        )}

        {/* 景點標記 */}
        {places.map((place, index) => {
          // 模擬位置分佈
          const angle = (index / places.length) * 2 * Math.PI;
          const radius = 80 + (index % 3) * 40;
          const x = 50 + Math.cos(angle) * radius;
          const y = 50 + Math.sin(angle) * radius;
          
          return (
            <div
              key={place.id}
              className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-200 ${
                selectedPlaceId === place.id ? 'scale-125 z-10' : 'hover:scale-110'
              }`}
              style={{
                left: `${x}%`,
                top: `${y}%`
              }}
              onClick={() => onPlaceClick?.(place.id)}
            >
              <div className={`w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-xs font-bold ${
                selectedPlaceId === place.id
                  ? 'bg-red-500 text-white'
                  : 'bg-primary-500 text-white'
              }`}>
                {index + 1}
              </div>
              
              {/* 景點資訊氣泡 */}
              {selectedPlaceId === place.id && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-white dark:bg-slate-800 rounded-lg shadow-lg p-2 min-w-[120px] border border-slate-200 dark:border-slate-700">
                  <div className="text-xs font-semibold text-slate-900 dark:text-white mb-1">
                    {place.name}
                  </div>
                  {place.rating && (
                    <div className="text-xs text-slate-600 dark:text-slate-300">
                      ⭐ {place.rating.toFixed(1)}
                    </div>
                  )}
                  {place.distance_meters && (
                    <div className="text-xs text-slate-600 dark:text-slate-300">
                      📍 {place.distance_meters < 1000 ? `${place.distance_meters}m` : `${(place.distance_meters / 1000).toFixed(1)}km`}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* 地圖控制按鈕 */}
        <div className="absolute top-4 right-4 space-y-2">
          <button className="w-8 h-8 bg-white dark:bg-slate-800 rounded-lg shadow-lg flex items-center justify-center hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
            <svg className="w-4 h-4 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <button className="w-8 h-8 bg-white dark:bg-slate-800 rounded-lg shadow-lg flex items-center justify-center hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
            <svg className="w-4 h-4 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4m16 0l-4-4m4 4l-4 4" />
            </svg>
          </button>
        </div>

        {/* 地圖圖例 */}
        <div className="absolute bottom-4 left-4 bg-white dark:bg-slate-800 rounded-lg shadow-lg p-3 text-xs">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-slate-600 dark:text-slate-300">我的位置</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
              <span className="text-slate-600 dark:text-slate-300">景點</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-slate-600 dark:text-slate-300">已選中</span>
            </div>
          </div>
        </div>
      </div>

      {/* 地圖載入提示 */}
      <div className="absolute top-4 left-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-lg px-3 py-2 text-xs text-slate-600 dark:text-slate-300">
        🗺️ 模擬地圖視圖
      </div>
    </div>
  );
}
