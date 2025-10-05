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

export interface RouteInfo {
  car: {
    distance: number; // 實際車程距離（米）
    duration: number; // 行駛時間（秒）
    distanceKm: number; // 距離（公里）
    durationMinutes: number; // 時間（分鐘）
    formatted: {
      distance: string;
      duration: string;
    };
  };
  motorcycle: {
    distance: number;
    duration: number;
    distanceKm: number;
    durationMinutes: number;
    formatted: {
      distance: string;
      duration: string;
    };
  };
  bus: {
    distance: number;
    duration: number;
    distanceKm: number;
    durationMinutes: number;
    formatted: {
      distance: string;
      duration: string;
    };
  };
}

export interface Place {
  id: string;
  name: string;
  distance_meters?: number;
  distance_text?: string;
  categories: string[];
  rating: number | null;
  stay_minutes: number;
  price_range: number | null;
  location: {
    lat: number;
    lon: number;
  };
  photo_url?: string;
  is_favorite?: boolean;
  carbon_emission?: CarbonEmissionInfo;
  route_info?: RouteInfo;
}

export interface PlaceDetail extends Place {
  description: string;
  address: string;
  phone: string;
  website: string;
  photo_urls: string[];
  hours: OperatingHours[];
}

export interface OperatingHours {
  weekday: number;
  open_time: string;
  close_time: string;
}

export interface PlaceFilter {
  categories: string[];
  radius: number; // 公尺
  min_rating: number;
  max_price: number | null;
  sort_by: 'distance' | 'rating' | 'name';
  sort_order: 'asc' | 'desc';
}

export interface UserLocation {
  lat: number;
  lon: number;
  accuracy: number;
}
