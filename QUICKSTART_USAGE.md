# Quick Start 使用範例

## 🎯 場景 1：第一次使用系統

```bash
# 1. 克隆專案
git clone <repository-url>
cd TravelAI

# 2. 執行一鍵啟動
bash quick-start.sh

# 3. 選擇模式 1（完整 Docker 模式）
請選擇啟動模式：
  1) 完整 Docker 模式（推薦，包含所有服務）
  2) 混合模式（Docker 基礎服務 + 本地開發）
  3) 僅後端服務
  4) 僅前端服務

請輸入選項 [1-4] (預設: 1): 1

# 4. 系統會自動：
#    - 檢查環境
#    - 建立 .env
#    - 啟動所有服務
#    - 提示匯入資料

# 5. 當提示資料匯入時，輸入 y
是否現在匯入資料？ (y/N): y

# 6. 等待匯入完成（約 3-5 分鐘）

# 7. 啟動前端
是否啟動前端開發服務器？ (Y/n): Y

# 8. 完成！訪問應用
open http://localhost:3000
```

**預期結果**：
- ✅ 後端 API: http://localhost:8000
- ✅ 前端應用: http://localhost:3000
- ✅ API 文檔: http://localhost:8000/docs
- ✅ 資料庫有 16,584 筆旅遊資料

---

## 🎯 場景 2：日常開發（推薦）

```bash
cd TravelAI

# 啟動混合模式（最適合開發）
bash quick-start.sh

# 選擇模式 2
請選擇啟動模式：
  1) 完整 Docker 模式（推薦，包含所有服務）
  2) 混合模式（Docker 基礎服務 + 本地開發）
  3) 僅後端服務
  4) 僅前端服務

請輸入選項 [1-4] (預設: 1): 2

# 系統會自動啟動（後台運行）：
# - Docker: PostgreSQL, Redis, OSRM
# - 本地: 後端 API, 前端應用

# 在另一個終端查看後端日誌
tail -f logs/backend.log

# 在另一個終端查看前端日誌
tail -f logs/frontend.log

# 開始開發...
# 修改 src/itinerary_planner/... (自動熱重載)
# 修改 frontend/src/... (自動熱重載)

# 完成後停止服務
bash scripts/stop.sh
```

**優點**：
- ⚡ 熱重載快速
- 🔍 易於調試
- 📊 日誌清晰

---

## 🎯 場景 3：後端 API 開發

```bash
cd TravelAI

# 啟動僅後端模式
bash quick-start.sh

# 選擇模式 3
請輸入選項 [1-4] (預設: 1): 3

# 後端在前台運行，可直接看到日誌
# 可以立即看到 API 請求和錯誤

# 測試 API
curl http://localhost:8000/v1/places/nearby?lat=24.7&lon=121.7&limit=5

# 查看 API 文檔
open http://localhost:8000/docs

# 修改代碼會自動重載
# src/itinerary_planner/api/v1/places.py

# 停止: Ctrl+C
```

**適用場景**：
- API 端點開發
- 後端邏輯調試
- API 性能測試

---

## 🎯 場景 4：前端 UI 開發

```bash
# 假設後端已經在運行（本地或遠端）

cd TravelAI

# 啟動僅前端模式
bash quick-start.sh

# 選擇模式 4
請輸入選項 [1-4] (預設: 1): 4

# 前端在前台運行
# 訪問 http://localhost:3000

# 修改 UI 組件
# frontend/src/components/...

# 實時查看變更
# 瀏覽器自動刷新

# 停止: Ctrl+C
```

**適用場景**：
- UI/UX 調整
- 組件開發
- 樣式調整

---

## 🎯 場景 5：測試環境設置

```bash
# 模擬生產環境進行測試

cd TravelAI

# 1. 清除現有服務
bash scripts/stop.sh
docker-compose down -v  # 清除 volume

# 2. 啟動完整 Docker 模式
bash quick-start.sh
# 選擇: 1

# 3. 匯入測試資料
# 選擇: y (匯入資料)

# 4. 執行測試
docker-compose exec api pytest tests/

# 5. 查看日誌
docker-compose logs -f api

# 6. 完成後清理
docker-compose down -v
```

---

## 🎯 場景 6：多人協作開發

### 開發者 A（後端）

```bash
# 終端 1
cd TravelAI
bash quick-start.sh
# 選擇: 3 (僅後端)

# 開發後端 API
# 修改 src/itinerary_planner/...
```

