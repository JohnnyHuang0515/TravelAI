// 車程計算工具
// 整合後端 OSRM 路由服務來計算實際的車程距離和時間

import { routingAPI } from '../api/routing';
import { osrmClient, OSRMRoute } from '../services/osrmClient';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface RouteInfo {
  distance: number; // 實際車程距離（米）
  duration: number; // 行駛時間（秒）
  distanceKm: number; // 距離（公里）
  durationMinutes: number; // 時間（分鐘）
  formatted: {
    distance: string;
    duration: string;
  };
  alternatives?: OSRMRoute[]; // 替代路線
  geometry?: string; // 路線幾何（GeoJSON）
  isRealTime?: boolean; // 是否為即時計算
}

export interface RouteCalculationOptions {
  vehicleType: 'car' | 'motorcycle' | 'bus';
  routePreference: 'fastest' | 'shortest' | 'balanced';
  trafficConditions: 'normal' | 'heavy' | 'light';
}

// 車輛速度係數（基於不同交通工具的實際行駛速度）
const VEHICLE_SPEED_FACTORS = {
  car: {
    highway: 1.0,      // 基準速度
    provincial: 0.8,   // 省道速度較慢
    urban: 0.6,        // 市區速度較慢
  },
  motorcycle: {
    highway: 0.9,      // 機車在高速公路上較慢
    provincial: 0.85,  // 省道稍快
    urban: 0.7,        // 市區相對靈活
  },
  bus: {
    highway: 0.8,      // 大客車在高速公路上較慢
    provincial: 0.7,   // 省道較慢
    urban: 0.5,        // 市區最慢，需要停靠站點
  }
};

// 交通狀況係數
const TRAFFIC_CONDITIONS_FACTORS = {
  light: 0.8,    // 交通順暢，時間減少20%
  normal: 1.0,   // 正常交通狀況
  heavy: 1.5,    // 交通擁塞，時間增加50%
};

// 路線偏好係數
const ROUTE_PREFERENCE_FACTORS = {
  fastest: { distanceFactor: 1.1, durationFactor: 0.9 },  // 選擇較快路線，可能距離稍長
  shortest: { distanceFactor: 0.95, durationFactor: 1.1 }, // 選擇最短路線，可能時間稍長
  balanced: { distanceFactor: 1.0, durationFactor: 1.0 },  // 平衡路線
};

// 估算實際車程（當 OSRM 服務不可用時）
export function estimateRouteDistance(
  startLat: number,
  startLon: number,
  endLat: number,
  endLon: number,
  options: RouteCalculationOptions = {
    vehicleType: 'car',
    routePreference: 'fastest',
    trafficConditions: 'normal'
  }
): RouteInfo {
  // 使用 Haversine 公式計算直線距離
  const R = 6371000; // 地球半徑（米）
  const dLat = (endLat - startLat) * Math.PI / 180;
  const dLon = (endLon - startLon) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(startLat * Math.PI / 180) * Math.cos(endLat * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const straightLineDistance = R * c;

  // 估算實際車程距離（考慮道路彎曲度）
  const roadCurvatureFactor = estimateRoadCurvature(straightLineDistance);
  const routePreference = ROUTE_PREFERENCE_FACTORS[options.routePreference];
  
  let actualDistance = straightLineDistance * roadCurvatureFactor * routePreference.distanceFactor;
  
  // 根據距離估算道路類型
  const roadType = estimateRoadType(actualDistance);
  
  // 估算平均速度
  const speedFactor = VEHICLE_SPEED_FACTORS[options.vehicleType][roadType];
  const trafficFactor = TRAFFIC_CONDITIONS_FACTORS[options.trafficConditions];
  
  // 不同道路類型的基準速度（km/h）
  const baseSpeeds = {
    highway: 80,
    provincial: 50,
    urban: 30
  };
  
  const averageSpeed = baseSpeeds[roadType] * speedFactor * trafficFactor;
  const durationSeconds = (actualDistance / 1000) / averageSpeed * 3600 * routePreference.durationFactor;
  
  const distanceKm = actualDistance / 1000;
  const durationMinutes = durationSeconds / 60;
  
  return {
    distance: Math.round(actualDistance),
    duration: Math.round(durationSeconds),
    distanceKm,
    durationMinutes,
    formatted: {
      distance: formatDistance(actualDistance),
      duration: formatDuration(durationMinutes)
    }
  };
}

// 估算道路彎曲度係數
function estimateRoadCurvature(distance: number): number {
  if (distance < 1000) {
    return 1.2; // 短距離，道路彎曲度較高
  } else if (distance < 5000) {
    return 1.15; // 中距離
  } else if (distance < 20000) {
    return 1.1; // 長距離，可能有高速公路
  } else {
    return 1.05; // 很長距離，高速公路比例高
  }
}

// 根據距離估算道路類型
function estimateRoadType(distance: number): 'highway' | 'provincial' | 'urban' {
  if (distance > 20000) {
    return 'highway'; // 20km以上，可能走高速公路
  } else if (distance > 5000) {
    return 'provincial'; // 5-20km，省道
  } else {
    return 'urban'; // 5km以下，市區道路
  }
}

// 格式化距離顯示
function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  } else {
    return `${(meters / 1000).toFixed(1)}km`;
  }
}

