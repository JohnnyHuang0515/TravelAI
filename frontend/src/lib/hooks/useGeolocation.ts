"use client";

import { useState, useEffect } from "react";

interface GeolocationState {
  location: GeolocationPosition | null;
  error: GeolocationPositionError | null;
  loading: boolean;
}

export function useGeolocation() {
  const [state, setState] = useState<GeolocationState>({
    location: null,
    error: null,
    loading: true
  });

  useEffect(() => {
    if (!navigator.geolocation) {
      setState({
        location: null,
        error: {
          code: 0,
          message: "Geolocation is not supported by this browser.",
          PERMISSION_DENIED: 1,
          POSITION_UNAVAILABLE: 2,
          TIMEOUT: 3
        } as GeolocationPositionError,
        loading: false
      });
      return;
    }

    const options: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 30000, // 增加超時時間到30秒
      maximumAge: 0 // 強制重新獲取位置
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          location: position,
          error: null,
          loading: false
        });
      },
      (error) => {
        setState({
          location: null,
          error,
          loading: false
        });
      },
      options
    );
  }, []);

  const requestLocation = () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    if (!navigator.geolocation) {
      setState(prev => ({
        ...prev,
        error: {
          code: 0,
          message: "Geolocation is not supported by this browser.",
          PERMISSION_DENIED: 1,
          POSITION_UNAVAILABLE: 2,
          TIMEOUT: 3
        } as GeolocationPositionError,
        loading: false
      }));
      return;
    }

    const options: PositionOptions = {
      enableHighAccuracy: true,
      timeout: 30000, // 增加超時時間到30秒
      maximumAge: 0 // 強制重新獲取
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          location: position,
          error: null,
          loading: false
        });
      },
      (error) => {
        setState({
          location: null,
          error,
          loading: false
        });
      },
      options
    );
  };

  return {
    ...state,
    requestLocation
  };
}
