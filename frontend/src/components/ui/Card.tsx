import React from "react";
import { cn } from "@/lib/utils";
import { CardProps, CardHeaderProps, CardContentProps } from "@/lib/types/ui";

export const Card: React.FC<CardProps> = ({ children, className }) => {
  return (
    <div className={cn("card card-hover", className)}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => {
  return (
    <div className={cn("px-6 py-5 border-b border-slate-200 dark:border-slate-700", className)}>
      {children}
    </div>
  );
};

export const CardContent: React.FC<CardContentProps> = ({ children, className }) => {
  return (
    <div className={cn("px-6 py-5", className)}>
      {children}
    </div>
  );
};
