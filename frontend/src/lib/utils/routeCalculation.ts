// 車程計算工具
// 整合 OSRM 路由服務來計算實際的車程距離和時間

export interface RouteInfo {
  distance: number; // 實際車程距離（米）
  duration: number; // 行駛時間（秒）
  distanceKm: number; // 距離（公里）
  durationMinutes: number; // 時間（分鐘）
  formatted: {
    distance: string;
    duration: string;
  };
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

// 使用 OSRM API 計算實際車程（需要後端 API 支援）
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
    // 構建 API 請求
    const params = new URLSearchParams({
      start_lat: startLat.toString(),
      start_lon: startLon.toString(),
      end_lat: endLat.toString(),
      end_lon: endLon.toString(),
      vehicle_type: options.vehicleType,
      route_preference: options.routePreference,
      traffic_conditions: options.trafficConditions
    });
    
    const response = await fetch(`/api/v1/routing/calculate?${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      distance: data.distance,
      duration: data.duration,
      distanceKm: data.distance / 1000,
      durationMinutes: data.duration / 60,
      formatted: {
        distance: formatDistance(data.distance),
        duration: formatDuration(data.duration / 60)
      }
    };
  } catch (error) {
    console.warn('OSRM API 不可用，使用估算方法:', error);
    // 如果 OSRM API 不可用，回退到估算方法
    return estimateRouteDistance(startLat, startLon, endLat, endLon, options);
  }
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
