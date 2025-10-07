"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { PlaceCard, PlaceFilter, PlaceMap } from "@/components/place";
import { Button } from "@/components/ui";
import { Navbar } from "@/components/layout/Navbar";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { Place, PlaceFilter as FilterType, UserLocation } from "@/lib/types/place";

// API 回應的景點資料類型
interface ApiPlace {
  id: string;
  name: string;
  categories: string[];
  rating: number | null;
  stay_minutes: number;
  price_range: number | null;
  location: {
    lat: number;
    lon: number;
  };
  is_favorite: boolean;
}

// 轉換後的景點資料類型
interface TransformedPlace {
  id: string;
  name: string;
  categories: string[];
  rating: number;
  stay_minutes: number;
  price_range: number;
  location: {
    lat: number;
    lon: number;
  };
  photo_url: string;
  is_favorite: boolean;
  description: string;
  address: string;
  phone: string;
  openTime: string;
}
import { calculateMultipleVehicleEmissions } from "@/lib/utils/carbonEmission";
import { calculateMultipleVehicleRoutes, getTrafficConditionSuggestion } from "@/lib/utils/routeCalculation";
// import { searchPlaces } from "@/lib/api/places"; // 暫時不使用

export default function NearbyPlacesPage() {
  const { location, error, loading: locationLoading, requestLocation } = useGeolocation();
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  const [showLocationPicker, setShowLocationPicker] = useState(false);
  const [manualLocation, setManualLocation] = useState<{lat: number, lon: number} | null>(null);
  
  const [filters, setFilters] = useState<FilterType>({
    categories: [],
    radius: 5000,
    min_rating: 0,
    max_price: null,
    sort_by: 'distance',
    sort_order: 'asc'
  });

  const userLocation: UserLocation | undefined = useMemo(() => {
    // 優先使用手動選擇的位置，其次使用 GPS 位置
    if (manualLocation) {
      return {
        lat: manualLocation.lat,
        lon: manualLocation.lon,
        accuracy: 0 // 手動選擇的位置精度設為 0
      };
    }
    if (!location) return undefined;
    return {
      lat: location.coords.latitude,
      lon: location.coords.longitude,
      accuracy: location.coords.accuracy
    };
  }, [location, manualLocation]);

  // 計算兩點間距離的函數（使用 Haversine 公式）
  const calculateDistance = useCallback((lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371000; // 地球半徑（米）
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // 距離（米）
  }, []);

  const loadNearbyPlaces = useCallback(async () => {
    if (!userLocation) return;

    try {
      setLoading(true);
      
      // 直接調用後端 API
      const response = await fetch(
        `http://localhost:8000/v1/places/nearby?lat=${userLocation.lat}&lon=${userLocation.lon}&radius=${filters.radius}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const apiResponse = await response.json();

      // 轉換 API 回應格式為前端需要的格式
      const transformedPlaces: TransformedPlace[] = apiResponse.places.map((place: ApiPlace) => ({
        id: place.id,
        name: place.name,
        categories: place.categories || [],
        rating: place.rating || 0,
        stay_minutes: place.stay_minutes || 120,
        price_range: place.price_range || 2,
        location: { 
          lat: place.location.lat, 
          lon: place.location.lon 
        },
        photo_url: "https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=300&h=200&fit=crop",
        is_favorite: place.is_favorite || false,
        description: "",
        address: "",
        phone: "",
        openTime: "營業時間未知"
      }));

      // 計算每個景點到用戶位置的實際距離、車程和碳排放
      const mockPlaces: Place[] = await Promise.all(transformedPlaces.map(async (place: TransformedPlace) => {
        const distanceMeters = Math.round(calculateDistance(
          userLocation.lat,
          userLocation.lon,
          place.location.lat,
          place.location.lon
        ));
        const distanceKm = distanceMeters / 1000;
        
        // 計算碳排放
        const carbonEmission = calculateMultipleVehicleEmissions(distanceKm);
        
        // 計算車程資訊
        const trafficConditions = getTrafficConditionSuggestion();
        const routeInfo = await calculateMultipleVehicleRoutes(
          userLocation.lat,
          userLocation.lon,
          place.location.lat,
          place.location.lon,
          trafficConditions
        );
        
        return {
          ...place,
          latitude: place.location.lat,
          longitude: place.location.lon,
          distance_meters: distanceMeters,
          carbon_emission: carbonEmission,
          route_info: routeInfo
        };
      }));


      // 應用篩選
      let filteredPlaces = mockPlaces;

      // 類別篩選
      if (filters.categories.length > 0) {
        filteredPlaces = filteredPlaces.filter(place =>
          place.categories.some(category =>
            filters.categories.some(filterCategory =>
              category.toLowerCase().includes(filterCategory.toLowerCase())
            )
          )
        );
      }

      // 評分篩選
      if (filters.min_rating > 0) {
        filteredPlaces = filteredPlaces.filter(place =>
          place.rating && place.rating >= filters.min_rating
        );
      }

      // 距離篩選
      filteredPlaces = filteredPlaces.filter(place =>
        place.distance_meters && place.distance_meters <= filters.radius
      );

      // 排序 - 確保按照距離排序
      filteredPlaces.sort((a, b) => {
        switch (filters.sort_by) {
          case 'distance':
            const distanceA = a.distance_meters || 0;
            const distanceB = b.distance_meters || 0;
            return filters.sort_order === 'desc' ? distanceB - distanceA : distanceA - distanceB;
          case 'rating':
            const ratingA = a.rating || 0;
            const ratingB = b.rating || 0;
            return filters.sort_order === 'desc' ? ratingA - ratingB : ratingB - ratingA;
          case 'name':
            const nameA = a.name.toLowerCase();
            const nameB = b.name.toLowerCase();
            return filters.sort_order === 'desc' ? nameB.localeCompare(nameA) : nameA.localeCompare(nameB);
          default:
            return 0;
        }
      });


      setPlaces(filteredPlaces);
    } catch (error) {
      console.error("載入附近景點失敗:", error);
    } finally {
      setLoading(false);
    }
  }, [userLocation, filters, calculateDistance]);

  useEffect(() => {
    if (userLocation) {
      loadNearbyPlaces();
    }
  }, [userLocation, loadNearbyPlaces]);

  const handlePlaceClick = useCallback((placeId: string) => {
    setSelectedPlaceId(prev => prev === placeId ? null : placeId);
  }, []);

  const handleFavorite = useCallback(async (placeId: string) => {
    setPlaces(prev => prev.map(place =>
      place.id === placeId
        ? { ...place, is_favorite: !place.is_favorite }
        : place
    ));
  }, []);

  const handleViewDetail = useCallback((placeId: string) => {
    // 模擬查看詳情
    const place = places.find(p => p.id === placeId);
    if (place) {
      alert(`查看 ${place.name} 的詳細資訊`);
    }
  }, [places]);

  const handleAddToTrip = useCallback((placeId: string) => {
    // 模擬加入行程
    const place = places.find(p => p.id === placeId);
    if (place) {
      alert(`已將 ${place.name} 加入行程`);
    }
  }, [places]);

  if (locationLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-slate-600 dark:text-slate-300">正在取得您的位置...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
            無法取得位置資訊
          </h2>
          <p className="text-slate-600 dark:text-slate-300 mb-6">
            {error.message || "請允許瀏覽器存取您的位置，或手動輸入位置"}
          </p>
          <div className="space-x-4">
            <Button onClick={requestLocation}>
              重新嘗試
            </Button>
            <Button 
              onClick={() => setShowLocationPicker(true)}
              variant="outline"
            >
              手動選擇位置
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col">
      <Navbar />
      <main className="flex-1 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-8">
        {/* 頁面標題 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              附近景點
            </h1>
            <p className="text-slate-600 dark:text-slate-300">
              探索您周邊的精彩景點
            </p>
            {userLocation && (
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                位置: {userLocation.lat.toFixed(4)}, {userLocation.lon.toFixed(4)}
                {manualLocation && <span className="ml-2 text-blue-600">(手動選擇)</span>}
              </p>
            )}
          </div>
          
          {/* 操作按鈕 */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowLocationPicker(true)}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              手動選擇位置
            </button>
            
            {/* 視圖切換 */}
            <div className="flex bg-white dark:bg-slate-800 rounded-lg p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-primary-500 text-white'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                列表
              </button>
              <button
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'map'
                    ? 'bg-primary-500 text-white'
                    : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                地圖
              </button>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* 左側：篩選器 */}
          <div className="lg:col-span-1">
            <PlaceFilter
              filters={filters}
              onChange={setFilters}
            />
          </div>

          {/* 右側：景點列表或地圖 */}
          <div className="lg:col-span-3">
            {viewMode === 'list' ? (
              <div className="space-y-4">
                {loading ? (
                  // 載入中的骨架
                  Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="bg-white dark:bg-slate-800 rounded-xl p-4 animate-pulse">
                      <div className="flex space-x-3">
                        <div className="w-20 h-20 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
                          <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
                          <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : places.length > 0 ? (
                  places.map((place) => (
                    <PlaceCard
                      key={place.id}
                      place={place}
                      distance={place.distance_meters}
                      isFavorite={place.is_favorite}
                      userLocation={userLocation}
                      onFavorite={() => handleFavorite(place.id)}
                      onViewDetail={() => handleViewDetail(place.id)}
                      onAddToTrip={() => handleAddToTrip(place.id)}
                    />
                  ))
                ) : (
                  <div className="bg-white dark:bg-slate-800 rounded-xl p-8 text-center">
                    <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                      沒有找到符合條件的景點
                    </h3>
                    <p className="text-slate-600 dark:text-slate-300">
                      請調整篩選條件或擴大搜尋範圍
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white dark:bg-slate-800 rounded-xl p-4">
                <PlaceMap
                  places={places}
                  userLocation={userLocation}
                  selectedPlaceId={selectedPlaceId || undefined}
                  onPlaceClick={handlePlaceClick}
                  className="h-96"
                />
              </div>
            )}
          </div>
        </div>
        </div>
      </main>

      {/* 手動位置選擇模態框 */}
      {showLocationPicker && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              手動選擇位置
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  緯度 (Latitude)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  placeholder="例如: 25.0330"
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
                  id="manual-lat"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  經度 (Longitude)
                </label>
                <input
                  type="number"
                  step="0.0001"
                  placeholder="例如: 121.5654"
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
                  id="manual-lon"
                />
              </div>
              
              <div className="text-sm text-slate-500 dark:text-slate-400">
                <p>💡 提示：</p>
                <p>• 台北: 25.0330, 121.5654</p>
                <p>• 宜蘭: 24.7500, 121.7500</p>
                <p>• 您可以在 Google Maps 中右鍵點擊位置來獲取座標</p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowLocationPicker(false)}
                className="px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
              >
                取消
              </button>
              <button
                onClick={() => {
                  const latInput = document.getElementById('manual-lat') as HTMLInputElement;
                  const lonInput = document.getElementById('manual-lon') as HTMLInputElement;
                  
                  if (latInput.value && lonInput.value) {
                    const lat = parseFloat(latInput.value);
                    const lon = parseFloat(lonInput.value);
                    
                    if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
                      setManualLocation({ lat, lon });
                      setShowLocationPicker(false);
                    } else {
                      alert('請輸入有效的座標範圍：緯度 -90 到 90，經度 -180 到 180');
                    }
                  } else {
                    alert('請輸入緯度和經度');
                  }
                }}
                className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg"
              >
                確認
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
