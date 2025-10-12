# TravelAI 一鍵啟動指南

## 📖 概述

`quick-start.sh` 是一個智能啟動腳本，可以自動檢測環境、配置系統並啟動 TravelAI 的所有服務。

## 🚀 基本使用

### 1. 快速啟動

```bash
cd TravelAI
bash quick-start.sh
```

腳本會：
1. 檢查系統環境（Docker, Node.js, Python 等）
2. 提示選擇啟動模式
3. 自動創建 `.env` 檔案（如果不存在）
4. 啟動所有必要的服務
5. 顯示服務狀態和訪問 URL

### 2. 停止服務

```bash
bash scripts/stop.sh
```

## 🎯 啟動模式詳解

### 模式 1: 完整 Docker 模式（推薦新手）

**適用場景**：
- 第一次使用系統
- 不想安裝本地開發環境
- 需要完整的服務隔離

**啟動內容**：
- PostgreSQL + PostGIS（資料庫）
- Redis（快取）
- OSRM（路由服務）
- FastAPI（後端 API）
- 可選：Next.js 前端（後台運行）

**優點**：
- ✅ 環境隔離，不污染本機
- ✅ 配置簡單，無需安裝 Python/Node.js
- ✅ 與生產環境一致

**缺點**：
- ❌ 熱重載可能較慢
- ❌ 調試相對複雜

**操作示例**：
```bash
bash quick-start.sh
# 選擇: 1

# 服務啟動後
# 後端: http://localhost:8000
# 前端: http://localhost:3000 (如果啟動)
# API 文檔: http://localhost:8000/docs

# 停止服務
docker-compose down
```

---

### 模式 2: 混合模式（推薦開發者）

**適用場景**：
- 本地開發和調試
- 需要快速熱重載
- 頻繁修改代碼

**啟動內容**：
- **Docker**：PostgreSQL, Redis, OSRM
- **本地**：FastAPI 後端, Next.js 前端

**優點**：
- ✅ 快速熱重載
- ✅ 易於調試
- ✅ 資源佔用較小

**缺點**：
- ❌ 需要安裝本地開發環境
- ❌ 需要管理環境變數

**操作示例**：
```bash
bash quick-start.sh
# 選擇: 2

# 服務啟動後（後台運行）
# 後端: http://localhost:8000
# 前端: http://localhost:3000

# 查看日誌
tail -f logs/backend.log
tail -f logs/frontend.log

# 停止服務
bash scripts/stop.sh
```

---

### 模式 3: 僅後端服務

**適用場景**：
- 後端開發
- API 測試
- 不需要前端界面

**啟動內容**：
- Docker: PostgreSQL, Redis, OSRM
- 本地: FastAPI 後端（前台運行）

**操作示例**：
```bash
bash quick-start.sh
# 選擇: 3

# 服務啟動後（前台運行，可直接看到日誌）
# 後端: http://localhost:8000
# API 文檔: http://localhost:8000/docs

# 停止服務: Ctrl+C
```

---

### 模式 4: 僅前端服務

**適用場景**：
- 前端開發
- UI/UX 調整
- 使用遠端後端 API

**啟動內容**：
- 本地: Next.js 前端（前台運行）

**注意**：需要確保後端 API 可訪問（本地或遠端）

**操作示例**：
```bash
bash quick-start.sh
# 選擇: 4

# 服務啟動後
# 前端: http://localhost:3000

# 停止服務: Ctrl+C
```

## 🔧 環境配置

### 必要的環境變數

腳本會自動從 `env.example` 創建 `.env`，但你需要編輯以下關鍵變數：

```env
# 必須設定（AI 功能需要）
GEMINI_API_KEY=your_actual_google_gemini_api_key

# 可選設定（OAuth 登入需要）
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 取得 API Key

1. **Google Gemini API Key**
   - 訪問：https://makersuite.google.com/app/apikey
   - 登入 Google 帳號
   - 點擊「Create API Key」
   - 複製並貼到 `.env` 的 `GEMINI_API_KEY`

2. **Google OAuth 憑證**（可選）
   - 訪問：https://console.cloud.google.com/
   - 創建專案 → 啟用 OAuth 2.0
   - 設定授權重定向 URI: `http://localhost:3000/auth/google/callback`
   - 複製 Client ID 和 Secret 到 `.env`

## 📊 資料匯入

### 首次使用

如果是第一次啟動，腳本會檢測資料庫為空並提示是否匯入資料：

```
⚠️  資料庫為空，建議執行資料匯入
是否現在匯入資料？ (y/N): y
```

輸入 `y` 後會自動執行資料匯入，包含：
- 🗺️ 全台灣 16,584 筆旅遊資料
- 📍 4,594 筆地點（95% 有座標）
- 🏨 2,523 筆住宿（100% 有座標）
- 🌱 4,327 筆環保認證資料

### 手動匯入

