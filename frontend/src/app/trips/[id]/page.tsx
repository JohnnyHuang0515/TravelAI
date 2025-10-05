"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { TripTimeline } from "@/components/trip/TripTimeline";
import { PlaceMap } from "@/components/place/PlaceMap";
import { Modal } from "@/components/ui";
import { Button } from "@/components/ui";
import { AppLayout } from "@/components/layout";
import { Trip } from "@/lib/types/trip";

export default function TripDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    loadTrip();
  }, [params.id]);

  const loadTrip = async () => {
    try {
      setLoading(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模擬行程資料
      const mockTrip: Trip = {
        id: params.id as string,
        user_id: "user123",
        title: "台北三日遊",
        description: "探索台北的經典景點，品嚐道地美食，體驗台灣文化",
        destination: "台北市",
        duration_days: 3,
        start_date: "2024-02-15",
        end_date: "2024-02-17",
        is_public: true,
        share_token: "abc123def456",
        view_count: 25,
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-20T15:30:00Z",
        itinerary_data: {
          days: [
            {
              day: 1,
              date: "2024-02-15",
              visits: [
                {
                  place_id: "1",
                  name: "台北101",
                  eta: "09:00",
                  etd: "11:00",
                  travel_minutes: 0,
                  stay_minutes: 120
                },
                {
                  place_id: "2",
                  name: "信義商圈",
                  eta: "11:30",
                  etd: "14:30",
                  travel_minutes: 30,
                  stay_minutes: 180
                },
                {
                  place_id: "3",
                  name: "松山文創園區",
                  eta: "15:00",
                  etd: "17:00",
                  travel_minutes: 30,
                  stay_minutes: 120
                }
              ],
              accommodation: {
                name: "台北君悅酒店",
                address: "台北市信義區松仁路100號",
                rating: 4.5,
                price: 8000
              }
            },
            {
              day: 2,
              date: "2024-02-16",
              visits: [
                {
                  place_id: "4",
                  name: "故宮博物院",
                  eta: "09:00",
                  etd: "12:00",
                  travel_minutes: 0,
                  stay_minutes: 180
                },
                {
                  place_id: "5",
                  name: "士林夜市",
                  eta: "18:00",
                  etd: "21:00",
                  travel_minutes: 60,
                  stay_minutes: 180
                }
              ],
              accommodation: {
                name: "台北君悅酒店",
                address: "台北市信義區松仁路100號",
                rating: 4.5,
                price: 8000
              }
            },
            {
              day: 3,
              date: "2024-02-17",
              visits: [
                {
                  place_id: "6",
                  name: "九份老街",
                  eta: "09:00",
                  etd: "15:00",
                  travel_minutes: 0,
                  stay_minutes: 360
                }
              ]
            }
          ]
        }
      };

      setTrip(mockTrip);
    } catch (error) {
      console.error("載入行程失敗:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    router.push(`/trips/${params.id}/edit`);
  };

  const handleShare = () => {
    setShowShareModal(true);
  };

  const handleDelete = () => {
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    try {
      // 模擬刪除 API
      router.push('/trips');
      alert("行程已刪除");
    } catch (error) {
      console.error("刪除失敗:", error);
      alert("刪除失敗，請稍後再試");
    }
  };

  const handleCopyTrip = () => {
    // 模擬複製行程
    alert("行程已複製到您的帳戶！");
  };

  const handleDownloadTrip = () => {
    // 模擬下載行程
    alert("行程下載功能開發中...");
  };

  const copyShareLink = async () => {
    const shareUrl = `${window.location.origin}/trips/public/${trip?.share_token}`;
    try {
      await navigator.clipboard.writeText(shareUrl);
      alert("分享連結已複製到剪貼簿！");
    } catch (error) {
      console.error("複製失敗:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-slate-600 dark:text-slate-300">載入行程中...</p>
        </div>
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-slate-600 dark:text-slate-300">找不到此行程</p>
          <Button onClick={() => router.push('/trips')} className="mt-4">
            返回行程列表
          </Button>
        </div>
      </div>
    );
  }

  // 提取所有景點用於地圖顯示
  const allPlaces = trip.itinerary_data.days.flatMap(day => 
    day.visits.map(visit => ({
      id: visit.place_id,
      name: visit.name,
      location: {
        lat: 25.0330 + Math.random() * 0.1,
        lon: 121.5654 + Math.random() * 0.1
      }
    }))
  );

  return (
    <AppLayout showFooter={false}>
      <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-8">
        {/* 頁面標題和操作 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              {trip.title}
            </h1>
            <p className="text-slate-600 dark:text-slate-300">
              {trip.destination} • {trip.duration_days} 天 • {trip.view_count} 次瀏覽
            </p>
            {trip.description && (
              <p className="text-slate-500 dark:text-slate-400 mt-2">
                {trip.description}
              </p>
            )}
          </div>
          
          <div className="flex space-x-3">
            <Button onClick={handleEdit} variant="outline">
              編輯
            </Button>
            <Button onClick={handleShare} variant="outline">
              分享
            </Button>
            <Button onClick={handleCopyTrip} variant="outline">
              複製
            </Button>
            <Button onClick={handleDownloadTrip} variant="outline">
              下載
            </Button>
            <Button onClick={handleDelete} variant="outline" className="text-red-600 hover:text-red-700">
              刪除
            </Button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* 左側：行程時間軸 */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
              <TripTimeline 
                days={trip.itinerary_data.days}
                editable={true}
                onModify={(dayIndex, visitIndex) => {
                  console.log(`修改第 ${dayIndex + 1} 天第 ${visitIndex + 1} 個景點`);
                }}
              />
            </div>
          </div>

          {/* 右側：地圖 */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-4">
                行程地圖
              </h2>
              <PlaceMap
                places={allPlaces}
                className="h-96"
              />
            </div>
          </div>
        </div>

        {/* 分享模態框 */}
        <Modal
          isOpen={showShareModal}
          onClose={() => setShowShareModal(false)}
          title="分享行程"
          size="md"
        >
          <div className="space-y-4">
            <p className="text-slate-600 dark:text-slate-300">
              分享這個行程給朋友，讓他們也能查看您的精彩旅程！
            </p>
            
            <div className="bg-slate-100 dark:bg-slate-700 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600 dark:text-slate-300 font-mono">
                  {window.location.origin}/trips/public/{trip.share_token}
                </span>
                <Button size="sm" onClick={copyShareLink}>
                  複製連結
                </Button>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="public"
                checked={trip.is_public}
                onChange={(e) => {
                  setTrip(prev => prev ? { ...prev, is_public: e.target.checked } : null);
                }}
                className="w-4 h-4 text-primary-600 border-slate-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="public" className="text-sm text-slate-600 dark:text-slate-300">
                設為公開行程
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <Button variant="outline" onClick={() => setShowShareModal(false)}>
                取消
              </Button>
              <Button onClick={() => setShowShareModal(false)}>
                完成
              </Button>
            </div>
          </div>
        </Modal>

        {/* 刪除確認模態框 */}
        <Modal
          isOpen={showDeleteModal}
          onClose={() => setShowDeleteModal(false)}
          title="確認刪除"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-slate-600 dark:text-slate-300">
              確定要刪除「{trip.title}」嗎？此操作無法復原。
            </p>
            
            <div className="flex justify-end space-x-3 pt-4">
              <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
                取消
              </Button>
              <Button onClick={confirmDelete} className="bg-red-600 hover:bg-red-700">
                刪除
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </AppLayout>
  );
}
