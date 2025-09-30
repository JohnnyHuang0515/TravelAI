"use client";

import { useState, useEffect } from "react";
import { PlaceCard, PlaceFilter, PlaceMap } from "@/components/place";
import { Button } from "@/components/ui";
import { Navbar } from "@/components/layout/Navbar";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { Place, PlaceFilter as FilterType, UserLocation } from "@/lib/types/place";

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

  const userLocation: UserLocation | undefined = location ? {
    lat: location.coords.latitude,
    lon: location.coords.longitude,
    accuracy: location.coords.accuracy
  } : undefined;

  useEffect(() => {
    if (userLocation) {
      loadNearbyPlaces();
    }
  }, [userLocation, filters]);

  const loadNearbyPlaces = async () => {
    if (!userLocation) return;

    try {
      setLoading(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模擬景點資料
      const mockPlaces: Place[] = [
        {
          id: "1",
          name: "台北101",
          distance_meters: 500,
          categories: ["地標建築", "觀光景點"],
          rating: 4.5,
          stay_minutes: 120,
          price_range: 3,
          location: {
            lat: userLocation.lat + 0.001,
            lon: userLocation.lon + 0.001
          },
          photo_url: "https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=300&h=200&fit=crop",
          is_favorite: false
        },
        {
          id: "2",
          name: "信義商圈",
          distance_meters: 800,
          categories: ["購物", "美食"],
          rating: 4.3,
          stay_minutes: 180,
          price_range: 4,
          location: {
            lat: userLocation.lat - 0.001,
            lon: userLocation.lon + 0.002
          },
          photo_url: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&h=200&fit=crop",
          is_favorite: true
        },
        {
          id: "3",
          name: "象山步道",
          distance_meters: 1200,
          categories: ["自然景觀", "健行"],
          rating: 4.7,
          stay_minutes: 240,
          price_range: 1,
          location: {
            lat: userLocation.lat + 0.002,
            lon: userLocation.lon - 0.001
          },
          photo_url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=200&fit=crop",
          is_favorite: false
        },
        {
          id: "4",
          name: "松山文創園區",
          distance_meters: 1500,
          categories: ["文化歷史", "藝術"],
          rating: 4.2,
          stay_minutes: 150,
          price_range: 2,
          location: {
            lat: userLocation.lat - 0.002,
            lon: userLocation.lon - 0.002
          },
          photo_url: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=200&fit=crop",
          is_favorite: false
        },
        {
          id: "5",
          name: "饒河夜市",
          distance_meters: 2000,
          categories: ["美食", "夜市"],
          rating: 4.4,
          stay_minutes: 120,
          price_range: 2,
          location: {
            lat: userLocation.lat + 0.003,
            lon: userLocation.lon + 0.003
          },
          photo_url: "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop",
          is_favorite: true
        }
      ];

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

      // 排序
      filteredPlaces.sort((a, b) => {
        switch (filters.sort_by) {
          case 'distance':
            return (a.distance_meters || 0) - (b.distance_meters || 0);
          case 'rating':
            return (b.rating || 0) - (a.rating || 0);
          case 'name':
            return a.name.localeCompare(b.name);
          default:
            return 0;
        }
      });

      if (filters.sort_order === 'desc' && filters.sort_by !== 'rating') {
        filteredPlaces.reverse();
      }

      setPlaces(filteredPlaces);
    } catch (error) {
      console.error("載入附近景點失敗:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlaceClick = (placeId: string) => {
    setSelectedPlaceId(selectedPlaceId === placeId ? null : placeId);
  };

  const handleFavorite = async (placeId: string) => {
    setPlaces(prev => prev.map(place =>
      place.id === placeId
        ? { ...place, is_favorite: !place.is_favorite }
        : place
    ));
  };

  const handleViewDetail = (placeId: string) => {
    // 模擬查看詳情
    const place = places.find(p => p.id === placeId);
    if (place) {
      alert(`查看 ${place.name} 的詳細資訊`);
    }
  };

  const handleAddToTrip = (placeId: string) => {
    // 模擬加入行程
    const place = places.find(p => p.id === placeId);
    if (place) {
      alert(`已將 ${place.name} 加入行程`);
    }
  };

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
