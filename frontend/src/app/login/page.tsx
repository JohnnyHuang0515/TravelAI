import { LoginForm } from "@/components/auth";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col">
      {/* 主要內容 */}
      <div className="flex flex-1">
        {/* 左側：品牌展示 */}
        <div className="hidden lg:flex lg:w-1/2 gradient-hero relative overflow-hidden">
          <div className="absolute inset-0 bg-black/30"></div>
          <div className="relative z-10 flex flex-col justify-center px-12 text-white">
            <div className="max-w-md animate-fade-in">
              <h1 className="text-5xl font-bold mb-6">
                歡迎回到 TravelAI
              </h1>
              <p className="text-xl text-white/90 mb-10 leading-relaxed">
                繼續您的旅行規劃之旅，讓 AI 為您打造完美的行程體驗
              </p>
              
              <div className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-lg font-medium">個人化行程推薦</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-lg font-medium">即時景點推薦</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-lg font-medium">對話式行程調整</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* 裝飾性元素 */}
          <div className="absolute top-20 right-20 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
          <div className="absolute bottom-20 left-20 w-32 h-32 bg-primary-300/20 rounded-full blur-2xl"></div>
        </div>

        {/* 右側：登入表單 */}
        <div className="w-full lg:w-1/2 flex items-center justify-center px-6 py-12">
          <div className="w-full max-w-md">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 animate-scale-in">
              <LoginForm />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}