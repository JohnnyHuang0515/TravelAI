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
