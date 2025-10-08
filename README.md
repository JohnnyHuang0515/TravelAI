# 智慧旅遊行程規劃系統

一個基於 AI 的智慧旅遊行程規劃系統，提供個人化行程推薦、景點探索和路線規劃功能。

## 🚀 快速開始

### 推薦啟動順序

1. **啟動基礎服務**（PostgreSQL, Redis）
2. **匯入資料**（首次使用）
3. **啟動 OSRM**（路由服務）
4. **啟動後端 API**
5. **啟動前端**

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
bash scripts/start.sh
```

### 開發環境啟動

```bash
# 啟動開發環境（不使用 Docker）
bash scripts/start_dev.sh

# 或手動啟動
source .venv/bin/activate
source .env
python3 -m uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload
```

### 手動啟動

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
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
| OSRM | 5000 | 路線規劃服務 |

## 📊 資料庫初始化

系統啟動時會自動：

1. **等待資料庫啟動** - 確保 PostgreSQL 服務就緒
2. **啟用 PostGIS 擴展** - 支援地理空間查詢
3. **建立資料表** - 根據 ORM 模型建立所有表
4. **執行遷移** - 執行資料庫結構更新

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
docker-compose up -d osrm-backend
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
docker-compose logs -f

# 特定服務
docker-compose logs -f api
docker-compose logs -f postgres
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

詳細結構請參考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

```
TravelAI/
├── src/                    # 後端源碼
│   └── itinerary_planner/
│       ├── api/           # API 路由
│       ├── application/   # 業務邏輯服務
│       ├── infrastructure/ # 基礎設施層
│       └── interfaces/    # 介面定義
├── frontend/              # 前端應用
├── scripts/               # 工具腳本
│   └── unified_data_importer.py # 統一資料匯入器
├── migrations/            # 資料庫遷移
├── data/                  # 資料檔案
├── docs/                  # 專案文檔
├── tests/                 # 測試代碼
└── 配置檔案...
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

### Q: 資料庫連接失敗
A: 檢查 PostgreSQL 服務是否正常啟動，確認環境變數設定正確。

### Q: OSRM 服務無法啟動
A: 
1. 確認 `data/osrm/` 目錄包含正確的 OSRM 資料檔案
2. 執行 `bash process_osrm.sh` 下載並處理地圖資料
3. 確認 Docker 有足夠的記憶體（建議 8GB+）

### Q: OSRM 路由計算超時 (504)
A:
1. 確認 OSRM 服務正常運行：`curl http://localhost:5000/route/v1/driving/121.5,25.0;121.5,25.0`
2. 檢查環境變數：`OSRM_HOST=http://localhost:5000`
3. 重啟後端服務載入新配置

### Q: 前端無法連接後端
A: 檢查 CORS 設定和 API 服務狀態。

### Q: Google OAuth 登入失敗
A: 確認 Google Cloud Console 設定和重定向 URI 配置。

### Q: 推薦景點沒有顯示
A:
1. 確認資料已匯入：`python3 scripts/unified_data_importer.py`
2. 檢查座標覆蓋率（應 >95%）
3. 驗證 API：`curl "http://localhost:8000/v1/places/nearby?lat=24.7&lon=121.7&radius=50000&limit=5"`

### Q: 地圖上景點無法顯示
A: 
1. 檢查資料是否有座標
2. 確認前端能正確調用 `/v1/places/nearby` API
3. 查看瀏覽器控制台是否有錯誤

## 📞 支援

如有問題，請建立 Issue 或聯繫開發團隊。

---

**智慧旅遊系統** - 讓 AI 為您的旅程增添智慧 ✈️