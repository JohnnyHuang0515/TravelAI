# 智慧旅遊行程規劃系統

一個基於 AI 的智慧旅遊行程規劃系統，提供個人化行程推薦、景點探索和路線規劃功能。

## ✨ 特色功能

- 🤖 **AI 智能規劃**：使用簡單關鍵字匹配提供基本行程建議（簡化版本）
- 🗺️ **地理空間搜尋**：基於 PostGIS 的精準地點推薦（功能完善）
- 🚗 **路線優化**：整合 OSRM 提供最佳路線規劃（功能完善）
- 🌱 **環保認證**：收錄超過 4,300 筆環保標章景點和住宿（功能完善）
- 📊 **資料豐富**：涵蓋全台灣 16,584 筆旅遊資料（功能完善）
- 🔐 **安全認證**：支援 Email 和 Google OAuth 登入（功能完善）
- ⚡ **快速部署**：一鍵啟動腳本，5 分鐘內完成部署（功能完善）

## ⚠️ 當前狀態（v1.0.2）

**開發中功能**：
- 🤖 **AI 對話引擎**：已簡化為基於關鍵字的行程規劃，不依賴複雜的 LLM 或 RAG 搜尋
- 💬 **統一對話**：基本的意圖檢測和實體提取功能正常運作

**已完成功能**：
- ✅ 資料庫系統和匯入
- ✅ 地理空間搜尋
- ✅ 路線規劃（OSRM）
- ✅ 基礎認證系統
- ✅ 前端介面

**下一步計劃**：
- 🔄 逐步整合真實的 LLM 生成
- 🔄 添加資料庫景點和住宿查詢
- 🔄 優化使用者體驗

## 🚀 快速開始

### ⚡ 一鍵啟動（推薦）

```bash
# 克隆專案
git clone <repository-url>
cd TravelAI

# 賦予執行權限
chmod +x quick-start.sh

# 互動模式啟動（會提示選擇模式）
bash quick-start.sh

# 或使用非互動模式直接啟動
bash quick-start.sh 1  # 完整 Docker 模式
bash quick-start.sh 2  # 混合模式（推薦開發）
bash quick-start.sh 3  # 僅後端服務
bash quick-start.sh 4  # 僅前端服務
```

**腳本自動完成**：
- ✅ 環境依賴檢查（Docker, Node.js, Python, uv）
- ✅ 環境變數配置（自動從 env.example 創建 .env）
- ✅ 啟動資料庫服務（PostgreSQL, Redis, OSRM）
- ✅ 建立資料表結構（自動執行 schema 初始化）
- ✅ 啟動應用服務（後端 API 和前端應用）
- ✅ 資料匯入提示（首次使用引導匯入 16,584 筆資料）
- ✅ 服務狀態監控（實時顯示服務健康狀態）

**啟動模式說明：**
1. **完整 Docker 模式**：所有服務運行在 Docker（推薦新手）
2. **混合模式**：Docker 基礎服務 + 本地開發（推薦開發）
3. **僅後端服務**：用於後端開發
4. **僅前端服務**：用於前端開發

**非互動模式特點：**
- ✅ 支援自動化腳本和 CI/CD
- ✅ 跳過所有使用者輸入提示
- ✅ 自動啟動前端服務（模式 1, 2）
- ✅ 快速啟動，無需等待輸入

> 📖 **詳細文檔**：
> - [一鍵啟動指南](docs/guides/quick_start_guide.md) - 完整功能說明和故障排除
> - [使用範例](QUICKSTART_USAGE.md) - 6 種常見場景的操作示範

### 停止服務

```bash
# 停止所有服務（Docker + 本地）
bash scripts/stop.sh

# 或使用 Docker Compose（僅 Docker 服務）
docker compose down
```

### 啟動模式對照表

