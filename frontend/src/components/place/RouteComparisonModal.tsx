"use client";

import { useState } from "react";
import { Modal } from "@/components/ui";
import { Button } from "@/components/ui";
import { RouteInfo } from "@/lib/utils/routeCalculation";
import { OSRMRoute } from "@/lib/services/osrmClient";

interface RouteComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  routes: RouteInfo[];
  bestRoute: RouteInfo;
  summary: {
    fastest: RouteInfo;
    shortest: RouteInfo;
    balanced: RouteInfo;
  };
  placeName: string;
}

export function RouteComparisonModal({
  isOpen,
  onClose,
  routes,
  bestRoute,
  summary,
  placeName
}: RouteComparisonModalProps) {
  const [selectedRoute, setSelectedRoute] = useState<RouteInfo>(bestRoute);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');

  const getRouteType = (route: RouteInfo): string => {
    if (route === summary.fastest) return '最快路線';
    if (route === summary.shortest) return '最短路線';
    if (route === summary.balanced) return '平衡路線';
    return '替代路線';
  };

  const getRouteTypeColor = (route: RouteInfo): string => {
    if (route === summary.fastest) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    if (route === summary.shortest) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    if (route === summary.balanced) return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
    return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
            路線比較 - {placeName}
          </h2>
          <div className="flex space-x-2">
            <Button
              size="sm"
              variant={viewMode === 'list' ? 'default' : 'outline'}
              onClick={() => setViewMode('list')}
            >
              列表
            </Button>
            <Button
              size="sm"
              variant={viewMode === 'map' ? 'default' : 'outline'}
              onClick={() => setViewMode('map')}
            >
              地圖
            </Button>
          </div>
        </div>

        {viewMode === 'list' ? (
          <div className="space-y-4">
            {/* 路線摘要 */}
            <div className="grid grid-cols-3 gap-3 mb-6">
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-center justify-center mb-1">
                  <span className="mr-1">⚡</span>
                  <span className="font-medium text-green-800 dark:text-green-300">最快路線</span>
                </div>
                <div className="text-sm text-green-700 dark:text-green-400">
                  <div>{summary.fastest.formatted.distance}</div>
                  <div>{summary.fastest.formatted.duration}</div>
                </div>
              </div>
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-center justify-center mb-1">
                  <span className="mr-1">📏</span>
                  <span className="font-medium text-blue-800 dark:text-blue-300">最短路線</span>
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-400">
                  <div>{summary.shortest.formatted.distance}</div>
                  <div>{summary.shortest.formatted.duration}</div>
                </div>
              </div>
              <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <div className="flex items-center justify-center mb-1">
                  <span className="mr-1">⚖️</span>
                  <span className="font-medium text-purple-800 dark:text-purple-300">平衡路線</span>
                </div>
                <div className="text-sm text-purple-700 dark:text-purple-400">
                  <div>{summary.balanced.formatted.distance}</div>
                  <div>{summary.balanced.formatted.duration}</div>
                </div>
              </div>
            </div>

            {/* 詳細路線列表 */}
            <div className="space-y-2">
              <h3 className="font-medium text-slate-900 dark:text-white">所有路線</h3>
              {routes.map((route, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedRoute === route
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
                  onClick={() => setSelectedRoute(route)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getRouteTypeColor(route)}`}>
                        {getRouteType(route)}
                      </div>
                      {route.isRealTime && (
                        <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded text-xs">
                          即時
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-slate-900 dark:text-white">
                        {route.formatted.distance}
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-300">
                        {route.formatted.duration}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 選中路線詳細資訊 */}
            {selectedRoute && (
              <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <h4 className="font-medium text-slate-900 dark:text-white mb-2">
                  選中路線詳細資訊
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-600 dark:text-slate-400">距離:</span>
                    <span className="ml-2 font-medium text-slate-900 dark:text-white">
                      {selectedRoute.formatted.distance}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-600 dark:text-slate-400">時間:</span>
                    <span className="ml-2 font-medium text-slate-900 dark:text-white">
                      {selectedRoute.formatted.duration}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-600 dark:text-slate-400">路線類型:</span>
                    <span className="ml-2 font-medium text-slate-900 dark:text-white">
                      {getRouteType(selectedRoute)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-600 dark:text-slate-400">數據來源:</span>
                    <span className="ml-2 font-medium text-slate-900 dark:text-white">
                      {selectedRoute.isRealTime ? 'OSRM 即時' : '估算'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-96 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
            <div className="text-center text-slate-500 dark:text-slate-400">
              <div className="text-lg mb-2">🗺️</div>
              <div>地圖視圖功能開發中...</div>
              <div className="text-sm mt-1">將顯示路線幾何和替代路線比較</div>
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3 mt-6">
          <Button variant="outline" onClick={onClose}>
            關閉
          </Button>
          <Button onClick={() => {
            // TODO: 實現選擇路線功能
            console.log('選擇路線:', selectedRoute);
            onClose();
          }}>
            選擇此路線
          </Button>
        </div>
      </div>
    </Modal>
  );
}
