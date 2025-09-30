import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Trip, TripListResponse } from "@/lib/api/trips";

interface TripState {
  // 狀態
  trips: Trip[];
  currentTrip: Trip | null;
  isLoading: boolean;
  error: string | null;
  
  // 分頁資訊
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };

  // Actions
  setTrips: (trips: Trip[]) => void;
  setCurrentTrip: (trip: Trip | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPagination: (pagination: Partial<TripState["pagination"]>) => void;
  
  // 行程操作
  addTrip: (trip: Trip) => void;
  updateTrip: (tripId: string, updates: Partial<Trip>) => void;
  removeTrip: (tripId: string) => void;
  
  // 重置狀態
  reset: () => void;
}

const initialState = {
  trips: [],
  currentTrip: null,
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    per_page: 10,
    total: 0,
    total_pages: 0,
  },
};

export const useTripStore = create<TripState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setTrips: (trips) => set({ trips }),
      
      setCurrentTrip: (trip) => set({ currentTrip: trip }),
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setError: (error) => set({ error }),
      
      setPagination: (pagination) => 
        set((state) => ({
          pagination: { ...state.pagination, ...pagination }
        })),

      addTrip: (trip) =>
        set((state) => ({
          trips: [trip, ...state.trips],
          pagination: {
            ...state.pagination,
            total: state.pagination.total + 1,
          },
        })),

      updateTrip: (tripId, updates) =>
        set((state) => ({
          trips: state.trips.map((trip) =>
            trip.id === tripId ? { ...trip, ...updates } : trip
          ),
          currentTrip:
            state.currentTrip?.id === tripId
              ? { ...state.currentTrip, ...updates }
              : state.currentTrip,
        })),

      removeTrip: (tripId) =>
        set((state) => ({
          trips: state.trips.filter((trip) => trip.id !== tripId),
          currentTrip:
            state.currentTrip?.id === tripId ? null : state.currentTrip,
          pagination: {
            ...state.pagination,
            total: Math.max(0, state.pagination.total - 1),
          },
        })),

      reset: () => set(initialState),
    }),
    {
      name: "trip-store",
      partialize: (state) => ({
        trips: state.trips,
        currentTrip: state.currentTrip,
        pagination: state.pagination,
      }),
    }
  )
);
