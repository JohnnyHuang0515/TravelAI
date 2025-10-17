# 公車資料整合指南

本文件說明如何將宜蘭公車資料整合到 TravelAI 專案中，包括 OSRM 路由引擎的整合。

## 📊 資料包內容

### OSRM 路由資料
- `taiwan-250923.osm.pbf` - 台灣地圖資料
- `taiwan-250923.osrm*` - 預處理的路由引擎檔案

### 公車資料檔案
- `routes.csv` - 路線基本資訊 (66條路線)
- `stations.csv` - 站點座標資料 (5,718筆站點記錄)
- `trips.csv` - 班次發車時間 (933個班次)
- `stop_times.csv` - 完整時刻表 (31,429筆時刻記錄)

### 處理工具
- `bus_data_manager.py` - 公車資料管理模組
- `database_design.py` - 資料庫設計分析
- `extract_departure_times.py` - 班次時間提取工具

## 🗄️ 資料庫設計

### 新增的資料表

#### 1. `bus_routes` - 公車路線表
```sql
- id (UUID, PK)
- route_id (VARCHAR(50), UNIQUE) - 路線ID
- route_name (VARCHAR(50), UNIQUE) - 路線編號
- departure_stop (VARCHAR(255)) - 起站
- destination_stop (VARCHAR(255)) - 迄站
- route_type (VARCHAR(50)) - 路線類型
- status (VARCHAR(50)) - 營運狀態
```

#### 2. `bus_stations` - 公車站點表
```sql
- id (UUID, PK)
- route_id (UUID, FK) - 路線ID
- station_id (VARCHAR(50)) - 站牌ID
- station_name (VARCHAR(255)) - 站名
- sequence (INTEGER) - 站序
- direction (INTEGER) - 方向 (0: 去程, 1: 回程)
- geom (GEOMETRY) - 站點座標
```

#### 3. `bus_trips` - 公車班次表
```sql
- id (UUID, PK)
- route_id (UUID, FK) - 路線ID
- trip_id (VARCHAR(50)) - 班次ID
- direction (INTEGER) - 方向
- departure_time (TIME) - 發車時間
- departure_station (VARCHAR(255)) - 發車站名
- operating_days (TEXT[]) - 營運日陣列
- is_low_floor (BOOLEAN) - 是否為低地板公車
```

#### 4. `bus_stop_times` - 公車時刻表
```sql
- id (UUID, PK)
- trip_id (UUID, FK) - 班次ID
- station_id (UUID, FK) - 站點ID
- sequence (INTEGER) - 站序
- arrival_time (TIME) - 抵達時間
- departure_time (TIME) - 離站時間
```

#### 5. `transport_connections` - 運輸連接點表
```sql
- id (UUID, PK)
- place_id (UUID, FK) - 景點ID (可選)
- station_id (UUID, FK) - 站點ID (可選)
- connection_type (VARCHAR(50)) - 連接類型
- distance_meters (INTEGER) - 距離
- walking_time_minutes (INTEGER) - 步行時間
- is_accessible (BOOLEAN) - 是否無障礙
```

## 🚀 整合步驟

### 1. 環境準備

確保已安裝必要依賴：
```bash
pip install pandas requests
```

### 2. 執行資料庫遷移

```bash
# 執行資料庫遷移
psql $DATABASE_URL -f migrations/008_add_bus_transport_tables.sql
```

### 3. 匯入公車資料

```bash
# 匯入 CSV 資料到資料庫
python scripts/import_bus_data.py
```

### 4. 啟動 OSRM 服務

```bash
# 啟動 OSRM 路由服務
python scripts/start_osrm_service.py
```

### 5. 執行完整整合

```bash
# 執行完整的整合流程
python scripts/integrate_bus_data.py
```

## 🛠️ 使用範例

### 基本使用

