"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface LoadingProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  className?: string;
  variant?: "spinner" | "dots" | "pulse";
}

export const Loading: React.FC<LoadingProps> = ({
  size = "md",
  text,
  className,
  variant = "spinner"
}) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8"
  };

  const textSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg"
  };

  const renderSpinner = () => (
    <div className={cn("animate-spin rounded-full border-2 border-slate-300 border-t-primary-500", sizeClasses[size])} />
  );

  const renderDots = () => (
    <div className="flex space-x-1">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            "bg-primary-500 rounded-full animate-pulse",
            size === "sm" ? "w-1 h-1" : size === "md" ? "w-2 h-2" : "w-3 h-3"
          )}
          style={{ animationDelay: `${i * 0.1}s` }}
        />
      ))}
    </div>
  );

  const renderPulse = () => (
    <div className={cn("bg-primary-500 rounded-full animate-pulse", sizeClasses[size])} />
  );

  const renderLoading = () => {
    switch (variant) {
      case "dots":
        return renderDots();
      case "pulse":
        return renderPulse();
      default:
        return renderSpinner();
    }
  };

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div className="flex flex-col items-center space-y-3">
        {renderLoading()}
        {text && (
          <p className={cn("text-slate-600 dark:text-slate-400 font-medium", textSizeClasses[size])}>
            {text}
          </p>
        )}
      </div>
    </div>
  );
};

// 全頁面載入組件
export const PageLoading: React.FC<{ text?: string }> = ({ text = "載入中..." }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
      <Loading size="lg" text={text} />
    </div>
  );
};

// 按鈕載入組件
export const ButtonLoading: React.FC<{ size?: "sm" | "md" | "lg" }> = ({ size = "sm" }) => {
  return (
    <div className={cn("animate-spin rounded-full border-2 border-white border-t-transparent", sizeClasses[size])} />
  );
};

// 卡片載入組件
export const CardLoading: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn("card p-6 animate-pulse", className)}>
      <div className="space-y-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-5/6"></div>
      </div>
    </div>
  );
};

// 列表載入組件
export const ListLoading: React.FC<{ count?: number; className?: string }> = ({ count = 3, className }) => {
  return (
    <div className={cn("space-y-4", className)}>
      {Array.from({ length: count }).map((_, index) => (
        <CardLoading key={index} />
      ))}
    </div>
  );
};
