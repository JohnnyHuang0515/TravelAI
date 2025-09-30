"use client";

import { ReactNode } from "react";

interface SimpleLayoutProps {
  children: ReactNode;
  showNavbar?: boolean;
  showFooter?: boolean;
  className?: string;
}

export const SimpleLayout: React.FC<SimpleLayoutProps> = ({
  children,
  showNavbar = true,
  showFooter = true,
  className = "",
}) => {
  return (
    <div className={`min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col ${className}`}>
      {showNavbar && (
        <nav className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <span className="text-xl font-bold text-slate-900 dark:text-white">TravelAI</span>
              </div>
            </div>
          </div>
        </nav>
      )}
      <main className="flex-1">
        {children}
      </main>
      {showFooter && (
        <footer className="bg-slate-900 dark:bg-slate-950 text-white py-12">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center text-slate-400">
              <p>&copy; 2024 TravelAI. All rights reserved.</p>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
};
