import Link from "next/link";
import { Button } from "@/components/ui";
import { AppLayout } from "@/components/layout";

export default function Home() {
  return (
    <AppLayout>

      {/* Hero Section */}
      <section className="relative gradient-hero overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-24 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* 左側內容 */}
            <div className="animate-fade-in">
              <h1 className="text-5xl lg:text-7xl font-bold text-white mb-6 leading-tight">
                智慧行程規劃
                <span className="text-primary-200 block">讓旅行更簡單</span>
              </h1>
              
              <p className="text-xl text-white/90 mb-10 leading-relaxed max-w-2xl">
                使用 AI 技術為您量身打造完美行程，從景點推薦到路線規劃，一次搞定所有旅行需求
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-16">
                <Link href="/login">
                  <Button size="xl" className="text-lg px-10 py-5 w-full sm:w-auto bg-white text-primary-600 hover:bg-white/90 shadow-large">
                    開始規劃行程
                  </Button>
                </Link>
                <Link href="/login">
                  <Button variant="outline" size="xl" className="text-lg px-10 py-5 w-full sm:w-auto border-white/30 text-white hover:bg-white/10">
                    探索附近景點
                  </Button>
                </Link>
              </div>

              {/* 統計數據 */}
              <div className="grid grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="text-4xl font-bold text-white mb-1">10K+</div>
                  <div className="text-sm text-white/80">活躍用戶</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-white mb-1">50K+</div>
                  <div className="text-sm text-white/80">成功行程</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-white mb-1">4.9</div>
                  <div className="text-sm text-white/80">用戶評分</div>
                </div>
              </div>
            </div>

            {/* 右側圖片/展示 */}
            <div className="relative animate-slide-up">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-large p-8 border border-white/20">
                <div className="space-y-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="h-4 bg-white/20 rounded w-3/4"></div>
                    <div className="h-4 bg-white/20 rounded w-1/2"></div>
                    <div className="h-4 bg-white/20 rounded w-2/3"></div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/10 rounded-lg p-4">
                      <div className="w-8 h-8 bg-white/20 rounded-lg mb-2"></div>
                      <div className="h-3 bg-white/20 rounded w-3/4 mb-1"></div>
                      <div className="h-2 bg-white/20 rounded w-1/2"></div>
                    </div>
                    <div className="bg-white/10 rounded-lg p-4">
                      <div className="w-8 h-8 bg-white/20 rounded-lg mb-2"></div>
                      <div className="h-3 bg-white/20 rounded w-3/4 mb-1"></div>
                      <div className="h-2 bg-white/20 rounded w-1/2"></div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 裝飾性元素 */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-primary-300/20 rounded-full blur-xl"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-white dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-6">
              為什麼選擇我們？
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed">
              我們提供最先進的 AI 技術，讓您的旅行規劃變得簡單而精彩
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            <div className="card card-hover p-8 animate-fade-in">
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">AI 智慧推薦</h3>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
                根據您的興趣和偏好，智能推薦最適合的景點和活動，讓每次旅行都獨一無二
              </p>
            </div>

            <div className="card card-hover p-8 animate-fade-in" style={{ animationDelay: '0.1s' }}>
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">附近景點</h3>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
                即時定位推薦周邊熱門景點，發現更多精彩去處，讓您的旅程充滿驚喜
              </p>
            </div>

            <div className="card card-hover p-8 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-2xl flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">對話式修改</h3>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
                透過自然對話輕鬆調整行程，讓規劃過程更直觀，隨時滿足您的需求變化
              </p>
            </div>
          </div>
        </div>
      </section>

    </AppLayout>
  );
}