```python
from src.itinerary_planner.infrastructure.persistence.database import get_session
from src.itinerary_planner.infrastructure.routing.bus_routing_service import BusRoutingService

# 建立服務實例
with get_session() as session:
    service = BusRoutingService(session)
    
    # 尋找附近站點
    stations = service.find_nearby_stations(121.7536, 24.7570, 500)
    
    # 規劃路線
    route_plan = service.plan_route(
        start_lon=121.839346, start_lat=24.870935,  # 外澳
        end_lon=121.7536, end_lat=24.7570,          # 宜蘭轉運站
        departure_time=time(8, 0)
    )
```

### 執行範例腳本

```bash
# 執行使用範例
python scripts/bus_routing_example.py
```

## 🔧 API 服務

### BusRoutingService 主要方法

#### `find_nearby_stations(lon, lat, radius)`
尋找指定位置附近的公車站點

#### `plan_route(start_lon, start_lat, end_lon, end_lat, departure_time)`
規劃從起點到終點的完整路線

#### `find_direct_routes(start_station, end_station, departure_time)`
尋找兩站間的直達路線

#### `get_route_schedule(route_name, direction, date)`
取得路線時刻表

### OSRMService 主要方法

#### `route_between_points(start_lon, start_lat, end_lon, end_lat)`
計算兩點間的路由

#### `is_service_running()`
檢查 OSRM 服務是否運行

#### `start_service()` / `stop_service()`
啟動/停止 OSRM 服務

## 📁 檔案結構

```
TravelAI/
├── data/
│   └── osrm/
│       ├── taiwan-250923.osm.pbf
│       ├── taiwan-250923.osrm*
│       └── data/
│           ├── routes.csv
│           ├── stations.csv
│           ├── trips.csv
│           ├── stop_times.csv
│           ├── bus_data_manager.py
│           ├── database_design.py
│           └── extract_departure_times.py
├── src/
│   └── itinerary_planner/
│       └── infrastructure/
│           ├── persistence/
│           │   └── orm_models.py (已更新)
│           └── routing/
│               ├── osrm_service.py (新增)
│               └── bus_routing_service.py (新增)
├── migrations/
│   └── 008_add_bus_transport_tables.sql (新增)
└── scripts/
    ├── import_bus_data.py (新增)
    ├── start_osrm_service.py (新增)
    ├── integrate_bus_data.py (新增)
    └── bus_routing_example.py (新增)
```

## 🚨 注意事項

### OSRM 服務要求
- 需要安裝 OSRM 工具集
- 需要足夠的記憶體運行路由服務
- 建議在生產環境中使用 Docker 容器

### 資料品質
- CSV 資料已進行清理和格式化
- 座標資料使用 WGS84 系統 (EPSG:4326)
- 時間格式統一為 HH:MM

### 效能考量
- 大量資料查詢時建議使用索引
- 空間查詢已優化使用 PostGIS
- 建議定期更新公車資料

## 🔍 故障排除

### 常見問題

1. **OSRM 服務啟動失敗**
   - 檢查 OSRM 是否已安裝
   - 確認資料檔案路徑正確
   - 檢查端口 5000 是否被占用

2. **資料匯入失敗**
   - 檢查資料庫連接
   - 確認 CSV 檔案格式正確
   - 查看詳細錯誤訊息

3. **路線規劃無結果**
   - 確認 OSRM 服務正在運行
   - 檢查座標是否在台灣範圍內
   - 確認附近有公車站點

### 日誌檢查

```bash
# 檢查應用程式日誌
tail -f logs/app.log

# 檢查 OSRM 服務狀態
python scripts/start_osrm_service.py --check
```

## 📈 未來擴展

### 計劃功能
- [ ] 轉乘路線優化演算法
- [ ] 即時公車位置整合
- [ ] 多種交通方式整合
- [ ] 無障礙路線規劃
- [ ] 路線偏好設定

### 資料更新
- [ ] 自動化資料更新流程
- [ ] 資料版本管理
- [ ] 增量更新支援
- [ ] 資料品質監控

---

如有任何問題，請參考專案文件或聯繫開發團隊。

