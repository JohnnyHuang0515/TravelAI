import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Place {
  place_id: string;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  rating: number;
  price_level: number;
  types: string[];
  photos?: string[];
  opening_hours?: {
    open_now: boolean;
    periods: Array<{
      open: { day: number; time: string };
      close: { day: number; time: string };
    }>;
  };
  reviews?: Array<{
    author_name: string;
    rating: number;
    text: string;
    time: number;
  }>;
}

export interface NearbyPlacesRequest {
  latitude: number;
  longitude: number;
  radius?: number;
  type?: string;
  price_level?: number;
  rating?: number;
  limit?: number;
}

export interface NearbyPlacesResponse {
  places: Place[];
  total: number;
  next_page_token?: string;
}

export interface PlaceSearchRequest {
  query: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  radius?: number;
  type?: string;
  limit?: number;
}

export interface PlaceSearchResponse {
  places: Place[];
  total: number;
}

export interface FavoritePlace {
  id: string;
  user_id: string;
  place_id: string;
  place: Place;
  created_at: string;
}

// 取得附近景點
export const getNearbyPlaces = async (params: NearbyPlacesRequest): Promise<NearbyPlacesResponse> => {
  const queryParams = new URLSearchParams({
    latitude: params.latitude.toString(),
    longitude: params.longitude.toString(),
  });

  if (params.radius) queryParams.append("radius", params.radius.toString());
  if (params.type) queryParams.append("type", params.type);
  if (params.price_level) queryParams.append("price_level", params.price_level.toString());
  if (params.rating) queryParams.append("rating", params.rating.toString());
  if (params.limit) queryParams.append("limit", params.limit.toString());

  const response = await axios.get(`${API_BASE_URL}/v1/places/nearby?${queryParams}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 取得景點詳情
export const getPlace = async (placeId: string): Promise<Place> => {
  const response = await axios.get(`${API_BASE_URL}/v1/places/${placeId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 搜索景點
export const searchPlaces = async (params: PlaceSearchRequest): Promise<PlaceSearchResponse> => {
  const queryParams = new URLSearchParams({
    query: params.query,
  });

  if (params.location) {
    queryParams.append("latitude", params.location.latitude.toString());
    queryParams.append("longitude", params.location.longitude.toString());
  }
  if (params.radius) queryParams.append("radius", params.radius.toString());
  if (params.type) queryParams.append("type", params.type);
  if (params.limit) queryParams.append("limit", params.limit.toString());

  const response = await axios.get(`${API_BASE_URL}/v1/places/search?${queryParams}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 取得我的收藏景點
export const getFavoritePlaces = async (): Promise<FavoritePlace[]> => {
  const response = await axios.get(`${API_BASE_URL}/v1/places/favorites`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 收藏景點
export const addToFavorites = async (placeId: string): Promise<FavoritePlace> => {
  const response = await axios.post(`${API_BASE_URL}/v1/places/${placeId}/favorite`, {}, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });

  return response.data;
};

// 取消收藏景點
export const removeFromFavorites = async (placeId: string): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/v1/places/${placeId}/favorite`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });
};

// 檢查景點是否已收藏
export const isPlaceFavorited = async (placeId: string): Promise<boolean> => {
  try {
    const favorites = await getFavoritePlaces();
    return favorites.some(fav => fav.place_id === placeId);
  } catch (error) {
    return false;
  }
};
