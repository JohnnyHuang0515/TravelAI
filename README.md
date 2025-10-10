# 智慧旅遊行程規劃系統

一個基於 AI 的智慧旅遊行程規劃系統，提供個人化行程推薦、景點探索和路線規劃功能。

## 🚀 快速開始

### 使用 uv 管理（推薦）

```bash
# 克隆專案
git clone <repository-url>
cd TravelAI

# 使用 uv 同步依賴
uv sync

# 啟動服務
uv run python start_server.py
```

### 一鍵啟動（Docker）

```bash
# 克隆專案
git clone <repository-url>
cd TravelAI

# 一鍵啟動所有服務
./scripts/start.sh
```

### 手動啟動

```bash
# 1. 啟動後端服務（PostgreSQL, Redis, OSRM, API）
docker-compose -p travelai up -d

# 2. 啟動前端服務
cd frontend
npm install  # 首次執行需要安裝依賴
npm run dev

# 查看服務狀態
docker-compose -p travelai ps

# 查看日誌
docker-compose -p travelai logs -f
```

## 📋 系統需求

### 使用 uv 開發
- uv (最新版本)
- Python 3.10+
- 8GB+ RAM（推薦）
- 10GB+ 磁碟空間

### Docker 部署
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM（推薦）
- 10GB+ 磁碟空間

## 🏗️ 系統架構

### 後端服務
- **FastAPI**: Python Web 框架
- **PostgreSQL + PostGIS**: 地理空間資料庫
- **Redis**: 快取和會話存儲
- **OSRM**: 路線規劃引擎

### 前端服務
- **Next.js 14**: React 框架
- **Tailwind CSS**: 樣式框架
- **Zustand**: 狀態管理

### AI 服務
- **Google Gemini**: 行程規劃 AI
- **LangChain**: AI 應用框架
- **LangGraph**: AI 工作流程

## 🔧 服務配置

### 環境變數

建立 `.env` 檔案：

```env
# 資料庫
DATABASE_URL=postgresql://postgres:password@localhost:5432/itinerary_db
REDIS_URL=redis://localhost:6379

# AI 服務
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

### 服務端口

| 服務 | 端口 | 描述 |
|------|------|------|
| API | 8000 | FastAPI 後端服務 |
| 前端 | 3000 | Next.js 前端應用 |
| 資料庫 | 5432 | PostgreSQL 資料庫 |
| Redis | 6379 | Redis 快取 |
| OSRM | 5001 | 路線規劃服務 |

> **注意**: OSRM 使用 5001 端口而非 5000，因為 macOS 的 5000 端口通常被 AirPlay/控制中心佔用。

## 📊 資料庫初始化

系統啟動時會自動：

1. **等待資料庫啟動** - 確保 PostgreSQL 服務就緒
2. **啟用 PostGIS 擴展** - 支援地理空間查詢
3. **建立資料表** - 根據 ORM 模型建立所有表
4. **執行遷移** - 執行資料庫結構更新

### 手動初始化

```bash
# 進入 API 容器
docker-compose exec api bash

# 執行初始化腳本
python3 scripts/init_database.py
```

## 🗺️ OSRM 資料準備

### 下載台灣地圖資料

```bash
# 執行 OSRM 資料處理腳本
./process_osrm.sh
```

### 手動下載

1. 下載台灣 OpenStreetMap 資料
2. 使用 OSRM 工具處理
3. 將處理後的檔案放入 `data/osrm/` 目錄

## 🔐 認證系統

### 支援的認證方式

- **Email 註冊/登入**: 傳統帳號密碼
- **Google OAuth**: Google 帳號登入
- **JWT Token**: API 認證

### 設定 Google OAuth

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立 OAuth 2.0 憑證
3. 設定授權重定向 URI
4. 更新環境變數

## 📱 前端開發

### 啟動前端開發服務

```bash
cd frontend
npm install
npm run dev
```

### 前端技術棧

- **Next.js 14**: App Router, Server Components
- **TypeScript**: 類型安全
- **Tailwind CSS**: 響應式設計
- **React Hook Form**: 表單處理
- **Zustand**: 狀態管理
- **React Hot Toast**: 通知系統

## 🧪 測試

### 後端測試

```bash
# 使用 uv 執行測試
uv run pytest tests/

