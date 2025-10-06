"use client";

import { useState, useEffect } from "react";

export default function TestLocationPage() {
  const [location, setLocation] = useState<GeolocationPosition | null>(null);
  const [error, setError] = useState<GeolocationPositionError | null>(null);
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState<any>(null);

  const getLocation = () => {
    setLoading(true);
    setError(null);
    
    if (!navigator.geolocation) {
      setError({
        code: 0,
        message: "Geolocation is not supported by this browser.",
        PERMISSION_DENIED: 1,
        POSITION_UNAVAILABLE: 2,
        TIMEOUT: 3
      } as GeolocationPositionError);
      setLoading(false);
      return;
    }

    const options: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 20000,
      maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation(position);
        setDebugInfo({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          altitudeAccuracy: position.coords.altitudeAccuracy,
          heading: position.coords.heading,
          speed: position.coords.speed,
          timestamp: new Date(position.timestamp).toLocaleString(),
          options: options
        });
        setLoading(false);
      },
      (error) => {
        setError(error);
        setLoading(false);
      },
      options
    );
  };

  useEffect(() => {
    getLocation();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">位置精度測試</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">狀態</h2>
          <div className="space-y-2">
            <p><strong>載入中:</strong> {loading ? "是" : "否"}</p>
            <p><strong>錯誤:</strong> {error ? error.message : "無"}</p>
            <p><strong>錯誤代碼:</strong> {error ? error.code : "無"}</p>
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p><strong>錯誤詳情:</strong></p>
                <p>代碼: {error.code}</p>
                <p>訊息: {error.message}</p>
                {error.code === 1 && <p className="text-red-600">用戶拒絕了位置權限</p>}
                {error.code === 2 && <p className="text-red-600">位置資訊不可用</p>}
                {error.code === 3 && <p className="text-red-600">位置請求超時</p>}
              </div>
            )}
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
                <p><strong>精度等級:</strong> {
                  debugInfo.accuracy < 10 ? "極高" :
                  debugInfo.accuracy < 50 ? "高" :
                  debugInfo.accuracy < 100 ? "中等" :
                  debugInfo.accuracy < 500 ? "低" : "極低"
                }</p>
              </div>
              <div>
                <p><strong>海拔:</strong> {debugInfo.altitude || "未知"}</p>
                <p><strong>海拔精度:</strong> {debugInfo.altitudeAccuracy || "未知"}</p>
                <p><strong>方向:</strong> {debugInfo.heading || "未知"}</p>
                <p><strong>速度:</strong> {debugInfo.speed || "未知"}</p>
              </div>
            </div>
            <div className="mt-4">
              <p><strong>時間戳:</strong> {debugInfo.timestamp}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">地圖顯示</h2>
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
              <p className="text-sm text-gray-600">
                如果地圖位置不準確，請檢查：
                <br />• 瀏覽器位置權限是否正確
                <br />• 是否使用 VPN 或代理
                <br />• 網路連線是否穩定
              </p>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">操作</h2>
          <div className="space-x-4">
            <button
              onClick={getLocation}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
            >
              重新獲取位置
            </button>
            <button
              onClick={() => {
                if (location) {
                  const url = `https://www.google.com/maps?q=${location.coords.latitude},${location.coords.longitude}`;
                  window.open(url, '_blank');
                }
              }}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg"
              disabled={!location}
            >
              在 Google Maps 中開啟
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
