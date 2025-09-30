"use client";

import { Day, Visit, Accommodation } from "@/lib/types/trip";
import { Card } from "@/components/ui";

interface TripTimelineProps {
  days: Day[];
  editable?: boolean;
  onModify?: (dayIndex: number, visitIndex: number) => void;
}

export function TripTimeline({ days, editable = false, onModify }: TripTimelineProps) {
  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('zh-TW', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    });
  };

  return (
    <div className="space-y-8">
      {days.map((day, dayIndex) => (
        <div key={day.day} className="relative">
          {/* 日期標題 */}
          <div className="flex items-center mb-6">
            <div className="bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-4 py-2 rounded-full text-sm font-medium">
              第 {day.day} 天
            </div>
            <div className="ml-4 text-lg font-semibold text-slate-900 dark:text-white">
              {formatDate(day.date)}
            </div>
          </div>

          {/* 行程時間軸 */}
          <div className="relative">
            {/* 垂直線 */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700"></div>

            <div className="space-y-6">
              {day.visits.map((visit, visitIndex) => (
                <div key={visitIndex} className="relative flex items-start space-x-4">
                  {/* 時間點 */}
                  <div className="relative z-10">
                    <div className="w-12 h-12 bg-white dark:bg-slate-800 border-4 border-primary-500 rounded-full flex items-center justify-center shadow-lg">
                      <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                    </div>
                  </div>

                  {/* 行程內容 */}
                  <div className="flex-1 pb-6">
                    <Card className="p-4 hover:shadow-lg transition-shadow">
                      <div className="space-y-3">
                        {/* 景點名稱和時間 */}
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">
                              {visit.name}
                            </h3>
                            <div className="flex items-center space-x-4 text-sm text-slate-600 dark:text-slate-300">
                              <div className="flex items-center space-x-1">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>到達: {formatTime(visit.eta)}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span>離開: {formatTime(visit.etd)}</span>
                              </div>
                            </div>
                          </div>
                          
                          {editable && (
                            <button
                              onClick={() => onModify?.(dayIndex, visitIndex)}
                              className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            </button>
                          )}
                        </div>

                        {/* 停留時間和交通時間 */}
                        <div className="flex items-center space-x-6 text-sm text-slate-500 dark:text-slate-400">
                          <div className="flex items-center space-x-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>停留 {visit.stay_minutes} 分鐘</span>
                          </div>
                          
                          {visit.travel_minutes > 0 && (
                            <div className="flex items-center space-x-1">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                              </svg>
                              <span>交通 {visit.travel_minutes} 分鐘</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
              ))}

              {/* 住宿資訊 */}
              {day.accommodation && (
                <div className="relative flex items-start space-x-4">
                  {/* 住宿圖標 */}
                  <div className="relative z-10">
                    <div className="w-12 h-12 bg-white dark:bg-slate-800 border-4 border-green-500 rounded-full flex items-center justify-center shadow-lg">
                      <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 21v-4a2 2 0 012-2h4a2 2 0 012 2v4" />
                      </svg>
                    </div>
                  </div>

                  {/* 住宿內容 */}
                  <div className="flex-1">
                    <Card className="p-4 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                          {day.accommodation.name}
                        </h3>
                        <p className="text-sm text-slate-600 dark:text-slate-300">
                          {day.accommodation.address}
                        </p>
                        <div className="flex items-center space-x-4 text-sm text-slate-500 dark:text-slate-400">
                          <div className="flex items-center space-x-1">
                            <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            <span>{day.accommodation.rating}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                            </svg>
                            <span>NT$ {day.accommodation.price}</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
