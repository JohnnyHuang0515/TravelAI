"use client";

import { useEffect, useState } from "react";
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
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapId] = useState(() => `map-container-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    // 載入 Leaflet CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(link);

    // 載入 Leaflet JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.onload = () => {
      setMapLoaded(true);
    };
    document.head.appendChild(script);

    return () => {
      if (document.head.contains(link)) {
        document.head.removeChild(link);
      }
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  useEffect(() => {
    if (!mapLoaded || typeof window === 'undefined') return;

    // 計算地圖中心點
    const getMapCenter = () => {
      if (userLocation) {
        return [userLocation.lat, userLocation.lon];
      }
      if (places.length > 0) {
        return [places[0].location.lat, places[0].location.lon];
      }
      // 預設為台北
      return [25.0330, 121.5654];
    };

    const center = getMapCenter();
    const zoom = userLocation ? 15 : 13;

    // 清除現有地圖
    const existingMap = (window as any).L.getMap ? (window as any).L.getMap(mapId) : null;
    if (existingMap) {
      existingMap.remove();
    }

    // 創建地圖
    const map = (window as any).L.map(mapId).setView(center, zoom);

    // 添加地圖圖層 - 使用更準確的圖層
    (window as any).L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(map);

    // 添加用戶位置標記
    if (userLocation) {
      const userIcon = (window as any).L.divIcon({
        html: '<div style="background-color: #3b82f6; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
        iconSize: [16, 16],
        className: 'user-location-marker'
      });

      (window as any).L.marker([userLocation.lat, userLocation.lon], { icon: userIcon })
        .addTo(map)
        .bindPopup('📍 我的位置');
    }

    // 添加景點標記 - 簡潔的大頭針樣式
    places.forEach((place, index) => {
      const isSelected = selectedPlaceId === place.id;
      
      // 使用 Leaflet 預設的大頭針圖標
      const markerIcon = (window as any).L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });

      const marker = (window as any).L.marker([place.location.lat, place.location.lon], { icon: markerIcon })
        .addTo(map);

      // 創建彈出視窗內容
      const popupContent = `
        <div style="min-width: 240px;">
          <div style="font-weight: 600; margin-bottom: 8px; color: #1f2937;">${place.name}</div>
          <div style="font-size: 14px;">
            ${place.rating ? `<div style="color: #f59e0b; margin-bottom: 4px;">⭐ ${place.rating.toFixed(1)}</div>` : ''}
            ${place.distance_meters ? `<div style="color: #6b7280; margin-bottom: 4px;">📍 ${place.distance_meters < 1000 ? `${place.distance_meters}m` : `${(place.distance_meters / 1000).toFixed(1)}km`}</div>` : ''}
            ${place.categories && place.categories.length > 0 ? `<div style="color: #6b7280; margin-bottom: 6px;">🏷️ ${place.categories.join(", ")}</div>` : ''}
            ${place.route_info ? `
              <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 8px; margin-top: 8px;">
                <div style="font-size: 13px; font-weight: 600; color: #1e40af; margin-bottom: 6px;">🛣️ 車程資訊</div>
                <div style="font-size: 11px; color: #1d4ed8; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;">
                  <div style="text-align: center; padding: 4px;">
                    <div style="font-weight: 600; font-size: 12px;">🏍️ 機車</div>
                    <div style="margin-top: 2px;">${place.route_info.motorcycle.formatted.distance}</div>
                    <div>${place.route_info.motorcycle.formatted.duration}</div>
                  </div>
                  <div style="text-align: center; padding: 4px;">
                    <div style="font-weight: 600; font-size: 12px;">🚗 小客車</div>
                    <div style="margin-top: 2px;">${place.route_info.car.formatted.distance}</div>
                    <div>${place.route_info.car.formatted.duration}</div>
                  </div>
                  <div style="text-align: center; padding: 4px;">
                    <div style="font-weight: 600; font-size: 12px;">🚌 大客車</div>
                    <div style="margin-top: 2px;">${place.route_info.bus.formatted.distance}</div>
                    <div>${place.route_info.bus.formatted.duration}</div>
                  </div>
                </div>
              </div>
            ` : ''}
            ${place.carbon_emission ? `
              <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px; margin-top: 8px;">
                <div style="font-size: 13px; font-weight: 600; color: #166534; margin-bottom: 6px;">🌱 每人碳排放</div>
                <div style="font-size: 11px; color: #15803d; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px;">
                  <div style="text-align: center; padding: 4px;">
                    <div style="font-weight: 600;">🏍️ 機車</div>
                    <div>${place.carbon_emission.motorcycle.formatted}</div>
                    <div style="font-size: 9px; color: #16a34a;">(${place.carbon_emission.motorcycle.passengers}人)</div>
                  </div>
                  <div style="text-align: center; padding: 4px;">
                    <div style="font-weight: 600;">🚗 小客車</div>
                    <div>${place.carbon_emission.car.formatted}</div>
                    <div style="font-size: 9px; color: #16a34a;">(${place.carbon_emission.car.passengers}人)</div>
                  </div>
                  <div style="text-align: center; padding: 4px;">
                    <div style="font-weight: 600;">🚌 大客車</div>
                    <div>${place.carbon_emission.bus.formatted}</div>
                    <div style="font-size: 9px; color: #16a34a;">(${place.carbon_emission.bus.passengers}人)</div>
                  </div>
                </div>
              </div>
            ` : ''}
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);

      // 點擊標記時只顯示彈出視窗，不觸發其他事件
      // 移除 onPlaceClick 以避免地圖跳轉
    });

    return () => {
      if (map) {
        map.remove();
      }
    };
  }, [mapLoaded, places, userLocation, selectedPlaceId, onPlaceClick]);

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
    <div className={`${className} rounded-lg overflow-hidden`}>
      <div id={mapId} className="h-full w-full"></div>
    </div>
  );
}