| 模式 | 啟動內容 | 適用場景 | 優點 | 缺點 |
|------|---------|---------|------|------|
| **模式 1**<br/>完整 Docker | 所有服務在 Docker | 新手使用<br/>生產環境測試 | 環境隔離<br/>配置簡單 | 熱重載較慢<br/>調試複雜 |
| **模式 2**<br/>混合模式 | Docker: DB, Redis, OSRM<br/>本地: 後端 + 前端 | 日常開發<br/>快速迭代 | 快速熱重載<br/>易於調試 | 需要本地環境 |
| **模式 3**<br/>僅後端 | Docker: DB, Redis, OSRM<br/>本地: 後端 | 後端開發<br/>API 測試 | 專注後端<br/>資源節省 | 需要另外啟動前端 |
| **模式 4**<br/>僅前端 | 本地: 前端 | 前端開發<br/>UI 調整 | 專注前端<br/>獨立開發 | 需要後端已運行 |

---

## 📚 其他啟動方式

### 方式 A：使用 uv 開發（推薦開發者）

```bash
# 克隆專案
git clone <repository-url>
cd TravelAI

# 建立環境變數檔案
cp env.example .env
# 編輯 .env 設定必要的 API Key

# 使用 uv 同步依賴
uv sync

# 啟動基礎服務（PostgreSQL, Redis, OSRM）
docker compose up -d postgres redis osrm-backend

# 初始化資料庫（建立表格）
uv run python scripts/init_database.py

# 匯入資料（首次使用，約 3-5 分鐘）
uv run python scripts/unified_data_importer.py

# 啟動後端服務
source .env
uv run uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload

# 在另一個終端啟動前端
cd frontend
npm install
npm run dev
```

**服務訪問**：
- 後端 API: http://localhost:8000
- API 文檔: http://localhost:8000/docs
- 前端應用: http://localhost:3000

---

### 方式 B：完整 Docker 部署

```bash
# 使用 Docker Compose 啟動所有服務
docker compose up -d

# 等待服務啟動後，初始化資料庫
docker compose exec api python3 scripts/init_database.py

# 匯入資料（首次使用）
docker compose exec api python3 scripts/unified_data_importer.py

# 查看服務狀態
docker compose ps

# 查看日誌
docker compose logs -f api
```

---

### 方式 C：傳統腳本啟動

```bash
# 啟動所有 Docker 服務（包含後端 API）
bash scripts/start.sh

# 啟動本地開發環境（不使用 Docker 運行後端）
bash scripts/start_dev.sh
```

---

## 🔄 完整啟動流程圖

```
┌─────────────────────────────────────────────────────┐
│ 1️⃣ 執行 quick-start.sh                              │
│    └─ 選擇啟動模式 (1-4)                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2️⃣ 環境檢查                                         │
│    ├─ Docker & Docker Compose                       │
│    ├─ Python / uv / Node.js                         │
│    └─ .env 環境變數檔案                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3️⃣ 啟動基礎服務                                     │
│    ├─ PostgreSQL (5432) - 資料庫                    │
│    ├─ Redis (6379) - 快取                           │
│    └─ OSRM (5000) - 路由引擎                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4️⃣ 初始化資料庫                                     │
│    ├─ 等待資料庫就緒 (自動重試 30 次)               │
│    ├─ 啟用 PostGIS 擴展                             │
│    └─ 建立資料表 (13 個表)                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5️⃣ 檢查資料狀態                                     │
│    ├─ 如果資料為空 → 提示匯入資料                   │
│    └─ 如果已有資料 → 顯示記錄數量                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 6️⃣ 啟動應用服務                                     │
│    ├─ 後端 API (8000) - FastAPI                     │
│    └─ 前端應用 (3000) - Next.js                     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 7️⃣ 系統就緒 ✅                                       │
│    ├─ 顯示服務地址和狀態                            │
│    ├─ 顯示日誌位置                                  │
│    └─ 顯示停止命令                                  │
└─────────────────────────────────────────────────────┘
```

## 📋 系統需求

### 必要軟體

