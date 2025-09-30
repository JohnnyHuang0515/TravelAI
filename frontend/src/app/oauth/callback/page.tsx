"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/stores";
import { PageLoading } from "@/components/ui";
import { AppLayout } from "@/components/layout";

export default function OAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setToken } = useAuthStore();

  useEffect(() => {
    const token = searchParams.get("token");
    const error = searchParams.get("error");

    if (error) {
      // 處理錯誤
      console.error("OAuth error:", error);
      router.push(`/login?error=${encodeURIComponent(error)}`);
      return;
    }

    if (token) {
      // 儲存 token
      setToken(token);
      
      // 重定向到首頁或儀表板
      router.push("/");
    } else {
      // 沒有 token，重定向到登入頁面
      router.push("/login");
    }
  }, [searchParams, router, setToken]);

  return (
    <AppLayout showNavbar={false} showFooter={false}>
      <PageLoading text="正在處理 Google 登入..." />
    </AppLayout>
  );
}
