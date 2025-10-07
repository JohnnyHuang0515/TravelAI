"use client";

import { useState, useEffect } from "react";
import { useGeolocation } from "@/lib/hooks/useGeolocation";

export default function DebugLocationPage() {
  const { location, error, loading, requestLocation } = useGeolocation();
  const [debugInfo, setDebugInfo] = useState<any>(null);

  useEffect(() => {
    if (location) {
      setDebugInfo({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy: location.coords.accuracy,
        altitude: location.coords.altitude,
        altitudeAccuracy: location.coords.altitudeAccuracy,
        heading: location.coords.heading,
        speed: location.coords.speed,
        timestamp: new Date(location.timestamp).toLocaleString()
      });
    }
  }, [location]);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">位置抓取除錯頁面</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">狀態</h2>
          <div className="space-y-2">
            <p><strong>載入中:</strong> {loading ? "是" : "否"}</p>
            <p><strong>錯誤:</strong> {error ? error.message : "無"}</p>
            <p><strong>錯誤代碼:</strong> {error ? error.code : "無"}</p>
          </div>
        </div>

        {debugInfo && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">位置資訊</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p><strong>緯度:</strong> {debugInfo.latitude}</p>
                <p><strong>經度:</strong> {debugInfo.longitude}</p>
                <p><strong>精度:</strong> {debugInfo.accuracy} 公尺</p>
              </div>
              <div>
                <p><strong>海拔:</strong> {debugInfo.altitude || "未知"}</p>
                <p><strong>海拔精度:</strong> {debugInfo.altitudeAccuracy || "未知"}</p>
                <p><strong>方向:</strong> {debugInfo.heading || "未知"}</p>
              </div>
            </div>
            <div className="mt-4">
              <p><strong>速度:</strong> {debugInfo.speed || "未知"}</p>
              <p><strong>時間戳:</strong> {debugInfo.timestamp}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">地圖測試</h2>
          {location && (
            <div className="space-y-4">
              <p>您的座標: {location.coords.latitude}, {location.coords.longitude}</p>
              <div className="h-96 w-full bg-gray-200 rounded-lg overflow-hidden">
                <iframe
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  src={`https://www.openstreetmap.org/export/embed.html?bbox=${location.coords.longitude-0.01},${location.coords.latitude-0.01},${location.coords.longitude+0.01},${location.coords.latitude+0.01}&layer=mapnik&marker=${location.coords.latitude},${location.coords.longitude}`}
                />
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">操作</h2>
          <button
            onClick={requestLocation}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
          >
            重新獲取位置
          </button>
        </div>
      </div>
    </div>
  );
}
