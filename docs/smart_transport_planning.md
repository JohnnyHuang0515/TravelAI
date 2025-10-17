# 智能交通規劃系統

本文件說明 TravelAI 專案中新增的智能交通規劃系統，該系統根據使用者的交通工具偏好來智能規劃行程中的交通方式。

## 🚗 系統概述

智能交通規劃系統能夠：
- 根據使用者偏好選擇最佳交通方式
- 整合開車、大眾運輸、步行等多種交通模式
- 計算精確的交通時間和費用
- 提供環保和無障礙交通選項
- 與對話系統整合，智能收集交通偏好

## 📊 交通工具模式

### 1. 開車模式 (Driving)
- **適用場景**: 山區景點、遠距離景點、需要彈性安排
- **特點**: 
  - 最大步行距離: 200m
  - 最大步行時間: 5分鐘
  - 考慮交通狀況和停車需求
  - 計算油錢和過路費

### 2. 大眾運輸模式 (Public Transport)
- **適用場景**: 市區景點、文化景點、環保出行
- **特點**:
  - 最大步行距離: 800m
  - 最大步行時間: 15分鐘
  - 整合宜蘭公車系統
  - 考慮班次時間和轉乘

### 3. 混合模式 (Mixed)
- **適用場景**: 多樣化景點、智能選擇
- **特點**:
  - 根據距離智能選擇交通方式
  - 平衡時間、費用和便利性
  - 動態調整交通策略

### 4. 環保模式 (Eco-friendly)
- **適用場景**: 環保意識、生態旅遊
- **特點**:
  - 優先使用大眾運輸和步行
  - 最大步行距離: 1000m
  - 減少碳排放
  - 考慮無障礙設施

## 🏗️ 系統架構

### 核心組件

#### 1. TransportPreference (交通工具偏好)
```python
@dataclass
class TransportPreference:
    primary_mode: TransportMode              # 主要交通模式
    primary_type: TransportType              # 主要交通工具類型
    secondary_modes: List[TransportMode]     # 次要交通模式
    optimization: RouteOptimization          # 路線優化策略
    constraints: TransportConstraints        # 約束條件
    accessibility_needs: List[str]           # 無障礙需求
    budget_preference: str                   # 預算偏好
    eco_friendly: bool                       # 環保偏好
```

#### 2. SmartTransportPlanner (智能交通規劃器)
- 規劃兩個景點間的交通
- 整合 OSRM 和公車路線規劃
- 計算時間、距離、費用和碳排放

#### 3. EnhancedPlanningService (增強版行程規劃服務)
- 整合交通工具偏好的行程規劃
- 為每個行程天數規劃詳細交通
- 估算交通對行程的影響

### 資料流程

```
用戶輸入 → 對話系統 → 交通工具偏好 → 智能規劃器 → 行程規劃 → 交通整合 → 最終行程
```

## 🔧 使用方式

### 1. 基本使用

```python
from src.itinerary_planner.application.services.enhanced_planning_service import EnhancedPlanningService

# 建立增強版規劃服務
planner = EnhancedPlanningService()

# 規劃行程（包含交通）
itinerary = planner.plan_itinerary_with_transport(
    story=story,
    candidates=candidates,
    user_transport_choice="mixed"  # 開車、大眾運輸、混合、環保
)
```

### 2. 自訂偏好設定

```python
from src.itinerary_planner.domain.models.transport_preference import create_custom_preference

# 建立自訂偏好
preference = create_custom_preference(
    primary_mode=TransportMode.DRIVING,
    primary_type=TransportType.CAR,
    constraints=TransportConstraints(
        max_walking_distance=300.0,
        max_walking_time=5,
        max_daily_driving_time=600
    )
)
```

### 3. 對話整合

系統會自動在對話中收集交通工具偏好：

```
AI: 您希望使用什麼樣的交通工具呢？
選項：
🚗 開車 - 彈性高，適合遠距離景點
🚌 大眾運輸 - 經濟環保，體驗當地交通
🔄 混合模式 - 智能選擇最佳交通方式
🌱 環保出行 - 優先使用大眾運輸和步行
```

## 📈 功能特色

### 1. 智能交通選擇
- 根據景點距離自動選擇最佳交通方式
- 考慮時間、費用、便利性等因素
- 動態調整交通策略

### 2. 精確時間計算
- 整合 OSRM 路由引擎計算開車時間
- 使用公車時刻表計算大眾運輸時間
- 考慮步行時間和等待時間

### 3. 費用估算
- 開車：油錢 + 過路費
- 大眾運輸：公車票價
- 混合模式：綜合費用計算

### 4. 環保考量
- 計算碳排放量
- 提供環保交通選項
- 無障礙交通支援

### 5. 對話整合
- 智能收集交通偏好
- 根據目的地推薦交通方式
- 自然語言理解交通需求

## 🧪 測試範例

執行測試腳本：

```bash
python scripts/test_smart_transport_planning.py
```

測試內容包括：
- 交通工具偏好設定
- 增強版行程規劃
- 交通工具選項推薦
- 對話整合功能

## 🔄 與現有系統整合

### 1. 對話系統整合
- 在 `GraphNodes` 中新增交通工具偏好收集
- 更新問題生成邏輯
- 整合關鍵字分析

### 2. 行程規劃整合
- 更新 `plan_itinerary` 節點
- 整合增強版規劃服務
- 添加交通摘要到行程

### 3. 公車系統整合
- 使用已整合的宜蘭公車資料
- 整合 OSRM 路由引擎
- 提供完整的交通規劃

## 📊 效能優化

### 1. 快取策略
- 快取交通時間矩陣
- 快取路線規劃結果
- 快取偏好設定

### 2. 並行處理
- 並行計算多個交通選項
- 非同步調用 OSRM 服務
- 並行處理多天行程

### 3. 回退機制
- OSRM 服務不可用時使用估算
- 公車資料不可用時回退到步行
- 增強版規劃失敗時使用基礎規劃

## 🚀 未來擴展

### 1. 即時交通資訊
- 整合即時路況資訊
- 動態調整交通時間
- 提供替代路線建議

### 2. 多種交通方式
- 計程車/叫車服務
- 自行車租借
- 共享機車

### 3. 個人化偏好
- 學習使用者交通習慣
- 個人化交通推薦
- 歷史偏好記憶

### 4. 進階功能
- 交通費用優化
- 多目的地路線優化
- 團體交通規劃

## 📝 注意事項

### 1. 依賴服務
- 需要 OSRM 服務運行
- 需要公車資料庫
- 需要 PostGIS 支援

### 2. 效能考量
- 大量景點時規劃時間較長
- 建議限制每日景點數量
- 使用快取提升效能

### 3. 資料品質
- 依賴公車時刻表準確性
- 路況變化影響時間估算
- 建議定期更新交通資料

---

智能交通規劃系統大幅提升了 TravelAI 的實用性，為使用者提供了更精確、更貼心的行程規劃體驗。系統的模組化設計也為未來的功能擴展奠定了良好的基礎。