```bash
# 使用 Docker（模式 1）
docker-compose exec api python3 scripts/unified_data_importer.py

# 使用本地環境（模式 2/3）
uv run python scripts/unified_data_importer.py
# 或
source .venv/bin/activate
python3 scripts/unified_data_importer.py
```

## 🔍 常見問題

### Q1: 腳本執行失敗，顯示「permission denied」

**解決方案**：
```bash
chmod +x quick-start.sh
bash quick-start.sh
```

### Q2: Docker 服務無法啟動

**檢查項目**：
1. Docker Desktop 是否正在運行？
2. Docker 是否有足夠的記憶體（建議 8GB+）？
3. 端口是否被佔用（5432, 6379, 5000, 8000, 3000）？

**解決方案**：
```bash
# 檢查端口佔用
lsof -i :8000
lsof -i :3000
lsof -i :5432

# 停止佔用端口的服務
kill <PID>
```

### Q3: GEMINI_API_KEY 未設定警告

**原因**：`.env` 中的 API Key 是預設值或未設定

**解決方案**：
1. 編輯 `.env` 檔案
2. 將 `GEMINI_API_KEY` 設定為真實的 API Key
3. 重新啟動服務

### Q4: 後端啟動但無法訪問

**檢查項目**：
```bash
# 檢查後端是否真的在運行
curl http://localhost:8000/health

# 查看後端日誌
# Docker 模式
docker-compose logs -f api

# 本地模式
tail -f logs/backend.log
```

### Q5: 資料匯入失敗

**可能原因**：
- 資料庫連接失敗
- 網路問題（無法下載資料）
- 磁碟空間不足

**解決方案**：
```bash
# 檢查資料庫連接
docker-compose exec postgres pg_isready -U postgres

# 手動重試匯入
uv run python scripts/unified_data_importer.py
```

## 🎓 進階使用

### 自訂環境變數

除了在 `.env` 設定，也可以在啟動時覆寫：

```bash
# 使用不同的資料庫
DATABASE_URL="postgresql://user:pass@remote:5432/db" bash quick-start.sh

# 使用遠端 OSRM 服務
OSRM_HOST="http://remote-osrm:5000" bash quick-start.sh
```

### 僅啟動特定 Docker 服務

```bash
# 僅啟動資料庫
docker-compose up -d postgres

# 僅啟動 OSRM
docker-compose up -d osrm-backend

# 啟動多個服務
docker-compose up -d postgres redis osrm-backend
```

### 查看服務狀態

```bash
# Docker 服務
docker-compose ps

# 本地服務
ps aux | grep uvicorn
ps aux | grep "next dev"

# 檢查端口
netstat -an | grep LISTEN | grep -E "8000|3000|5432|6379|5000"
```

## 📝 開發工作流程建議

### 後端開發流程

```bash
# 1. 啟動混合模式
bash quick-start.sh
# 選擇: 2

# 2. 修改代碼（自動熱重載）
# 編輯 src/itinerary_planner/...

# 3. 查看日誌
tail -f logs/backend.log

# 4. 測試 API
curl http://localhost:8000/v1/places/nearby?lat=24.7&lon=121.7&limit=5

# 5. 查看 API 文檔
open http://localhost:8000/docs

# 6. 停止服務
bash scripts/stop.sh
```

### 前端開發流程

```bash
# 1. 確保後端運行
bash quick-start.sh
# 選擇: 3 (僅後端)

# 2. 在另一個終端啟動前端
cd frontend
npm run dev

# 3. 修改代碼（自動熱重載）
# 編輯 frontend/src/...

# 4. 查看瀏覽器
open http://localhost:3000

# 5. 停止前端: Ctrl+C
```

### 全棧開發流程

```bash
# 使用混合模式（推薦）
bash quick-start.sh
# 選擇: 2

# 後端和前端都在後台運行
# 可以同時修改前後端代碼

# 查看後端日誌
tail -f logs/backend.log

# 查看前端日誌
tail -f logs/frontend.log

# 完成後停止所有服務
bash scripts/stop.sh
```

## 🔗 相關文檔

- [專案結構說明](../PROJECT_STRUCTURE.md)
- [API 設計規範](../specs/04_api_design_specification.md)
- [架構設計文檔](../design/03_architecture_and_design_document.md)
- [資料匯入指南](../../README.md#資料庫初始化)

## 💡 提示

1. **第一次使用**：建議使用「模式 1: 完整 Docker 模式」
2. **日常開發**：建議使用「模式 2: 混合模式」
3. **記得設定 API Key**：否則 AI 功能無法運作
4. **定期更新依賴**：`uv sync` 或 `docker-compose pull`
5. **查看日誌**：遇到問題先查看日誌檔案

---

**需要幫助？**
- 查看 [README.md](../../README.md)
- 建立 [GitHub Issue](https://github.com/your-org/travelai/issues)

