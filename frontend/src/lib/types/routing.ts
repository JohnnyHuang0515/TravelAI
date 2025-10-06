/**
 * 路由規劃相關的 TypeScript 類型定義
 */

// 交通工具類型
export type VehicleType = 'car' | 'motorcycle' | 'bus';

// 路線偏好
export type RoutePreference = 'fastest' | 'shortest' | 'balanced';

// 交通狀況
export type TrafficConditions = 'normal' | 'heavy' | 'light';

// 路由計算選項
export interface RouteCalculationOptions {
  vehicleType: VehicleType;
  routePreference: RoutePreference;
  trafficConditions: TrafficConditions;
}

// 路由計算請求
export interface RouteCalculationRequest {
  start_lat: number;
  start_lon: number;
  end_lat: number;
  end_lon: number;
  vehicle_type?: string;
  route_preference?: string;
  traffic_conditions?: string;
}

// 路由計算回應
export interface RouteCalculationResponse {
  duration: number; // 行駛時間（秒）
  distance: number; // 距離（公尺）
  carbon_emission: number; // 碳排放量（克）
  route_geometry?: string; // 路線幾何（可選）
}

// 時間矩陣回應
export interface TravelTimeMatrixResponse {
  matrix: number[][];
  locations: Array<[number, number]>;
  vehicle_type: string;
}

// 路線資訊（格式化後）
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

// 多種交通工具的路線比較
export interface MultipleVehicleRoutes {
  car: RouteCalculationResponse;
  motorcycle: RouteCalculationResponse;
  bus: RouteCalculationResponse;
}

// 碳排放資訊
export interface CarbonEmissionInfo {
  car: {
    co2Grams: number;
    co2Kg: number;
    formatted: string;
  };
  bus: {
    co2Grams: number;
    co2Kg: number;
    formatted: string;
  };
  motorcycle: {
    co2Grams: number;
    co2Kg: number;
    formatted: string;
  };
}

// 路線評分權重
export interface RouteScoreWeights {
  time: number;
  distance: number;
  carbon: number;
}

// 路線評分結果
export interface RouteScore {
  total: number;
  breakdown: {
    time: number;
    distance: number;
    carbon: number;
  };
  weights: RouteScoreWeights;
}

// 路線比較結果
export interface RouteComparison {
  routes: {
    [key in VehicleType]: {
      route: RouteCalculationResponse;
      score: number;
      advantages: string[];
      disadvantages: string[];
    };
  };
  recommendation: VehicleType;
  reasoning: string;
}