// 格式化時間顯示
function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${Math.round(minutes)}分鐘`;
  } else {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = Math.round(minutes % 60);
    if (remainingMinutes === 0) {
      return `${hours}小時`;
    } else {
      return `${hours}小時${remainingMinutes}分鐘`;
    }
  }
}

// 使用後端 OSRM 服務計算實際車程
export async function calculateOSRMRoute(
  startLat: number,
  startLon: number,
  endLat: number,
  endLon: number,
  options: RouteCalculationOptions = {
    vehicleType: 'car',
    routePreference: 'fastest',
    trafficConditions: 'normal'
  }
): Promise<RouteInfo | null> {
  try {
    // 首先嘗試使用後端 API
    try {
      const result = await routingAPI.calculateRouteSimple(
        startLat, startLon, endLat, endLon, {
          vehicle_type: options.vehicleType,
          route_preference: options.routePreference,
          traffic_conditions: options.trafficConditions,
          alternatives: true
        }
      );

      if (result && result.routes && result.routes.length > 0) {
        const mainRoute = result.routes[0];
        const alternatives = result.routes.slice(1);

        return {
          distance: mainRoute.distance,
          duration: mainRoute.duration,
          distanceKm: mainRoute.distance / 1000,
          durationMinutes: mainRoute.duration / 60,
          formatted: {
            distance: formatDistance(mainRoute.distance),
            duration: formatDuration(mainRoute.duration / 60)
          },
          alternatives: alternatives,
          geometry: mainRoute.geometry,
          isRealTime: true
        };
      }
    } catch (apiError) {
      console.warn('後端 API 不可用，嘗試直接 OSRM 服務:', apiError);
    }

    // 回退到直接 OSRM 服務
    const isHealthy = await osrmClient.checkHealth();
    if (!isHealthy) {
      console.warn('OSRM 服務不可用，使用估算方法');
      return estimateRouteDistance(startLat, startLon, endLat, endLon, options);
    }

    // 選擇合適的 OSRM 配置文件
    const profile = getOSRMProfile(options.vehicleType, options.trafficConditions);
    
    // 獲取主要路線
    const routeResponse = await osrmClient.getRoute(
      startLat, startLon, endLat, endLon,
      {
        profile,
        alternatives: true,
        steps: false
      }
    );

    if (!routeResponse || !routeResponse.routes.length) {
      console.warn('OSRM 無法計算路線，使用估算方法');
      return estimateRouteDistance(startLat, startLon, endLat, endLon, options);
    }

    const mainRoute = routeResponse.routes[0];
    const alternatives = routeResponse.routes.slice(1);

    // 根據交通狀況調整時間
    const trafficFactor = TRAFFIC_CONDITIONS_FACTORS[options.trafficConditions];
    const adjustedDuration = Math.round(mainRoute.duration * trafficFactor);

    return {
      distance: mainRoute.distance,
      duration: adjustedDuration,
      distanceKm: mainRoute.distance / 1000,
      durationMinutes: adjustedDuration / 60,
      formatted: {
        distance: formatDistance(mainRoute.distance),
        duration: formatDuration(adjustedDuration / 60)
      },
      alternatives: alternatives,
      geometry: mainRoute.geometry,
      isRealTime: true
    };
  } catch (error) {
    console.warn('OSRM 計算失敗，使用估算方法:', error);
    return estimateRouteDistance(startLat, startLon, endLat, endLon, options);
  }
}

// 根據交通工具和交通狀況選擇 OSRM 配置文件
function getOSRMProfile(
  vehicleType: 'car' | 'motorcycle' | 'bus',
  trafficConditions: 'normal' | 'heavy' | 'light'
): 'driving' | 'driving-traffic' {
  // 如果有交通數據且為小客車，使用 traffic 配置
  if (vehicleType === 'car' && trafficConditions !== 'light') {
    return 'driving-traffic';
  }
  return 'driving';
}

// 計算多種交通工具的車程比較
export async function calculateMultipleVehicleRoutes(
  startLat: number,
  startLon: number,
  endLat: number,
  endLon: number,
  trafficConditions: 'normal' | 'heavy' | 'light' = 'normal'
): Promise<{
  car: RouteInfo;
  motorcycle: RouteInfo;
  bus: RouteInfo;
}> {
  try {
    // 首先嘗試使用後端批量 API
    try {
      const result = await routingAPI.calculateMultipleVehicleRoutes(
        startLat, startLon, endLat, endLon, trafficConditions
      );

      return {
        car: convertToRouteInfo(result.car.routes[0], result.car.routes.slice(1)),
        motorcycle: convertToRouteInfo(result.motorcycle.routes[0], result.motorcycle.routes.slice(1)),
        bus: convertToRouteInfo(result.bus.routes[0], result.bus.routes.slice(1))
      };
    } catch (apiError) {
      console.warn('後端批量 API 不可用，使用單個請求:', apiError);
    }

    // 回退到單個請求
    const [carRoute, motorcycleRoute, busRoute] = await Promise.all([
      calculateOSRMRoute(startLat, startLon, endLat, endLon, {
        vehicleType: 'car',
        routePreference: 'fastest',
        trafficConditions
      }),
      calculateOSRMRoute(startLat, startLon, endLat, endLon, {
        vehicleType: 'motorcycle',
        routePreference: 'fastest',
        trafficConditions
      }),
      calculateOSRMRoute(startLat, startLon, endLat, endLon, {
        vehicleType: 'bus',
        routePreference: 'fastest',
        trafficConditions
      })
    ]);
    
    return {
      car: carRoute || estimateRouteDistance(startLat, startLon, endLat, endLon, {
        vehicleType: 'car',
        routePreference: 'fastest',
        trafficConditions
      }),
      motorcycle: motorcycleRoute || estimateRouteDistance(startLat, startLon, endLat, endLon, {
        vehicleType: 'motorcycle',
        routePreference: 'fastest',
        trafficConditions
      }),
      bus: busRoute || estimateRouteDistance(startLat, startLon, endLat, endLon, {
        vehicleType: 'bus',
        routePreference: 'fastest',
        trafficConditions
      })
    };
  } catch (error) {
    console.error('多交通工具路由計算失敗:', error);
    // 返回估算結果
    return {
      car: estimateRouteDistance(startLat, startLon, endLat, endLon, {
        vehicleType: 'car',
        routePreference: 'fastest',
        trafficConditions
      }),
      motorcycle: estimateRouteDistance(startLat, startLon, endLat, endLon, {
        vehicleType: 'motorcycle',
        routePreference: 'fastest',
        trafficConditions
      }),
      bus: estimateRouteDistance(startLat, startLon, endLat, endLon, {
        vehicleType: 'bus',
        routePreference: 'fastest',
        trafficConditions
      })
    };
  }
}

// 輔助函數：轉換後端 API 回應為 RouteInfo
function convertToRouteInfo(mainRoute: any, alternatives: any[]): RouteInfo {
  return {
    distance: mainRoute.distance,
    duration: mainRoute.duration,
    distanceKm: mainRoute.distance / 1000,
    durationMinutes: mainRoute.duration / 60,
    formatted: {
      distance: formatDistance(mainRoute.distance),
      duration: formatDuration(mainRoute.duration / 60)
    },
    alternatives: alternatives,
    geometry: mainRoute.geometry,
    isRealTime: true
  };
}

// 獲取交通狀況建議
export function getTrafficConditionSuggestion(): 'light' | 'normal' | 'heavy' {
  const hour = new Date().getHours();
  
  // 根據時間估算交通狀況
  if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
    return 'heavy'; // 上下班尖峰時間
  } else if ((hour >= 10 && hour <= 16) || (hour >= 20 && hour <= 22)) {
    return 'normal'; // 一般時間
  } else {
    return 'light'; // 深夜或清晨
  }
}

// 獲取多條替代路線的詳細比較
export async function getAlternativeRoutesComparison(
  startLat: number,
  startLon: number,
  endLat: number,
  endLon: number,
  options: RouteCalculationOptions = {
    vehicleType: 'car',
    routePreference: 'fastest',
    trafficConditions: 'normal'
  }
): Promise<{
  routes: RouteInfo[];
  bestRoute: RouteInfo;
  summary: {
    fastest: RouteInfo;
    shortest: RouteInfo;
    balanced: RouteInfo;
  };
} | null> {
  try {
    // 檢查 OSRM 服務狀態
    const isHealthy = await osrmClient.checkHealth();
    if (!isHealthy) {
      console.warn('OSRM 服務不可用');
      return null;
    }

    const profile = getOSRMProfile(options.vehicleType, options.trafficConditions);
    
    // 獲取多條替代路線
    const alternativeRoutes = await osrmClient.getAlternativeRoutes(
      startLat, startLon, endLat, endLon,
      {
        profile,
        maxAlternatives: 5
      }
    );

    if (!alternativeRoutes || alternativeRoutes.length === 0) {
      return null;
    }

    // 轉換為 RouteInfo 格式
    const routes: RouteInfo[] = alternativeRoutes.map((route, index) => {
      const trafficFactor = TRAFFIC_CONDITIONS_FACTORS[options.trafficConditions];
      const adjustedDuration = Math.round(route.duration * trafficFactor);

      return {
        distance: route.distance,
        duration: adjustedDuration,
        distanceKm: route.distance / 1000,
        durationMinutes: adjustedDuration / 60,
        formatted: {
          distance: formatDistance(route.distance),
          duration: formatDuration(adjustedDuration / 60)
        },
        geometry: route.geometry,
        isRealTime: true
      };
    });

    // 找出最佳路線
    const bestRoute = routes.reduce((best, current) => {
      if (options.routePreference === 'fastest') {
        return current.duration < best.duration ? current : best;
      } else if (options.routePreference === 'shortest') {
        return current.distance < best.distance ? current : best;
      } else {
        // balanced: 考慮時間和距離的平衡
        const bestScore = best.duration / 60 + best.distance / 1000 * 0.1;
        const currentScore = current.duration / 60 + current.distance / 1000 * 0.1;
        return currentScore < bestScore ? current : best;
      }
    });

    // 分類路線
    const summary = {
      fastest: routes.reduce((fastest, current) => 
        current.duration < fastest.duration ? current : fastest
      ),
      shortest: routes.reduce((shortest, current) => 
        current.distance < shortest.distance ? current : shortest
      ),
      balanced: bestRoute
    };

    return {
      routes,
      bestRoute,
      summary
    };
  } catch (error) {
    console.error('獲取替代路線比較失敗:', error);
    return null;
  }
}

// 計算等時線（可到達範圍）
export async function getReachableArea(
  centerLat: number,
  centerLon: number,
  maxTimeMinutes: number = 30,
  vehicleType: 'car' | 'motorcycle' | 'bus' = 'car'
): Promise<any> {
  try {
    const isHealthy = await osrmClient.checkHealth();
    if (!isHealthy) {
      console.warn('OSRM 服務不可用');
      return null;
    }

    const profile = vehicleType === 'car' ? 'driving' : 'driving';
    const contours = [maxTimeMinutes * 60]; // 轉換為秒

    return await osrmClient.getIsochrone(
      centerLat, centerLon,
      {
        profile,
        contours,
        geometries: 'geojson'
      }
    );
  } catch (error) {
    console.error('計算可到達範圍失敗:', error);
    return null;
  }
}
