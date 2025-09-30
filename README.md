# 🗺️ 智慧旅遊行程規劃系統

> AI 驅動的個性化旅遊行程規劃平台

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)](https://www.postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 專案簡介

智慧旅遊行程規劃系統是一個結合 **AI 對話技術**與**地理資訊系統**的旅遊規劃平台，為使用者提供：

- 🤖 **AI 對話式規劃**: 自然語言輸入，智慧生成行程
- 📍 **智慧景點推薦**: 基於位置、興趣的個性化推薦
- 👤 **會員系統**: 行程儲存、分享、個人偏好管理
- 🗺️ **路線優化**: 基於 OSRM 的交通時間計算與路徑優化

---

## ✨ 核心功能

### 1. 對話式行程規劃
- AI 理解自然語言需求
- 多輪對話收集資訊
- 自動生成完整行程
- 即時修改與優化

### 2. 智慧景點推薦
- 基於地理位置的附近景點
- 考慮評分、距離、營業時間
- 支援類別篩選
- 會員個性化推薦

### 3. 會員系統
- Email + OAuth 註冊登入
- 行程儲存與管理
- 行程分享與複製
- 景點收藏功能
- 個人偏好設定

### 4. 路徑優化
- OSRM 精確交通時間
- 貪婪演算法快速規劃
- 2-opt 局部優化
- 考慮營業時間與時間窗

---

## 🏗️ 系統架構

```
前端 (React/Vue)
      ↓
API Gateway (FastAPI)
      ↓
┌─────────────┬─────────────┬─────────────┐
│  認證模組   │  行程管理   │  景點推薦   │
└─────────────┴─────────────┴─────────────┘
      ↓
┌─────────────────────────────────────────┐
│       LangGraph AI 規劃引擎              │
│  (對話管理 + 混合檢索 + 路徑優化)        │
└─────────────────────────────────────────┘
      ↓
┌──────────┬─────────┬─────────┐
│PostgreSQL│  Redis  │  OSRM   │
│ +PostGIS │         │         │
└──────────┴─────────┴─────────┘
```

詳細架構請參考: [系統架構設計文件](docs/系統架構設計文件.md)

---

## 🚀 快速開始

```bash
# 1. Clone 專案
git clone <repo-url>
cd 比賽資料

# 2. 啟動服務
docker-compose up -d

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 執行 Migration
python3 scripts/run_migration.py 001_create_user_system_tables

# 5. 啟動 API
python3 start_server.py

# 6. 測試
python3 scripts/test_complete_flow.py
```

詳細說明: [快速啟動指南](docs/快速啟動指南.md)

---

## 📊 API 端點

### 認證 (9)
```
POST   /v1/auth/register              # 註冊
POST   /v1/auth/login                 # 登入
POST   /v1/auth/refresh               # 刷新 Token
GET    /v1/auth/me                    # 取得使用者資料
PUT    /v1/auth/me/preferences        # 設定偏好
```

### 行程管理 (8)
```
GET    /v1/trips                      # 我的行程列表
POST   /v1/trips                      # 儲存行程
GET    /v1/trips/{id}                 # 行程詳情
PUT    /v1/trips/{id}                 # 更新行程
DELETE /v1/trips/{id}                 # 刪除行程
POST   /v1/trips/{id}/share           # 分享行程
GET    /v1/trips/public/{token}       # 查看公開行程
POST   /v1/trips/{id}/copy            # 複製行程
```

### 景點推薦 (4)
```
GET    /v1/places/nearby              # 附近景點
GET    /v1/places/favorites           # 我的收藏
POST   /v1/places/{id}/favorite       # 收藏景點
DELETE /v1/places/{id}/favorite       # 取消收藏
```

### 行程規劃 (2)
```
POST   /v1/itinerary/propose          # 生成行程
POST   /v1/itinerary/feedback         # 修改行程
```

**完整 API 文件**: http://localhost:8000/docs

---

## 📁 專案結構

```
比賽資料/
├── src/itinerary_planner/          # 原始碼
│   ├── domain/                     # 領域模型
│   ├── application/                # 應用服務
│   │   └── services/               # 業務邏輯
│   ├── infrastructure/             # 基礎設施
│   │   ├── persistence/            # ORM 模型
│   │   ├── repositories/           # 資料存取
│   │   └── clients/                # 外部服務客戶端
│   └── api/                        # API 層
│       └── v1/                     # API v1
│           ├── endpoints/          # 路由端點
│           ├── schemas/            # Pydantic 模型
│           └── dependencies/       # 依賴注入
│
├── scripts/                        # 腳本工具
│   ├── migrations/                 # 資料庫 Migration
│   ├── run_migration.py            # Migration 工具
│   ├── test_auth_api.py            # 認證 API 測試
│   └── test_complete_flow.py       # 完整流程測試
│
├── docs/                           # 文件
│   ├── 系統架構設計文件.md
│   ├── 行程規劃邏輯文件.md
│   ├── 快速啟動指南.md
│   └── 認證API使用指南.md
│
├── data/                           # 資料檔案
│   ├── osrm/                       # OSRM 路網資料
│   └── tdx/                        # TDX 景點資料
│
├── docker-compose.yml              # Docker 編排
├── Dockerfile                      # Docker 映像
├── requirements.txt                # Python 依賴
├── start_server.py                 # 啟動腳本
└── TODO.md                         # 開發待辦清單
```

---

## 🛠️ 技術棧

### 後端
- **框架**: FastAPI 0.104
- **資料庫**: PostgreSQL 14 + PostGIS
- **快取**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **認證**: JWT + bcrypt

### AI & 規劃
- **AI 框架**: LangGraph + LangChain
- **LLM**: Google Gemini / OpenAI
- **檢索**: 混合檢索（結構化 + 語義）
- **演算法**: 貪婪 + 2-opt 優化

### 地理與交通
- **地理查詢**: PostGIS
- **路網計算**: OSRM
- **距離計算**: Haversine 公式

### 前端（規劃中）
- **框架**: React / Vue.js
- **樣式**: Tailwind CSS
- **地圖**: Leaflet / Google Maps

---

## 📈 開發進度

### ✅ Phase 1: 後端系統（已完成 100%）
- ✅ 資料庫設計（8 張會員表）
- ✅ 會員認證模組
- ✅ 行程管理模組
- ✅ 景點推薦模組
- ✅ AI 行程規劃整合

### 📋 Phase 2: 前端開發（待開始）
- [ ] 前端專案設定
- [ ] 註冊/登入頁面
- [ ] 行程規劃頁面
- [ ] 景點推薦頁面
- [ ] 會員中心

### 📋 Phase 3: 測試與優化
- [ ] 單元測試
- [ ] 整合測試
- [ ] 效能優化
- [ ] 安全性加固

### 📋 Phase 4: 部署上線
- [ ] CI/CD 設定
- [ ] 生產環境配置
- [ ] 監控與日誌
- [ ] 文件完善

---

## 🧪 測試

### 執行測試

```bash
# 認證功能測試
python3 scripts/test_auth_api.py

# 完整流程測試（推薦）
python3 scripts/test_complete_flow.py
```

### 測試涵蓋範圍
- ✅ 使用者註冊與登入
- ✅ 偏好設定
- ✅ AI 行程規劃（會員個性化）
- ✅ 行程儲存與管理
- ✅ 行程分享與複製
- ✅ 附近景點推薦
- ✅ 景點收藏

---

## 📚 文件

### 設計文件
- [系統架構設計文件](docs/系統架構設計文件.md) - 完整系統設計
- [行程規劃邏輯文件](docs/行程規劃邏輯文件.md) - AI 規劃邏輯

### 開發文件
- [快速啟動指南](docs/快速啟動指南.md) - 5 分鐘啟動系統
- [快速開始-資料庫設定](docs/快速開始-資料庫設定.md) - 資料庫設定
- [認證 API 使用指南](docs/認證API使用指南.md) - API 使用說明

### 進度文件
- [TODO.md](TODO.md) - 開發待辦清單
- [會員系統整合完成](docs/會員系統整合完成.md) - Phase 1 總結

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 📄 授權

MIT License

---

## 👨‍💻 開發團隊

- **系統設計**: AI Assistant
- **開發**: Johnny
- **AI 技術**: Google Gemini / OpenAI

---

## 🔗 相關連結

- API 文件: http://localhost:8000/docs
- 系統架構: [架構文件](docs/系統架構設計文件.md)
- 開發進度: [TODO](TODO.md)

---

**最後更新**: 2025-09-30  
**版本**: v2.0 - Phase 1 完成
