// OSRM 客戶端服務
// 直接與 OSRM 路由服務通信，提供真實的路由計算

export interface OSRMRouteRequest {
  coordinates: [number, number][]; // [經度, 緯度] 座標陣列
  profile: 'driving' | 'driving-traffic' | 'cycling' | 'walking';
  alternatives?: boolean; // 是否返回替代路線
  steps?: boolean; // 是否返回詳細步驟
  geometries?: 'polyline' | 'polyline6' | 'geojson';
  overview?: 'simplified' | 'full' | 'false';
}

export interface OSRMRouteResponse {
  routes: OSRMRoute[];
  waypoints: OSRMWaypoint[];
  code: string;
}

export interface OSRMRoute {
  distance: number; // 距離（米）
  duration: number; // 時間（秒）
  weight: number;
  geometry: string; // 路線幾何
  legs: OSRMLeg[];
}

export interface OSRMLeg {
  distance: number;
  duration: number;
  steps: OSRMStep[];
  summary: string;
  weight: number;
}

export interface OSRMStep {
  distance: number;
  duration: number;
  geometry: string;
  name: string;
  mode: string;
  maneuver: {
    bearing_after: number;
    bearing_before: number;
    location: [number, number];
    type: number;
    instruction: string;
  };
}

export interface OSRMWaypoint {
  hint: string;
  distance: number;
  name: string;
  location: [number, number];
}

// OSRM 服務配置
const OSRM_BASE_URL = process.env.NEXT_PUBLIC_OSRM_URL || 'http://localhost:5001';

class OSRMClient {
  private baseUrl: string;

  constructor(baseUrl: string = OSRM_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * 計算單一路線
   */
  async getRoute(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    options: {
      profile?: 'driving' | 'driving-traffic' | 'cycling' | 'walking';
      alternatives?: boolean;
      steps?: boolean;
    } = {}
  ): Promise<OSRMRouteResponse | null> {
    try {
      const coordinates = `${startLon},${startLat};${endLon},${endLat}`;
      const profile = options.profile || 'driving';
      const params = new URLSearchParams({
        alternatives: (options.alternatives || false).toString(),
        steps: (options.steps || false).toString(),
        geometries: 'geojson',
        overview: 'simplified'
      });

      const url = `${this.baseUrl}/route/v1/${profile}/${coordinates}?${params}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`OSRM API error: ${response.status} ${response.statusText}`);
      }

      const data: OSRMRouteResponse = await response.json();
      
      if (data.code !== 'Ok') {
        throw new Error(`OSRM routing error: ${data.code}`);
      }

      return data;
    } catch (error) {
      console.error('OSRM route calculation failed:', error);
      return null;
    }
  }

  /**
   * 計算多條替代路線
   */
  async getAlternativeRoutes(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number,
    options: {
      profile?: 'driving' | 'driving-traffic' | 'cycling' | 'walking';
      maxAlternatives?: number;
    } = {}
  ): Promise<OSRMRoute[] | null> {
    try {
      const coordinates = `${startLon},${startLat};${endLon},${endLat}`;
      const profile = options.profile || 'driving';
      const params = new URLSearchParams({
        alternatives: 'true',
        steps: 'false',
        geometries: 'geojson',
        overview: 'simplified',
        number: (options.maxAlternatives || 3).toString()
      });

      const url = `${this.baseUrl}/route/v1/${profile}/${coordinates}?${params}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`OSRM API error: ${response.status} ${response.statusText}`);
      }

      const data: OSRMRouteResponse = await response.json();
      
      if (data.code !== 'Ok') {
        throw new Error(`OSRM routing error: ${data.code}`);
      }

      return data.routes || [];
    } catch (error) {
      console.error('OSRM alternative routes calculation failed:', error);
      return null;
    }
  }

  /**
   * 計算多個目的地的路線
   */
  async getTrip(
    coordinates: [number, number][],
    options: {
      profile?: 'driving' | 'driving-traffic' | 'cycling' | 'walking';
      roundtrip?: boolean;
    } = {}
  ): Promise<OSRMRouteResponse | null> {
    try {
      const coordsString = coordinates.map(([lon, lat]) => `${lon},${lat}`).join(';');
      const profile = options.profile || 'driving';
      const params = new URLSearchParams({
        roundtrip: (options.roundtrip || false).toString(),
        geometries: 'geojson',
        overview: 'simplified'
      });

      const url = `${this.baseUrl}/trip/v1/${profile}/${coordsString}?${params}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`OSRM API error: ${response.status} ${response.statusText}`);
      }

      const data: OSRMRouteResponse = await response.json();
      
      if (data.code !== 'Ok') {
        throw new Error(`OSRM trip calculation error: ${data.code}`);
      }

      return data;
    } catch (error) {
      console.error('OSRM trip calculation failed:', error);
      return null;
    }
  }

  /**
   * 計算等時線（從起點出發，在指定時間內可到達的範圍）
   */
  async getIsochrone(
    centerLat: number,
    centerLon: number,
    options: {
      profile?: 'driving' | 'driving-traffic' | 'cycling' | 'walking';
      contours?: number[]; // 時間（秒）
      geometries?: 'polyline' | 'polyline6' | 'geojson';
    } = {}
  ): Promise<any> {
    try {
      const coordinates = `${centerLon},${centerLat}`;
      const profile = options.profile || 'driving';
      const contours = options.contours || [900, 1800, 3600]; // 15分鐘, 30分鐘, 1小時
      const params = new URLSearchParams({
        contours: contours.join(','),
        geometries: options.geometries || 'geojson'
      });

      const url = `${this.baseUrl}/isochrone/v1/${profile}/${coordinates}?${params}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`OSRM API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('OSRM isochrone calculation failed:', error);
      return null;
    }
  }

  /**
   * 檢查 OSRM 服務狀態
   */
  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      // 使用簡單的路由請求來檢查服務狀態
      const response = await fetch(`${this.baseUrl}/route/v1/driving/121.5170,25.0478;121.5170,25.0478`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.warn('OSRM service health check failed:', error);
      return false;
    }
  }
}

// 創建 OSRM 客戶端實例
export const osrmClient = new OSRMClient();
