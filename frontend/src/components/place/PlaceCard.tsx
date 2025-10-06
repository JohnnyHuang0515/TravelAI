"use client";

import { useState } from "react";
import { Card } from "@/components/ui";
import { Button } from "@/components/ui";
import { Place } from "@/lib/types/place";
import { RouteComparisonModal } from "./RouteComparisonModal";
import { getAlternativeRoutesComparison } from "@/lib/utils/routeCalculation";

interface PlaceCardProps {
  place: Place;
  distance?: number;
  isFavorite?: boolean;
  userLocation?: { lat: number; lon: number };
  onFavorite?: () => void;
  onViewDetail?: () => void;
  onAddToTrip?: () => void;
}

export function PlaceCard({ 
  place, 
  distance, 
  isFavorite = false, 
  userLocation,
  onFavorite, 
  onViewDetail, 
  onAddToTrip 
}: PlaceCardProps) {
  const [imageError, setImageError] = useState(false);
  const [showRouteComparison, setShowRouteComparison] = useState(false);
  const [routeComparisonData, setRouteComparisonData] = useState<any>(null);
  const [loadingRoutes, setLoadingRoutes] = useState(false);

  const formatDistance = (meters?: number) => {
    if (!meters) return "距離未知";
    if (meters < 1000) return `${Math.round(meters)}m`;
    return `${(meters / 1000).toFixed(1)}km`;
  };

  const formatPrice = (priceRange?: number | null) => {
    if (!priceRange) return "價格未知";
    return "$".repeat(priceRange);
  };

  const handleShowRouteComparison = async () => {
    if (!userLocation) {
      console.warn('用戶位置不可用，無法比較路線');
      return;
    }

    setLoadingRoutes(true);
    try {
      const comparisonData = await getAlternativeRoutesComparison(
        userLocation.lat,
        userLocation.lon,
        place.latitude,
        place.longitude
      );

      if (comparisonData) {
        setRouteComparisonData(comparisonData);
        setShowRouteComparison(true);
      }
    } catch (error) {
      console.error('獲取路線比較數據失敗:', error);
    } finally {
      setLoadingRoutes(false);
    }
  };

  const getCategoryIcon = (categories: string[]) => {
    const category = categories[0]?.toLowerCase();
    
    if (category?.includes('food') || category?.includes('restaurant')) {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      );
    }
    
    if (category?.includes('nature') || category?.includes('park')) {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      );
    }
    
    if (category?.includes('culture') || category?.includes('museum')) {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      );
    }
    
    return (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    );
  };

  return (
    <Card className="p-4 hover:shadow-lg transition-all duration-300 cursor-pointer group">
      <div className="space-y-3">
        {/* 圖片和基本資訊 */}
        <div className="flex space-x-3">
          {/* 景點圖片 */}
          <div className="w-20 h-20 bg-slate-200 dark:bg-slate-700 rounded-lg overflow-hidden flex-shrink-0">
            {place.photo_url && !imageError ? (
              <img
                src={place.photo_url}
                alt={place.name}
                className="w-full h-full object-cover"
                onError={() => setImageError(true)}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-400">
                {getCategoryIcon(place.categories)}
              </div>
            )}
          </div>

          {/* 景點資訊 */}
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-1 group-hover:text-primary-600 transition-colors line-clamp-1">
              {place.name}
            </h3>
            
            <div className="flex items-center space-x-2 mb-2">
              {place.rating && (
                <div className="flex items-center space-x-1">
                  <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span className="text-sm text-slate-600 dark:text-slate-300">
                    {place.rating.toFixed(1)}
                  </span>
                </div>
              )}
              
              {place.price_range && (
                <span className="text-sm text-slate-600 dark:text-slate-300">
                  {formatPrice(place.price_range)}
                </span>
              )}
            </div>

            {/* 類別標籤 */}
            <div className="flex flex-wrap gap-1 mb-2">
              {place.categories.slice(0, 2).map((category, index) => (
                <span
                  key={index}
                  className="bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-1 rounded text-xs"
                >
                  {category}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* 距離和停留時間 */}
        <div className="flex items-center justify-between text-sm text-slate-600 dark:text-slate-300">
          <div className="flex items-center space-x-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>{formatDistance(distance || place.distance_meters)}</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{place.stay_minutes} 分鐘</span>
          </div>
        </div>

        {/* 車程資訊 */}
        {place.route_info && (
          <div className="mt-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="text-xs font-medium text-blue-800 dark:text-blue-300 mb-1 flex items-center justify-between">
              <div className="flex items-center">
                <span className="mr-1">🛣️</span>
                車程資訊
                {place.route_info.car.isRealTime && (
                  <span className="ml-2 px-1 py-0.5 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded text-xs">
                    即時
                  </span>
                )}
              </div>
              {place.route_info.car.alternatives && place.route_info.car.alternatives.length > 0 && (
                <button
                  onClick={handleShowRouteComparison}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 underline"
                >
                  +{place.route_info.car.alternatives.length} 替代路線
                </button>
              )}
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-blue-700 dark:text-blue-400">
              <div className="text-center">
                <div className="flex items-center justify-center mb-1">
                  <span className="mr-1">🏍️</span>
                  <span className="font-medium">機車</span>
                </div>
                <div className="text-xs">
                  <div>{place.route_info.motorcycle.formatted.distance}</div>
                  <div>{place.route_info.motorcycle.formatted.duration}</div>
                </div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-1">
                  <span className="mr-1">🚗</span>
                  <span className="font-medium">小客車</span>
                </div>
                <div className="text-xs">
                  <div>{place.route_info.car.formatted.distance}</div>
                  <div>{place.route_info.car.formatted.duration}</div>
                </div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-1">
                  <span className="mr-1">🚌</span>
                  <span className="font-medium">大客車</span>
                </div>
                <div className="text-xs">
                  <div>{place.route_info.bus.formatted.distance}</div>
                  <div>{place.route_info.bus.formatted.duration}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 碳排放資訊 */}
        {place.carbon_emission && (
          <div className="mt-3 p-2 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="text-xs font-medium text-green-800 dark:text-green-300 mb-1 flex items-center">
              <span className="mr-1">🌱</span>
              交通碳排放
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-green-700 dark:text-green-400">
              <span className="flex items-center justify-center">
                <span className="mr-1">🏍️</span>
                機車: {place.carbon_emission.motorcycle.formatted}
              </span>
              <span className="flex items-center justify-center">
                <span className="mr-1">🚗</span>
                小客車: {place.carbon_emission.car.formatted}
              </span>
              <span className="flex items-center justify-center">
                <span className="mr-1">🚌</span>
                大客車: {place.carbon_emission.bus.formatted}
              </span>
            </div>
          </div>
        )}

        {/* 操作按鈕 */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-700">
          <div className="flex space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={onViewDetail}
              className="text-xs"
            >
              詳情
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={onAddToTrip}
              className="text-xs"
            >
              加入行程
            </Button>
          </div>
          
          <button
            onClick={onFavorite}
            className={`p-2 rounded-lg transition-colors ${
              isFavorite
                ? 'text-red-500 bg-red-50 dark:bg-red-900/20'
                : 'text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
            }`}
          >
            <svg className="w-4 h-4" fill={isFavorite ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
        </div>
      </div>

      {/* 路線比較模態框 */}
      {routeComparisonData && (
        <RouteComparisonModal
          isOpen={showRouteComparison}
          onClose={() => setShowRouteComparison(false)}
          routes={routeComparisonData.routes}
          bestRoute={routeComparisonData.bestRoute}
          summary={routeComparisonData.summary}
          placeName={place.name}
        />
      )}
    </Card>
  );
}
