# TravelAI 專案結構

## 📁 核心目錄

```
TravelAI/
├── 📂 src/                          # 後端核心代碼
│   └── itinerary_planner/
│       ├── api/                     # API 端點
│       ├── application/             # 業務邏輯服務
│       ├── infrastructure/          # 基礎設施層
│       └── interfaces/              # 介面定義
├── 📂 frontend/                     # 前端 Next.js 應用
├── 📂 scripts/                      # 工具腳本
│   ├── unified_data_importer.py     # 統一資料匯入器（含去重）
│   ├── deduplication_manager.py    # 資料去重管理器
│   ├── start.sh                    # 一鍵啟動（Docker）
│   ├── start_dev.sh                # 開發環境啟動
│   ├── stop.sh                     # 停止所有服務
│   ├── mock_osrm_server.py         # OSRM 模擬伺服器
│   ├── start_osrm.sh               # OSRM 啟動腳本
│   └── start_real_osrm.sh          # 真實 OSRM 啟動（已更新）
├── 📂 tests/                        # 測試代碼
├── 📂 migrations/                   # 資料庫遷移
├── 📂 docs/                         # 專案文檔
├── 📂 data/                         # 資料檔案
└── 📄 配置檔案
    ├── docker-compose.yml          # Docker 編排
    ├── Dockerfile                  # Docker 映像
    ├── pyproject.toml              # Python 專案配置
    ├── requirements.txt            # Python 依賴
    ├── process_osrm.sh             # OSRM 處理腳本
    └── start_server.py             # 伺服器啟動腳本
```

## 🚀 核心功能

### 後端 (src/itinerary_planner/)
- **API 層**: RESTful API 端點
- **應用層**: 業務邏輯服務 (規劃、推薦、搜尋)
- **基礎設施層**: 資料庫、外部服務客戶端
- **介面層**: API 架構定義

### 前端 (frontend/)
- Next.js 14 應用
- React 元件
- API 客戶端

### 資料處理 (scripts/)
- **unified_data_importer.py**: 統一資料匯入管道（含智能去重）
- **deduplication_manager.py**: 智能去重系統
- **OSRM 相關**: 路由服務腳本
- **啟動腳本**: start.sh (Docker), start_dev.sh (開發), stop.sh (停止)

## 🔧 開發工具

- **測試**: pytest 框架
- **資料庫**: PostgreSQL + pgvector
- **快取**: Redis
- **容器化**: Docker
- **依賴管理**: uv (Python), npm (Node.js)

## 📊 資料流程

1. **資料匯入**: `scripts/unified_data_importer.py`
2. **資料處理**: 地址解析、語境增強、嵌入生成
3. **API 服務**: 搜尋、推薦、規劃
4. **前端展示**: 使用者介面