| 軟體 | 版本 | 用途 | 安裝方式 |
|------|------|------|---------|
| **Docker** | 20.10+ | 容器化部署 | [安裝指南](https://docs.docker.com/get-docker/) |
| **Docker Compose** | 2.0+ | 多容器管理 | [安裝指南](https://docs.docker.com/compose/install/) |

### 開發環境（可選）

| 軟體 | 版本 | 用途 | 安裝方式 |
|------|------|------|---------|
| **Python** | 3.10+ | 後端開發 | [python.org](https://www.python.org/) |
| **uv** | 最新版 | Python 套件管理 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node.js** | 18+ | 前端開發 | [nodejs.org](https://nodejs.org/) |
| **npm** | 9+ | 前端套件管理 | 隨 Node.js 安裝 |

### 硬體需求

| 配置 | 最低 | 推薦 |
|------|------|------|
| **RAM** | 4GB | 8GB+ |
| **磁碟空間** | 5GB | 10GB+ |
| **CPU** | 雙核 | 四核+ |

## 🏗️ 系統架構

### 後端服務
- **FastAPI**: Python Web 框架
- **PostgreSQL + PostGIS + pgvector**: 地理空間與向量資料庫
- **Redis**: 快取和會話存儲
- **OSRM**: 路線規劃引擎

### 前端服務
- **Next.js 14**: React 框架（App Router）
- **Tailwind CSS**: 樣式框架
- **Zustand**: 狀態管理
- **Leaflet**: 地圖顯示

### AI 服務
- **Google Gemini**: 行程規劃 AI
- **Sentence Transformers**: 多語言語義嵌入
- **LangChain**: AI 應用框架
- **LangGraph**: AI 工作流程

### 資料處理管道
- **統一匯入系統**: 一次完成所有資料處理
- **地址解析**: 結構化地址與座標獲取
- **語境增強**: 自動生成活動類型、價格等級等元資料
- **智能去重**: 自動檢測並處理重複資料
- **向量嵌入**: 支援語義搜尋

## 🔧 服務配置

### 環境變數

啟動腳本會自動從 `env.example` 建立 `.env` 檔案。手動建立：

```bash
cp env.example .env
# 編輯 .env 設定必要的 API Key
nano .env
```

`.env` 檔案內容：

```env
# 資料庫
DATABASE_URL=postgresql://postgres:password@localhost:5432/itinerary_db
REDIS_URL=redis://localhost:6379

# AI 服務（必填）
GEMINI_API_KEY=your_google_gemini_api_key

# OAuth（可選）
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# 路由服務
OSRM_HOST=http://localhost:5000

# JWT 安全
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 服務端口

| 服務 | 端口 | 描述 |
|------|------|------|
| API | 8000 | FastAPI 後端服務 |
| 前端 | 3000 | Next.js 前端應用 |
| 資料庫 | 5432 | PostgreSQL 資料庫 |
| Redis | 6379 | Redis 快取 |
| OSRM | 5000 | 路線規劃服務 |

## 📊 資料庫初始化

### 自動初始化（推薦）

使用 `quick-start.sh` 會自動執行：
1. **等待資料庫啟動** - 確保 PostgreSQL 服務就緒
2. **啟用 PostGIS 擴展** - 支援地理空間查詢
3. **建立資料表** - 根據 ORM 模型建立所有表

### 手動初始化

```bash
# 使用初始化腳本
python3 scripts/init_database.py

# 或使用 uv
uv run python scripts/init_database.py

# 使用 Docker
docker compose exec api python3 scripts/init_database.py
```

**初始化腳本功能** (`scripts/init_database.py`)：
- ✅ 等待資料庫就緒（自動重試 30 次，每次間隔 2 秒）
- ✅ 啟用 PostGIS 擴展（地理空間功能）
- ✅ 建立所有資料表（13 個表，基於 ORM 模型）
- ✅ 顯示已建立的表清單（確認初始化成功）

**建立的資料表**：
```
places              - 地點資料（景點、餐廳等）
accommodations      - 住宿資料
hours              - 營業時間
users              - 使用者帳號
user_preferences   - 使用者偏好
user_trips         - 使用者行程
trip_days          - 行程天數
trip_day_items     - 行程項目
place_favorites    - 收藏的地點
place_visits       - 地點訪問記錄
conversation_sessions - 對話會話
messages           - 訊息記錄
feedback_events    - 使用者回饋
```

### 資料匯入

#### **統一資料匯入系統**

本專案使用智能資料處理管道，在匯入時自動完成：
- ✅ 地址解析與座標獲取
- ✅ 語境增強（活動類型、價格等級等）
- ✅ Embedding 生成（支援語義搜尋）
- ✅ 智能去重（避免重複資料）
- ✅ 環保認證標記

```bash
# 完整匯入（會清除舊資料）
python3 scripts/unified_data_importer.py

# 或使用 uv
uv run python scripts/unified_data_importer.py

# 查看資料統計
python3 -c "
import sys
sys.path.append('src')
from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Place, Accommodation

db = SessionLocal()
print(f'地點: {db.query(Place).count()} 筆')
print(f'住宿: {db.query(Accommodation).count()} 筆')
db.close()
"

# 或使用 uv
uv run python -c "
from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Place, Accommodation

db = SessionLocal()
print(f'地點: {db.query(Place).count()} 筆')
print(f'住宿: {db.query(Accommodation).count()} 筆')
db.close()
"
```

#### **資料覆蓋範圍**

- 🗺️ **全台灣** 16,584 筆旅遊資料
- 📍 **地點**: 4,594 筆（95% 有座標）
  - 環保餐廳 4,380 筆
  - 環境教育設施 267 筆
  - 宜蘭縣景點 96 筆
- 🏨 **住宿**: 2,523 筆（100% 有座標）
  - 環保標章旅館 174 筆
  - 宜蘭縣住宿 2,350 筆
- 🌱 **環保認證**: 4,327 筆高品質資料

## 🗺️ OSRM 路由服務

### 啟動 OSRM 服務

```bash
# 使用腳本啟動
bash scripts/start_real_osrm.sh

# 或使用 Docker Compose（會自動處理）
docker compose up -d osrm-backend
```

### 準備台灣地圖資料

```bash
# 執行 OSRM 資料處理腳本
bash process_osrm.sh
```

此腳本會：
1. 下載台灣 OpenStreetMap 資料
2. 使用 OSRM 工具處理（extract → partition → customize）
3. 生成可用的路由資料檔案

### 手動處理

1. 下載台灣 OSM 資料：`taiwan-latest.osm.pbf`
2. 執行 OSRM 處理流程：
   ```bash
   docker run -t -v "${PWD}/data/osrm:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/taiwan.osm.pbf
   docker run -t -v "${PWD}/data/osrm:/data" osrm/osrm-backend osrm-partition /data/taiwan.osrm
   docker run -t -v "${PWD}/data/osrm:/data" osrm/osrm-backend osrm-customize /data/taiwan.osrm
   ```
3. 啟動服務：`bash scripts/start_real_osrm.sh`

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
docker compose exec api bash
python -m pytest tests/
```

### 前端測試

```bash
cd frontend
npm run lint  # 執行 ESLint 檢查
```

## 📈 監控和日誌

### 查看服務日誌

```bash
# 所有服務
docker compose logs -f

# 特定服務
docker compose logs -f api
docker compose logs -f postgres
```

### 健康檢查

```bash
# API 健康檢查
curl http://localhost:8000/health

# 資料庫連接
docker compose exec postgres pg_isready -U postgres
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

詳細結構請參考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

```
TravelAI/
├── quick-start.sh         ⭐ 一鍵啟動腳本
├── scripts/
│   ├── init_database.py   ⭐ 資料庫初始化
│   ├── unified_data_importer.py  # 統一資料匯入器
│   ├── start.sh           # Docker 啟動腳本
│   ├── start_dev.sh       # 開發環境啟動
│   └── stop.sh            ⭐ 停止所有服務
├── src/
│   └── itinerary_planner/
│       ├── api/           # API 路由 (FastAPI)
│       ├── application/   # 業務邏輯服務
│       ├── domain/        # 領域模型
│       ├── infrastructure/ # 基礎設施層
│       │   ├── persistence/    # 資料庫（ORM 模型）
│       │   ├── clients/        # 外部服務客戶端
│       │   └── repositories/   # 資料存取層
│       └── interfaces/    # 介面定義
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js 14 App Router
│   │   ├── components/   # React 組件
│   │   ├── lib/          # 工具函數
│   │   └── stores/       # Zustand 狀態管理
│   └── package.json
├── docs/
│   ├── guides/
│   │   └── quick_start_guide.md  ⭐ 詳細啟動指南
│   ├── design/           # 設計文檔
│   └── specs/            # API 規範
├── migrations/           # SQL 遷移腳本
├── data/
│   └── osrm/            # OSRM 路由資料
├── tests/               # 測試代碼
├── docker-compose.yml   # Docker 編排配置
├── Dockerfile           # API 容器映像
├── pyproject.toml       # Python 專案配置 (uv)
├── requirements.txt     # Python 依賴
└── README.md            # 本文件
```

### 新增功能

1. **後端 API**: 在 `src/itinerary_planner/api/` 新增路由
2. **資料庫模型**: 在 `src/itinerary_planner/infrastructure/persistence/` 定義模型
3. **前端頁面**: 在 `frontend/src/app/` 新增頁面
4. **組件**: 在 `frontend/src/components/` 新增組件

### 資料庫遷移

```bash
# 建立遷移檔案
touch migrations/008_new_feature.sql

# 使用 psql 執行遷移（本地）
psql -h localhost -U postgres -d itinerary_db -f migrations/008_new_feature.sql

# 或使用 Docker Compose 執行
docker compose exec postgres psql -U postgres -d itinerary_db -f /migrations/008_new_feature.sql

# 或進入容器內執行
docker compose exec postgres bash
psql -U postgres -d itinerary_db < /migrations/008_new_feature.sql
```

## 🚀 部署

### 生產環境

```bash
# 使用生產配置
docker compose -f docker-compose.prod.yml up -d
```

### 環境變數

生產環境需要設定：

- `DATABASE_URL`: 生產資料庫連接
- `REDIS_URL`: 生產 Redis 連接
- `GEMINI_API_KEY`: Google Gemini AI 服務金鑰
- `JWT_SECRET_KEY`: JWT 簽名密鑰
- `OSRM_HOST`: OSRM 路由服務地址

## 🧹 專案清理

本專案已進行大規模整理，移除了：
- ❌ 重複的資料處理腳本
- ❌ 舊的對話模式 API
- ❌ 未使用的測試檔案
- ❌ 臨時檔案

現在採用：
- ✅ 統一資料匯入系統
- ✅ 單一對話引擎（`/v1/conversation`）
- ✅ 清晰的專案結構

## 🤝 貢獻指南

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 建立 Pull Request

## 📄 授權

MIT License

## 🆘 常見問題

### Q1: 資料庫連接失敗

**症狀**：啟動時顯示無法連接到資料庫

**解決方案**：
```bash
# 1. 檢查 PostgreSQL 是否運行
docker compose ps postgres

# 2. 重啟資料庫
docker compose restart postgres

# 3. 檢查連接
docker compose exec postgres pg_isready -U postgres

# 4. 查看日誌
docker compose logs postgres
```

### Q2: 一鍵啟動腳本權限錯誤

**症狀**：`Permission denied: quick-start.sh`

**解決方案**：
```bash
chmod +x quick-start.sh
bash quick-start.sh

# 或使用非互動模式
bash quick-start.sh 2  # 直接啟動混合模式
```

### Q3: OSRM 服務無法啟動

**症狀**：路由計算失敗或 OSRM 容器啟動失敗

**解決方案**：
```bash
# 1. 確認 OSRM 資料檔案存在
ls -lh data/osrm/taiwan-250923.osrm

# 2. 如果檔案不存在，執行處理腳本
bash process_osrm.sh

# 3. 手動啟動 OSRM
bash scripts/start_real_osrm.sh

# 4. 測試 OSRM 服務
curl "http://localhost:5000/route/v1/driving/121.5,25.0;121.5,25.1"

# 5. 增加 Docker 記憶體（Settings → Resources → Memory → 8GB+）
```

### Q4: 資料匯入失敗

**症狀**：`unified_data_importer.py` 執行報錯

**解決方案**：
```bash
# 1. 確認資料庫已初始化
python3 scripts/init_database.py

# 2. 檢查資料檔案是否存在
ls -lh docs/*.json

# 3. 查看詳細錯誤訊息重新執行
python3 scripts/unified_data_importer.py 2>&1 | tee import.log

# 4. 如果是網路問題，重試即可
```

### Q5: 前端無法連接後端

**症狀**：前端顯示 `ERR_CONNECTION_REFUSED` 或 `Network Error`

**解決方案**：
```bash
# 1. 確認後端正在運行
curl http://localhost:8000/health
ps aux | grep uvicorn

# 2. 啟動後端服務
bash quick-start.sh 3  # 僅後端模式

# 3. 檢查 API 路徑配置
# 前端應使用: /v1/auth/register （非 /v1/auth/auth/register）

# 4. 檢查 CORS 設定（main.py）
# 應包含: allow_origins=["http://localhost:3000"]

# 5. 重啟後端服務
docker compose restart api
# 或
pkill -f uvicorn && bash quick-start.sh 3
```

### Q6: API Key 未設定警告

**症狀**：`GEMINI_API_KEY 未設定`

**解決方案**：
```bash
# 1. 編輯 .env 檔案
nano .env

# 2. 設定 GEMINI_API_KEY
GEMINI_API_KEY=your_actual_api_key_here

# 3. 取得 API Key
# 訪問: https://makersuite.google.com/app/apikey

# 4. 重啟服務載入新配置
bash scripts/stop.sh
bash quick-start.sh
```

### Q7: 端口被佔用

**症狀**：啟動失敗，顯示端口已被使用

**解決方案**：
```bash
# 檢查端口佔用
lsof -i :8000  # 後端
lsof -i :3000  # 前端
lsof -i :5432  # PostgreSQL
lsof -i :5000  # OSRM

# 停止佔用端口的進程
kill <PID>

# 或使用一鍵停止腳本
bash scripts/stop.sh
```

## 📞 取得協助

### 📖 文檔資源

- [一鍵啟動指南](docs/guides/quick_start_guide.md) - 完整功能說明和故障排除
- [使用範例](QUICKSTART_USAGE.md) - 6 種常見場景的操作示範
- [專案結構](PROJECT_STRUCTURE.md) - 完整的專案架構說明
- [API 規範](docs/specs/04_api_design_specification.md) - RESTful API 文檔
- [架構設計](docs/design/03_architecture_and_design_document.md) - 系統架構文檔

### 🐛 問題回報

如果遇到問題，請提供以下資訊：
1. 作業系統版本
2. Docker 版本
3. 錯誤訊息和日誌
4. 執行的命令

建立 Issue: [GitHub Issues](https://github.com/your-org/travelai/issues)

### 💬 社群支援

- 📧 Email: support@travelai.example.com
- 💬 Discord: [加入討論](https://discord.gg/travelai)

---

## 📝 更新日誌

### v1.0.1 (2025-10-13)

**新增功能**：
- ✨ 一鍵啟動腳本支援非互動模式（命令行參數）
- ✨ 支援自動化部署和 CI/CD 整合

**修正問題**：
- 🐛 修正後端 API 路徑重複 `/auth/auth` 問題
- 🐛 修正啟動腳本在後台模式無法執行的問題

**改進**：
- ⚡ 優化啟動腳本，支援參數化啟動
- 📝 更新所有 Docker 指令為新版格式 (`docker compose`)
- 📝 更新 README 文檔說明和環境變數配置範例

### v1.0.0 (2025-10-12)

**新增功能**：
- ✨ 一鍵啟動腳本 (`quick-start.sh`)
- ✨ 資料庫初始化腳本 (`init_database.py`)
- ✨ 4 種啟動模式選擇
- ✨ 自動環境檢測和配置
- ✨ 完整的文檔體系

**修正問題**：
- 🐛 修正 OSRM 端口配置不一致
- 🐛 修正環境變數名稱（GEMINI_API_KEY）
- 🐛 移除不存在的初始化服務

**改進**：
- 📝 重構 README 結構
- 📝 補充詳細的故障排除指南
- ⚡ 優化啟動流程和體驗

查看完整更新: [CHANGELOG_QUICKSTART.md](CHANGELOG_QUICKSTART.md)

---

<div align="center">

**🎉 智慧旅遊行程規劃系統**

讓 AI 為您的旅程增添智慧 ✈️

Made with ❤️ by TravelAI Team

[開始使用](#-快速開始) • [查看文檔](docs/) • [報告問題](https://github.com/your-org/travelai/issues)

</div>