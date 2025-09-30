import axios from "axios";
import { LoginRequest, RegisterRequest, RegisterAPIRequest, AuthResponse } from "@/lib/types/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 請求攔截器：添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 響應攔截器：處理 token 過期
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  // 登入
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post("/v1/auth/login", data);
    return response.data;
  },

  // 註冊
  register: async (data: RegisterAPIRequest): Promise<AuthResponse> => {
    const response = await api.post("/v1/auth/register", data);
    return response.data;
  },

  // 登出
  logout: async (): Promise<void> => {
    await api.post("/v1/auth/logout");
  },

  // 獲取當前用戶
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get("/v1/auth/me");
    return response.data;
  },

  // 刷新 token
  refreshToken: async (): Promise<AuthResponse> => {
    const response = await api.post("/v1/auth/refresh");
    return response.data;
  },
};
