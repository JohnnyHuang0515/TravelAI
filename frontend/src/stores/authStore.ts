import { create } from "zustand";
import { persist } from "zustand/middleware";
import { User, AuthState, LoginRequest, RegisterRequest } from "@/lib/types/auth";
import { authAPI } from "@/lib/api/auth";
import toast from "react-hot-toast";

interface AuthStore extends AuthState {
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (data: LoginRequest) => {
        try {
          set({ isLoading: true });
          const response = await authAPI.login(data);
          
          localStorage.setItem("access_token", response.access_token);
          localStorage.setItem("user", JSON.stringify(response.user));
          
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          
          toast.success("登入成功！");
        } catch (error: any) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || "登入失敗，請檢查您的帳號密碼";
          toast.error(message);
          throw error;
        }
      },

      register: async (data: RegisterRequest) => {
        try {
          set({ isLoading: true });
          // 只傳送後端需要的欄位
          const registerData = {
            email: data.email,
            password: data.password,
            username: data.username
          };
          const response = await authAPI.register(registerData);
          
          localStorage.setItem("access_token", response.access_token);
          localStorage.setItem("user", JSON.stringify(response.user));
          
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
          
          toast.success("註冊成功！歡迎使用智慧旅遊系統");
        } catch (error: any) {
          set({ isLoading: false });
          console.error("註冊錯誤:", error);
          console.error("錯誤回應:", error.response?.data);
          const message = error.response?.data?.detail || "註冊失敗，請稍後再試";
          toast.error(message);
          throw error;
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          // 即使 API 失敗也要清除本地狀態
          console.error("Logout API error:", error);
        } finally {
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
          });
          
          toast.success("已成功登出");
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem("access_token");
        const userStr = localStorage.getItem("user");
        
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr);
            set({
              user,
              token,
              isAuthenticated: true,
            });
            
            // 驗證 token 是否仍然有效
            await authAPI.getCurrentUser();
          } catch (error) {
            // Token 無效，清除本地狀態
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            set({
              user: null,
              token: null,
              isAuthenticated: false,
            });
          }
        }
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
