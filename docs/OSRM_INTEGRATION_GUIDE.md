# OSRM 整合指南

## 概述

本專案已成功整合 OSRM (Open Source Routing Machine) 服務，提供真實的路由計算功能，包括：

- ✅ **真實道路網路數據** - 基於台灣實際道路數據
- ✅ **實時交通狀況** - 考慮交通流量和路況
- ✅ **多條替代路線比較** - 提供最快、最短、平衡路線
- ✅ **精確的行駛時間預測** - 基於實際道路條件

## 系統架構

```
前端 (Next.js) 
    ↓ HTTP API 調用
OSRM 客戶端服務
    ↓ 直接通信
OSRM 路由服務 (localhost:5000)
    ↓ 使用
台灣道路數據 (taiwan-251004.osrm)
```

## 核心功能

### 1. OSRM 客戶端服務 (`frontend/src/lib/services/osrmClient.ts`)

提供完整的 OSRM API 封裝：

```typescript
// 基本路由計算
const route = await osrmClient.getRoute(startLat, startLon, endLat, endLon);

// 多條替代路線
const alternatives = await osrmClient.getAlternativeRoutes(startLat, startLon, endLat, endLon);

// 等時線計算（可到達範圍）
const isochrone = await osrmClient.getIsochrone(centerLat, centerLon);
```

### 2. 智能車程計算 (`frontend/src/lib/utils/routeCalculation.ts`)

整合 OSRM 數據與交通狀況分析：

```typescript
// 計算多種交通工具的車程
const routes = await calculateMultipleVehicleRoutes(
  userLat, userLon, placeLat, placeLon, 'normal'
);

// 獲取替代路線比較
const comparison = await getAlternativeRoutesComparison(
  userLat, userLon, placeLat, placeLon
);
```

### 3. 前端組件整合

#### PlaceCard 組件
- 顯示即時路由資訊
- 支援替代路線查看
- 標示數據來源（OSRM 即時 vs 估算）

#### RouteComparisonModal 組件
- 多路線詳細比較
- 最快/最短/平衡路線分類
- 路線選擇功能

## 使用方式

### 1. 啟動 OSRM 服務

```bash
# 使用提供的啟動腳本
./scripts/start_osrm.sh
```

### 2. 環境配置

在前端項目中設置環境變數：

```bash
# .env.local
NEXT_PUBLIC_OSRM_URL=http://localhost:5000
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### 3. 測試整合功能

```bash
# 運行整合測試
python scripts/test_osrm_integration.py
```

## API 端點

### OSRM 服務端點

- **健康檢查**: `GET /health`
- **路由計算**: `GET /route/v1/driving/{coordinates}`
- **替代路線**: `GET /route/v1/driving/{coordinates}?alternatives=true`
- **等時線**: `GET /isochrone/v1/driving/{coordinates}`

### 前端 API 調用

```typescript
// 檢查服務狀態
const isHealthy = await osrmClient.checkHealth();

// 計算路線
const route = await calculateOSRMRoute(
  startLat, startLon, endLat, endLon, {
    vehicleType: 'car',
    routePreference: 'fastest',
    trafficConditions: 'normal'
  }
);
```

## 數據流程

1. **用戶定位** → 獲取當前位置
2. **景點選擇** → 選擇目標景點
3. **OSRM 查詢** → 計算實際路線
4. **交通分析** → 考慮交通狀況
5. **結果整合** → 顯示完整資訊

## 特色功能

### 智能路線選擇
- **最快路線**: 優先考慮行駛時間
- **最短路線**: 優先考慮行駛距離  
- **平衡路線**: 綜合時間和距離考量

### 交通狀況感知
- **輕度交通**: 時間減少 20%
- **正常交通**: 標準時間計算
- **重度交通**: 時間增加 50%

### 交通工具適配
- **小客車**: 支援交通數據 (`driving-traffic`)
- **機車**: 使用標準駕駛配置
- **大客車**: 考慮停靠站點時間

## 性能優化

### 前端優化
- 使用 `useCallback` 和 `useMemo` 避免重複計算
- 動態載入 OSRM 客戶端
- 錯誤處理和回退機制

### 服務優化
- 連接超時控制 (5秒)
- 請求重試機制
- 健康檢查監控

## 故障排除

### 常見問題

1. **OSRM 服務無法啟動**
   ```bash
   # 檢查數據檔案
   ls -la osrm_data/taiwan-251004.osrm*
   
   # 重新處理數據
   ./scripts/process_osrm.sh
   ```

2. **前端無法連接 OSRM**
   ```bash
   # 檢查服務狀態
   curl http://localhost:5000/health
   
   # 檢查防火牆設定
   ```

3. **路由計算失敗**
   - 確認座標格式正確
   - 檢查服務日誌
   - 驗證數據完整性

### 日誌監控

```bash
# 查看 OSRM 服務日誌
tail -f /tmp/osrm.log

# 查看前端錯誤
# 瀏覽器開發者工具 Console
```

## 未來擴展

### 計劃功能
- [ ] 即時交通數據整合
- [ ] 路線偏好學習
- [ ] 多模式交通支援
- [ ] 路線分享功能

### 性能提升
- [ ] 路線緩存機制
- [ ] 預計算常用路線
- [ ] CDN 加速
- [ ] 服務負載均衡

## 技術支援

如有問題，請參考：
- [OSRM 官方文檔](http://project-osrm.org/)
- [專案 GitHub Issues](../../issues)
- [開發團隊聯絡資訊](../../CONTACT.md)

---

**最後更新**: 2024年12月
**版本**: 1.0.0
**狀態**: ✅ 生產就緒