### 開發者 B（前端）

```bash
# 終端 1
cd TravelAI

# 設定後端 API 地址（指向開發者 A 的機器）
# 編輯 frontend/.env.local
echo "NEXT_PUBLIC_API_URL=http://192.168.1.100:8000" > frontend/.env.local

bash quick-start.sh
# 選擇: 4 (僅前端)

# 開發前端
# 修改 frontend/src/...
```

---

## 🛠️ 常用操作

### 查看服務狀態

```bash
# Docker 服務
docker-compose ps

# 本地服務
ps aux | grep uvicorn
ps aux | grep "next dev"

# 檢查端口
lsof -i :8000  # 後端
lsof -i :3000  # 前端
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :5000  # OSRM
```

### 查看日誌

```bash
# Docker 服務
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f osrm-backend

# 本地服務
tail -f logs/backend.log
tail -f logs/frontend.log

# 查看最後 100 行
tail -n 100 logs/backend.log
```

### 重啟服務

```bash
# Docker 服務
docker-compose restart api
docker-compose restart postgres

# 本地服務
# 後端
kill $(cat logs/backend.pid)
uv run uvicorn src.itinerary_planner.main:app --host 0.0.0.0 --port 8000 --reload

# 前端
kill $(cat logs/frontend.pid)
cd frontend && npm run dev
```

### 清理和重置

```bash
# 停止所有服務
bash scripts/stop.sh

# 清除 Docker volumes（會刪除資料庫）
docker-compose down -v

# 清除日誌
rm -rf logs/*.log

# 重新開始
bash quick-start.sh
```

---

## 📊 效能對比

| 操作 | 完整 Docker | 混合模式 | 僅後端 | 僅前端 |
|------|------------|---------|--------|--------|
| 啟動時間 | ~30秒 | ~15秒 | ~10秒 | ~5秒 |
| 熱重載速度 | 較慢（~3秒） | 快（~1秒） | 快（~1秒） | 快（<1秒） |
| 記憶體使用 | 高（~4GB） | 中（~2GB） | 低（~1.5GB） | 極低（~500MB） |
| CPU 使用 | 中 | 低 | 低 | 極低 |
| 適合場景 | 測試/演示 | 開發 | 後端開發 | 前端開發 |

---

## 💡 最佳實踐

### 1. 開發工作流程

```bash
# 早上開始工作
bash quick-start.sh  # 選擇模式 2

# 開發一整天...
# 自動熱重載，無需重啟

# 下班前停止
bash scripts/stop.sh
```

### 2. 功能開發

```bash
# 1. 創建功能分支
git checkout -b feature/new-api

# 2. 啟動開發環境
bash quick-start.sh  # 模式 2 或 3

# 3. 開發和測試
# 修改代碼 → 自動重載 → 測試

# 4. 提交變更
git add .
git commit -m "feat: add new API endpoint"
git push

# 5. 停止服務
bash scripts/stop.sh
```

### 3. Bug 修復

```bash
# 1. 重現問題
bash quick-start.sh  # 模式 1（完整環境）

# 2. 查看日誌找問題
docker-compose logs -f api

# 3. 切換到開發模式修復
bash scripts/stop.sh
bash quick-start.sh  # 模式 2

# 4. 修復代碼並測試
# 5. 確認修復
# 6. 提交
```

---

## 🚨 故障排除

### 問題 1：端口被佔用

```bash
# 檢查哪個進程佔用端口
lsof -i :8000

# 停止該進程
kill <PID>

# 或強制停止
kill -9 <PID>

# 重新啟動
bash quick-start.sh
```

### 問題 2：Docker 記憶體不足

```bash
# 增加 Docker 記憶體限制
# Docker Desktop → Settings → Resources → Memory → 8GB+

# 或清理 Docker 資源
docker system prune -a
docker volume prune
```

### 問題 3：資料庫連接失敗

```bash
# 檢查 PostgreSQL 是否運行
docker-compose ps postgres

# 檢查連接
docker-compose exec postgres pg_isready -U postgres

# 重啟資料庫
docker-compose restart postgres

# 如果還是失敗，重建
docker-compose down -v
docker-compose up -d postgres
```

---

**需要更多幫助？**
- 📖 查看 [詳細指南](docs/guides/quick_start_guide.md)
- 📖 查看 [README.md](README.md)
- 🐛 報告問題 [GitHub Issues](https://github.com/your-org/travelai/issues)

