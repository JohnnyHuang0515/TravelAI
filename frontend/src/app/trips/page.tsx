"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { TripList } from "@/components/trip";
import { Button } from "@/components/ui";
import { Navbar } from "@/components/layout/Navbar";

interface TripSummary {
  id: string;
  title: string;
  description: string | null;
  destination: string;
  duration_days: number;
  start_date: string;
  end_date: string;
  is_public: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export default function MyTripsPage() {
  const router = useRouter();
  const [trips, setTrips] = useState<TripSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadTrips();
  }, [currentPage]);

  const loadTrips = async () => {
    try {
      setLoading(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模擬資料
      const mockTrips: TripSummary[] = [
        {
          id: "1",
          title: "台北三日遊",
          description: "探索台北的經典景點，品嚐道地美食",
          destination: "台北市",
          duration_days: 3,
          start_date: "2024-02-15",
          end_date: "2024-02-17",
          is_public: true,
          view_count: 25,
          created_at: "2024-01-15T10:00:00Z",
          updated_at: "2024-01-20T15:30:00Z"
        },
        {
          id: "2",
          title: "高雄美食之旅",
          description: "品嚐高雄最著名的夜市美食和小吃",
          destination: "高雄市",
          duration_days: 2,
          start_date: "2024-03-01",
          end_date: "2024-03-02",
          is_public: false,
          view_count: 0,
          created_at: "2024-01-10T14:20:00Z",
          updated_at: "2024-01-10T14:20:00Z"
        },
        {
          id: "3",
          title: "花蓮自然風光",
          description: "欣賞花蓮的壯麗山景和海岸線",
          destination: "花蓮縣",
          duration_days: 4,
          start_date: "2024-04-10",
          end_date: "2024-04-13",
          is_public: true,
          view_count: 12,
          created_at: "2024-01-05T09:15:00Z",
          updated_at: "2024-01-18T11:45:00Z"
        }
      ];

      setTrips(mockTrips);
      setTotalPages(1);
    } catch (error) {
      console.error("載入行程失敗:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewTrip = (tripId: string) => {
    router.push(`/trips/${tripId}`);
  };

  const handleEditTrip = (tripId: string) => {
    router.push(`/trips/${tripId}/edit`);
  };

  const handleShareTrip = async (tripId: string) => {
    try {
      // 模擬分享功能
      const shareUrl = `${window.location.origin}/trips/public/${tripId}`;
      await navigator.clipboard.writeText(shareUrl);
      alert("分享連結已複製到剪貼簿！");
    } catch (error) {
      console.error("分享失敗:", error);
      alert("分享失敗，請稍後再試");
    }
  };

  const handleDeleteTrip = async (tripId: string) => {
    if (!confirm("確定要刪除這個行程嗎？此操作無法復原。")) {
      return;
    }

    try {
      // 模擬刪除 API
      setTrips(prev => prev.filter(trip => trip.id !== tripId));
      alert("行程已刪除");
    } catch (error) {
      console.error("刪除失敗:", error);
      alert("刪除失敗，請稍後再試");
    }
  };

  const handleCreateTrip = () => {
    router.push("/plan/start");
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col">
      <Navbar />
      <main className="flex-1 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-8">
        {/* 頁面標題 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              我的行程
            </h1>
            <p className="text-slate-600 dark:text-slate-300">
              管理您已儲存的旅行行程
            </p>
          </div>
          
          <Button onClick={handleCreateTrip} size="lg">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            新增行程
          </Button>
        </div>

        {/* 行程列表 */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
          <TripList
            trips={trips}
            loading={loading}
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            onViewTrip={handleViewTrip}
            onEditTrip={handleEditTrip}
            onShareTrip={handleShareTrip}
            onDeleteTrip={handleDeleteTrip}
            onCreateTrip={handleCreateTrip}
          />
        </div>
        </div>
      </main>
    </div>
  );
}
