import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Trip {
  id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  duration: number;
  status: "draft" | "active" | "completed";
  is_public: boolean;
  share_token?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  days?: TripDay[];
}

export interface TripDay {
  id: string;
  trip_id: string;
  day_number: number;
  date: string;
  visits: TripVisit[];
  accommodation?: Accommodation;
}

export interface TripVisit {
  id: string;
  day_id: string;
  place_id: string;
  place_name: string;
  eta: string;
  etd: string;
  travel_minutes: number;
  stay_minutes: number;
  notes?: string;
}

export interface Accommodation {
  id: string;
  name: string;
  address: string;
  rating: number;
  price: number;
  check_in: string;
  check_out: string;
}

export interface CreateTripRequest {
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  duration: number;
  days: Omit<TripDay, "id" | "trip_id">[];
}

export interface UpdateTripRequest {
  title?: string;
  destination?: string;
  start_date?: string;
  end_date?: string;
  status?: "draft" | "active" | "completed";
  days?: Omit<TripDay, "id" | "trip_id">[];
}

export interface TripListResponse {
  trips: Trip[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// 取得我的行程列表
export const getMyTrips = async (
  page: number = 1,
  per_page: number = 10,
  status?: string
): Promise<TripListResponse> => {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: per_page.toString(),
  });
  
  if (status) {
    params.append("status", status);
  }

  const response = await axios.get(`${API_BASE_URL}/v1/trips?${params}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 取得行程詳情
export const getTrip = async (tripId: string): Promise<Trip> => {
  const response = await axios.get(`${API_BASE_URL}/v1/trips/${tripId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 建立新行程
export const createTrip = async (tripData: CreateTripRequest): Promise<Trip> => {
  const response = await axios.post(`${API_BASE_URL}/v1/trips`, tripData, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

// 更新行程
export const updateTrip = async (tripId: string, tripData: UpdateTripRequest): Promise<Trip> => {
  const response = await axios.put(`${API_BASE_URL}/v1/trips/${tripId}`, tripData, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });

  return response.data;
};

// 刪除行程
export const deleteTrip = async (tripId: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/v1/trips/${tripId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });
};

// 分享行程
export const shareTrip = async (tripId: string): Promise<{ share_token: string; share_url: string }> => {
  const response = await axios.post(`${API_BASE_URL}/v1/trips/${tripId}/share`, {}, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 複製行程
export const copyTrip = async (tripId: string): Promise<Trip> => {
  const response = await axios.post(`${API_BASE_URL}/v1/trips/${tripId}/copy`, {}, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 取得公開行程
export const getPublicTrip = async (shareToken: string): Promise<Trip> => {
  const response = await axios.get(`${API_BASE_URL}/v1/trips/public/${shareToken}`);
  return response.data;
};