# 或進入 API 容器執行測試
docker-compose exec api bash
python -m pytest tests/
```

### 前端測試

```bash
cd frontend
npm test
```

## 📈 監控和日誌

### 查看服務日誌

```bash
# 所有服務
docker-compose -p travelai logs -f

# 特定服務
docker-compose -p travelai logs -f api
docker-compose -p travelai logs -f postgres
```

### 健康檢查

```bash
# API 健康檢查
curl http://localhost:8000/health

# 資料庫連接
docker-compose exec postgres pg_isready -U postgres
```

## 🛠️ 開發指南

### uv 專案管理

本專案使用 uv 作為 Python 套件與環境管理工具：

```bash
# 安裝 uv（如果尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依賴
uv sync

# 在虛擬環境中執行指令
uv run python <script.py>
uv run pytest tests/
uv run ruff check src/

# 新增依賴
uv add <package-name>

# 新增開發依賴
uv add --dev <package-name>

# 移除依賴
uv remove <package-name>

# 查看依賴樹
uv tree

# 產生鎖定檔
uv lock
```

### 專案結構

```
TravelAI/
├── src/                    # 後端源碼
│   └── itinerary_planner/
│       ├── api/           # API 路由
│       ├── core/          # 核心邏輯
│       ├── infrastructure/ # 基礎設施
│       └── main.py        # 應用入口
├── frontend/              # 前端應用
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React 組件
│   │   ├── lib/          # 工具函數
│   │   └── stores/       # 狀態管理
├── scripts/               # 工具腳本
├── migrations/            # 資料庫遷移
├── data/                  # 資料檔案
├── pyproject.toml         # Python 專案配置
├── uv.lock               # 依賴鎖定檔
├── .venv/                # 虛擬環境（不提交）
└── docker-compose.yml     # 服務配置
```

### 新增功能

1. **後端 API**: 在 `src/itinerary_planner/api/` 新增路由
2. **資料庫模型**: 在 `src/itinerary_planner/infrastructure/persistence/` 定義模型
3. **前端頁面**: 在 `frontend/src/app/` 新增頁面
4. **組件**: 在 `frontend/src/components/` 新增組件

### 資料庫遷移

```bash
# 建立遷移檔案
touch migrations/007_new_feature.sql

# 執行遷移
python3 scripts/run_migration.py 007_new_feature.sql
```

## 🚀 部署

### 生產環境

```bash
# 使用生產配置
docker-compose -f docker-compose.prod.yml up -d
```

### 環境變數

生產環境需要設定：

- `DATABASE_URL`: 生產資料庫連接
- `REDIS_URL`: 生產 Redis 連接
- `GOOGLE_API_KEY`: AI 服務金鑰
- `JWT_SECRET_KEY`: JWT 簽名密鑰

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 建立 Pull Request

## 📄 授權

MIT License

## 🆘 常見問題

### Q: 資料庫連接失敗
A: 檢查 PostgreSQL 服務是否正常啟動，確認環境變數設定正確。

### Q: OSRM 服務無法啟動
A: 確認 `data/osrm/` 目錄包含正確的 OSRM 資料檔案。

### Q: 5000 端口被佔用
A: macOS 系統的 AirPlay 服務佔用了 5000 端口。本專案已將 OSRM 改用 5001 端口。

### Q: 前端無法連接後端
A: 檢查 CORS 設定和 API 服務狀態。

### Q: Google OAuth 登入失敗
A: 確認 Google Cloud Console 設定和重定向 URI 配置。

## 📞 支援

如有問題，請建立 Issue 或聯繫開發團隊。

---

**智慧旅遊系統** - 讓 AI 為您的旅程增添智慧 ✈️