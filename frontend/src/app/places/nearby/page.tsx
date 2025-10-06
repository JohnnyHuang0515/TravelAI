"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { PlaceCard, PlaceFilter, PlaceMap } from "@/components/place";
import { Button } from "@/components/ui";
import { Navbar } from "@/components/layout/Navbar";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { Place, PlaceFilter as FilterType, UserLocation } from "@/lib/types/place";
import { calculateMultipleVehicleEmissions } from "@/lib/utils/carbonEmission";
import { calculateMultipleVehicleRoutes, getTrafficConditionSuggestion } from "@/lib/utils/routeCalculation";

export default function NearbyPlacesPage() {
  const { location, error, loading: locationLoading, requestLocation } = useGeolocation();
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');
  
  const [filters, setFilters] = useState<FilterType>({
    categories: [],
    radius: 5000,
    min_rating: 0,
    max_price: null,
    sort_by: 'distance',
    sort_order: 'asc'
  });

  const userLocation: UserLocation | undefined = useMemo(() => {
    if (!location) return undefined;
    return {
      lat: location.coords.latitude,
      lon: location.coords.longitude,
      accuracy: location.coords.accuracy
    };
  }, [location]);

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
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 真實的宜蘭地區景點和餐廳資料
      const realPlacesData = [
        // 景點資料 (來自 tdx_scenic_yilan_raw.json)
        {
          id: "1",
          name: "蘇澳冷泉公園",
          categories: ["文化類", "溫泉"],
          rating: 4.5,
          stay_minutes: 120,
          price_range: 2,
          location: { lat: 24.59654998779297, lon: 121.85115814208984 },
          photo_url: "https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=300&h=200&fit=crop",
          is_favorite: false,
          description: "得天獨厚的「天下第一奇泉」蘇澳冷泉",
          address: "宜蘭縣270蘇澳鎮冷泉路6-4號",
          phone: "886-3-9312152",
          openTime: "9：00- 17：00"
        },
        {
          id: "2",
          name: "礁溪溫泉公園",
          categories: ["溫泉", "休閒"],
          rating: 4.3,
          stay_minutes: 90,
          price_range: 3,
          location: { lat: 24.8270, lon: 121.7730 },
          photo_url: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=200&fit=crop",
          is_favorite: true,
          description: "宜蘭著名的溫泉勝地",
          address: "宜蘭縣礁溪鄉",
          phone: "886-3-9872403",
          openTime: "全天開放"
        },
        {
          id: "3",
          name: "蘭陽博物館",
          categories: ["文化類", "博物館"],
          rating: 4.7,
          stay_minutes: 180,
          price_range: 2,
          location: { lat: 24.8660, lon: 121.8320 },
          photo_url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=200&fit=crop",
          is_favorite: false,
          description: "展示宜蘭歷史文化的博物館",
          address: "宜蘭縣頭城鎮青雲路三段750號",
          phone: "886-3-9779700",
          openTime: "9:00-17:00"
        },
        {
          id: "4",
          name: "太平山國家森林遊樂區",
          categories: ["自然景觀", "森林"],
          rating: 4.8,
          stay_minutes: 240,
          price_range: 2,
          location: { lat: 24.5100, lon: 121.5500 },
          photo_url: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=200&fit=crop",
          is_favorite: false,
          description: "台灣著名的森林遊樂區",
          address: "宜蘭縣大同鄉",
          phone: "886-3-9809806",
          openTime: "6:00-20:00"
        },
        {
          id: "5",
          name: "幾米公園",
          categories: ["藝術", "文化類"],
          rating: 4.4,
          stay_minutes: 60,
          price_range: 1,
          location: { lat: 24.7510, lon: 121.7530 },
          photo_url: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop",
          is_favorite: true,
          description: "以幾米繪本為主題的公園",
          address: "宜蘭縣宜蘭市光復路1號",
          phone: "886-3-9325164",
          openTime: "全天開放"
        },
        // 餐廳資料 (來自 tdx_restaurant_yilan_raw.json)
        {
          id: "6",
          name: "藏酒酒莊",
          categories: ["中式美食", "酒莊"],
          rating: 4.2,
          stay_minutes: 120,
          price_range: 3,
          location: { lat: 24.90903091430664, lon: 121.84961700439453 },
          photo_url: "https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=300&h=200&fit=crop",
          is_favorite: false,
          description: "以各式水果酒釀造為主的酒莊",
          address: "宜蘭縣頭城鎮更新路126-50號",
          phone: "886-3-9778555",
          openTime: "09:00-21:00(預約制)"
        },
        {
          id: "7",
          name: "羅東夜市",
          categories: ["夜市", "美食"],
          rating: 4.6,
          stay_minutes: 90,
          price_range: 2,
          location: { lat: 24.6770, lon: 121.7730 },
          photo_url: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=200&fit=crop",
          is_favorite: true,
          description: "宜蘭最著名的夜市",
          address: "宜蘭縣羅東鎮",
          phone: "",
          openTime: "17:00-24:00"
        },
        {
          id: "8",
          name: "三星蔥文化館",
          categories: ["文化類", "農特產"],
          rating: 4.1,
          stay_minutes: 60,
          price_range: 1,
          location: { lat: 24.6700, lon: 121.6600 },
          photo_url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=200&fit=crop",
          is_favorite: false,
          description: "展示三星蔥文化的展館",
          address: "宜蘭縣三星鄉",
          phone: "886-3-9892010",
          openTime: "9:00-17:00"
        }
      ];


      const placesData = realPlacesData;

      // 計算每個景點到用戶位置的實際距離、車程和碳排放
      const mockPlaces: Place[] = await Promise.all(placesData.map(async (place) => {
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
  }, [userLocation, filters]);

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
          <Button onClick={requestLocation}>
            重新嘗試
          </Button>
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
          </div>
          
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
    </div>
  );
}
