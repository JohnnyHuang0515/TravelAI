export interface Trip {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  destination: string;
  duration_days: number;
  start_date: string;
  end_date: string;
  itinerary_data: Itinerary;
  is_public: boolean;
  share_token: string | null;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface TripSummary {
  id: string;
  title: string;
  description: string | null;
  destination: string;
  duration_days: number;
  start_date: string;
  end_date: string;
  is_public: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface SaveTripRequest {
  title: string;
  description?: string;
  destination: string;
  itinerary_data: Itinerary;
  is_public: boolean;
}

export interface UpdateTripRequest {
  title?: string;
  description?: string;
  is_public?: boolean;
}

export interface Itinerary {
  days: Day[];
}

export interface Day {
  day: number;
  date: string;
  visits: Visit[];
  accommodation?: Accommodation;
}

export interface Visit {
  place_id: string;
  name: string;
  eta: string;
  etd: string;
  travel_minutes: number;
  stay_minutes: number;
}

export interface Accommodation {
  name: string;
  address: string;
  rating: number;
  price: number;
}
