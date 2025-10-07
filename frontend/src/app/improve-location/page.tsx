"use client";

import { useState, useEffect, useCallback } from "react";

export default function ImproveLocationPage() {
  const [location, setLocation] = useState<GeolocationPosition | null>(null);
  const [error, setError] = useState<GeolocationPositionError | null>(null);
  const [loading, setLoading] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [bestLocation, setBestLocation] = useState<GeolocationPosition | null>(null);
  const [debugInfo, setDebugInfo] = useState<{
    latitude: number;
    longitude: number;
    accuracy: number;
    altitude: number | null;
    altitudeAccuracy: number | null;
    heading: number | null;
    speed: number | null;
    timestamp: string;
    attempts: number;
    isBest: boolean;
    allReadings?: Array<{
      accuracy: number;
      timestamp: string;
    }>;
  } | null>(null);

  const getHighAccuracyLocation = useCallback(() => {
    setLoading(true);
    setError(null);
    setAttempts(prev => prev + 1);
    
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

    // 使用最高精度設定
    const options: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 60000, // 60秒超時
      maximumAge: 0 // 強制重新獲取
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation(position);
        
        // 如果這是第一次獲取位置，或者精度更好，就更新最佳位置
        if (!bestLocation || position.coords.accuracy < bestLocation.coords.accuracy) {
          setBestLocation(position);
        }
        
        setDebugInfo({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          altitudeAccuracy: position.coords.altitudeAccuracy,
          heading: position.coords.heading,
          speed: position.coords.speed,
          timestamp: new Date(position.timestamp).toLocaleString(),
          attempts: attempts + 1,
          isBest: !bestLocation || position.coords.accuracy < bestLocation.coords.accuracy
        });
        setLoading(false);
      },
      (error) => {
        setError(error);
        setLoading(false);
      },
      options
    );
  }, [attempts, bestLocation]);

  const getMultipleReadings = async () => {
    const readings: GeolocationPosition[] = [];
    const maxReadings = 5;
    
    for (let i = 0; i < maxReadings; i++) {
      try {
        const position = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 0
          });
        });
        
        readings.push(position);
        
        // 如果精度已經很好，就停止
        if (position.coords.accuracy < 20) {
          break;
        }
        
        // 等待2秒再進行下一次讀取
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (error) {
        console.error(`Reading ${i + 1} failed:`, error);
      }
    }
    
    if (readings.length > 0) {
      // 找到精度最好的讀取
      const bestReading = readings.reduce((best, current) => 
        current.coords.accuracy < best.coords.accuracy ? current : best
      );
      
      setLocation(bestReading);
      setBestLocation(bestReading);
      setDebugInfo({
        latitude: bestReading.coords.latitude,
        longitude: bestReading.coords.longitude,
        accuracy: bestReading.coords.accuracy,
        altitude: bestReading.coords.altitude,
        altitudeAccuracy: bestReading.coords.altitudeAccuracy,
        heading: bestReading.coords.heading,
        speed: bestReading.coords.speed,
        timestamp: new Date(bestReading.timestamp).toLocaleString(),
        attempts: readings.length,
        isBest: true,
        allReadings: readings.map(r => ({
          accuracy: r.coords.accuracy,
          timestamp: new Date(r.timestamp).toLocaleString()
        }))
      });
    }
  };

  useEffect(() => {
    getHighAccuracyLocation();
  }, [getHighAccuracyLocation]);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">位置精度提升工具</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">狀態</h2>
          <div className="space-y-2">
            <p><strong>載入中:</strong> {loading ? "是" : "否"}</p>
            <p><strong>嘗試次數:</strong> {attempts}</p>
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
                <p><strong>是否最佳:</strong> {debugInfo.isBest ? "是" : "否"}</p>
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
              <p><strong>讀取次數:</strong> {debugInfo.attempts}</p>
            </div>
            
            {debugInfo.allReadings && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">所有讀取結果:</h3>
                <div className="space-y-1">
                  {debugInfo.allReadings.map((reading, index: number) => (
                    <p key={index} className="text-sm">
                      讀取 {index + 1}: 精度 {reading.accuracy}m, 時間 {reading.timestamp}
                    </p>
                  ))}
                </div>
              </div>
            )}
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
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">精度提升建議</h2>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">🌐 網路環境</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 關閉 VPN 或代理服務</li>
                <li>• 使用穩定的 WiFi 連線</li>
                <li>• 避免在室內深處使用</li>
              </ul>
            </div>
            
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="font-semibold text-green-800 mb-2">📱 設備設定</h3>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• 確保 GPS 已開啟</li>
                <li>• 允許瀏覽器存取位置</li>
                <li>• 關閉省電模式</li>
                <li>• 到戶外或窗邊使用</li>
              </ul>
            </div>
            
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h3 className="font-semibold text-yellow-800 mb-2">🔄 多次嘗試</h3>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• 使用「多次讀取」功能</li>
                <li>• 等待更長時間讓 GPS 穩定</li>
                <li>• 嘗試不同的瀏覽器</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">操作</h2>
          <div className="space-x-4">
            <button
              onClick={getHighAccuracyLocation}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg"
              disabled={loading}
            >
              {loading ? "獲取中..." : "重新獲取位置"}
            </button>
            <button
              onClick={getMultipleReadings}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg"
              disabled={loading}
            >
              {loading ? "讀取中..." : "多次讀取 (推薦)"}
            </button>
            <button
              onClick={() => {
                if (location) {
                  const url = `https://www.google.com/maps?q=${location.coords.latitude},${location.coords.longitude}`;
                  window.open(url, '_blank');
                }
              }}
              className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg"
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
