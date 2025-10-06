/**
 * 路由計算 API 客戶端
 * 整合後端 OSRM 服務提供路由計算功能
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface Coordinate {
  lat: number;
  lon: number;
}

export interface RouteRequest {
  start: Coordinate;
  end: Coordinate;
  vehicle_type?: 'car' | 'motorcycle' | 'bus';
  route_preference?: 'fastest' | 'shortest' | 'balanced';
  traffic_conditions?: 'light' | 'normal' | 'heavy';
  alternatives?: boolean;
}

export interface RouteLeg {
  distance: number;
  duration: number;
  summary: string;
  steps: any[];
}

export interface RouteResponse {
  distance: number;
  duration: number;
  geometry: string;
  legs: RouteLeg[];
  weight_name: string;
  weight: number;
}

export interface AlternativeRoute {
  routes: RouteResponse[];
  waypoints: Array<{
    hint: string;
    distance: number;
    name: string;
    location: [number, number];
  }>;
  code: string;
}

export interface BatchRouteRequest {
  requests: RouteRequest[];
}

export interface BatchRouteResponse {
  results: Array<{
    index: number;
    result?: AlternativeRoute;
    error?: string;
    success: boolean;
  }>;
  total: number;
  successful: number;
}

export interface IsochroneRequest {
  center_lat: number;
  center_lon: number;
  max_time_minutes?: number;
  vehicle_type?: 'car' | 'motorcycle' | 'bus';
}

class RoutingAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * 計算單一路線
   */
  async calculateRoute(request: RouteRequest): Promise<AlternativeRoute> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/routing/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('路由計算失敗:', error);
      throw error;
    }
  }

  /**
   * 計算單一路線 (GET 版本)
   */
  async calculateRouteSimple(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    options: {
      vehicle_type?: 'car' | 'motorcycle' | 'bus';
      route_preference?: 'fastest' | 'shortest' | 'balanced';
      traffic_conditions?: 'light' | 'normal' | 'heavy';
      alternatives?: boolean;
    } = {}
  ): Promise<AlternativeRoute> {
    try {
      const params = new URLSearchParams({
        start_lat: startLat.toString(),
        start_lon: startLon.toString(),
        end_lat: endLat.toString(),
        end_lon: endLon.toString(),
        vehicle_type: options.vehicle_type || 'car',
        route_preference: options.route_preference || 'fastest',
        traffic_conditions: options.traffic_conditions || 'normal',
        alternatives: (options.alternatives || false).toString(),
      });

      const response = await fetch(`${this.baseUrl}/v1/routing/calculate?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('路由計算失敗:', error);
      throw error;
    }
  }

  /**
   * 批量計算路線
   */
  async calculateBatchRoutes(requests: RouteRequest[]): Promise<BatchRouteResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/routing/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ requests }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('批量路由計算失敗:', error);
      throw error;
    }
  }

  /**
   * 計算等時線
   */
  async calculateIsochrone(request: IsochroneRequest): Promise<any> {
    try {
      const params = new URLSearchParams({
        center_lat: request.center_lat.toString(),
        center_lon: request.center_lon.toString(),
        max_time_minutes: (request.max_time_minutes || 30).toString(),
        vehicle_type: request.vehicle_type || 'car',
      });

      const response = await fetch(`${this.baseUrl}/v1/routing/isochrone?${params}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('等時線計算失敗:', error);
      throw error;
    }
  }

  /**
   * 健康檢查
   */
  async healthCheck(): Promise<{ status: string; osrm_service: string; timestamp: string; response?: boolean; error?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/routing/health`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('健康檢查失敗:', error);
      throw error;
    }
  }

  /**
   * 計算多種交通工具的路線
   */
  async calculateMultipleVehicleRoutes(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    trafficConditions: 'light' | 'normal' | 'heavy' = 'normal'
  ): Promise<{
    car: AlternativeRoute;
    motorcycle: AlternativeRoute;
    bus: AlternativeRoute;
  }> {
    try {
      const [carRoute, motorcycleRoute, busRoute] = await Promise.all([
        this.calculateRouteSimple(startLat, startLon, endLat, endLon, {
          vehicle_type: 'car',
          route_preference: 'fastest',
          traffic_conditions: trafficConditions,
          alternatives: true
        }),
        this.calculateRouteSimple(startLat, startLon, endLat, endLon, {
          vehicle_type: 'motorcycle',
          route_preference: 'fastest',
          traffic_conditions: trafficConditions,
          alternatives: true
        }),
        this.calculateRouteSimple(startLat, startLon, endLat, endLon, {
          vehicle_type: 'bus',
          route_preference: 'fastest',
          traffic_conditions: trafficConditions,
          alternatives: true
        })
      ]);

      return {
        car: carRoute,
        motorcycle: motorcycleRoute,
        bus: busRoute
      };
    } catch (error) {
      console.error('多交通工具路由計算失敗:', error);
      throw error;
    }
  }

  /**
   * 獲取替代路線比較
   */
  async getAlternativeRoutes(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    vehicleType: 'car' | 'motorcycle' | 'bus' = 'car',
    trafficConditions: 'light' | 'normal' | 'heavy' = 'normal'
  ): Promise<{
    routes: RouteResponse[];
    bestRoute: RouteResponse;
    summary: {
      fastest: RouteResponse;
      shortest: RouteResponse;
      balanced: RouteResponse;
    };
  } | null> {
    try {
      const result = await this.calculateRouteSimple(startLat, startLon, endLat, endLon, {
        vehicle_type: vehicleType,
        route_preference: 'fastest',
        traffic_conditions: trafficConditions,
        alternatives: true
      });

      if (!result.routes || result.routes.length === 0) {
        return null;
      }

      const routes = result.routes;
      
      // 找出最佳路線
      const bestRoute = routes.reduce((best, current) => {
        return current.duration < best.duration ? current : best;
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
      console.error('替代路線獲取失敗:', error);
      return null;
    }
  }
}

// 創建路由 API 實例
export const routingAPI = new RoutingAPI();

// 導出類型
export type {
  Coordinate,
  RouteRequest,
  RouteResponse,
  AlternativeRoute,
  BatchRouteRequest,
  BatchRouteResponse,
  IsochroneRequest
};