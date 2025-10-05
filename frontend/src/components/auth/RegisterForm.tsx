"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button, Input } from "@/components/ui";
import { useAuthStore } from "@/stores/authStore";
import { RegisterRequest } from "@/lib/types/auth";
import { GoogleLoginButton } from "./GoogleLoginButton";

const registerSchema = z.object({
  email: z.string().email("請輸入有效的電子郵件地址"),
  username: z.string().min(2, "使用者名稱至少需要2個字符").max(20, "使用者名稱不能超過20個字符"),
  password: z.string().min(6, "密碼至少需要6個字符"),
  confirmPassword: z.string(),
  terms: z.boolean().refine((val) => val === true, "請同意服務條款"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "密碼確認不匹配",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterForm: React.FC = () => {
  const router = useRouter();
  const { register: registerUser, isLoading, isAuthenticated } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  // 如果已經登入，跳轉到首頁
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      console.log("提交註冊表單:", data);
      await registerUser(data);
      console.log("註冊成功");
      // 註冊成功後跳轉到首頁
      router.push("/");
    } catch (error) {
      console.error("註冊表單錯誤:", error);
      // 錯誤已在 store 中處理
    }
  };

  return (
    <div className="w-full space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
          建立新帳戶
        </h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
          已有帳戶？{" "}
          <Link href="/login" className="font-medium text-primary hover:text-primary/80">
            立即登入
          </Link>
        </p>
      </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            id="email"
            label="電子郵件"
            type="email"
            placeholder="your@example.com"
            {...register("email")}
            error={errors.email?.message}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
              </svg>
            }
          />

          <Input
            id="username"
            label="使用者名稱"
            type="text"
            placeholder="您的名稱"
            {...register("username")}
            error={errors.username?.message}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            }
          />

          <Input
            id="password"
            label="密碼"
            type="password"
            placeholder="設定您的密碼"
            {...register("password")}
            error={errors.password?.message}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          />

          <Input
            id="confirmPassword"
            label="確認密碼"
            type="password"
            placeholder="再次輸入密碼"
            {...register("confirmPassword")}
            error={errors.confirmPassword?.message}
            icon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            }
          />

          <div className="flex items-center">
            <input
              id="terms"
              type="checkbox"
              {...register("terms")}
              className="h-4 w-4 text-primary focus:ring-primary border-slate-300 rounded"
            />
            <label htmlFor="terms" className="ml-2 block text-sm text-slate-900 dark:text-slate-300">
              我同意{" "}
              <Link href="/terms" className="text-primary hover:text-primary/80">
                服務條款
              </Link>{" "}
              與{" "}
              <Link href="/privacy" className="text-primary hover:text-primary/80">
                隱私政策
              </Link>
            </label>
          </div>
          {errors.terms && (
            <p className="text-sm text-red-600 dark:text-red-400">{errors.terms.message}</p>
          )}

          <Button
            type="submit"
            className="w-full"
            loading={isLoading}
            disabled={isLoading}
          >
            {isLoading ? "註冊中..." : "建立帳戶"}
          </Button>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-300 dark:border-slate-700" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-slate-900 text-slate-500">或</span>
              </div>
            </div>

            <div className="mt-6">
              <GoogleLoginButton className="w-full" />
            </div>
          </div>
        </form>
    </div>
  );
};
