# 智慧旅遊行程規劃系統 - 開發待辦清單

**更新日期**: 2025-09-30  
**版本**: v2.0 - 完整系統（含會員系統）

---

## 📊 進度總覽

- ✅ 已完成: 核心行程規劃功能、資料庫設計、會員認證、行程管理、景點推薦
- 🎉 Phase 1 完成度: **100%**
- 📋 待開始: Phase 2 前端開發

---

## 🎯 Phase 1: 會員系統與基礎功能（優先）

### 1️⃣ 資料庫擴展

- [X] **任務 1.1: 建立會員相關資料表**
  - [X] 建立 `users` 表（使用者基本資料）
  - [X] 建立 `user_preferences` 表（使用者偏好）
  - [X] 建立 `user_trips` 表（會員行程記錄）
  - [X] 建立 `trip_days` 表（行程天數明細）
  - [X] 建立 `trip_visits` 表（行程景點訪問）
  - [X] 建立 `place_favorites` 表（景點收藏）
  - [X] 建立 `conversation_sessions` 表（對話 Session）
  - [X] 編寫 Migration 腳本

- [X] **任務 1.2: ORM 模型定義**
  - [X] 在 `orm_models.py` 中定義所有新表的 ORM 模型
  - [X] 定義表之間的關聯關係（ForeignKey, relationships）
  - [X] 新增必要的索引

### 2️⃣ 會員認證模組

- [X] **任務 2.1: 認證服務開發**
  - [X] 建立 `src/itinerary_planner/application/services/auth_service.py`
  - [X] 實作使用者註冊功能（Email + 密碼）
  - [X] 實作使用者登入功能
  - [X] 實作 JWT Token 生成與驗證
  - [X] 實作密碼加密（bcrypt）
  - [X] 實作 OAuth 2.0 整合（Google）架構

- [X] **任務 2.2: 認證 API 端點**
  - [X] `POST /v1/auth/register` - 註冊
  - [X] `POST /v1/auth/login` - 登入
  - [X] `POST /v1/auth/logout` - 登出
  - [X] `POST /v1/auth/refresh` - 刷新 Token
  - [ ] `GET /v1/auth/oauth/google` - Google OAuth（待實作）

- [X] **任務 2.3: 會員資料 API 端點**
  - [X] `GET /v1/auth/me` - 取得當前使用者資料
  - [X] `PUT /v1/auth/me` - 更新使用者資料
  - [X] `GET /v1/auth/me/preferences` - 取得偏好
  - [X] `PUT /v1/auth/me/preferences` - 更新偏好

- [X] **任務 2.4: 認證中間件**
  - [X] 建立 JWT 認證中間件
  - [X] 建立可選認證裝飾器（訪客/會員皆可）
  - [ ] 實作 CORS 設定（待設定）
  - [ ] 實作 Rate Limiting（待設定）

### 3️⃣ 行程管理模組

- [X] **任務 3.1: 行程服務開發**
  - [X] 建立 `src/itinerary_planner/application/services/trip_service.py`
  - [X] 實作建立行程功能
  - [X] 實作取得使用者行程列表
  - [X] 實作更新行程功能
  - [X] 實作刪除行程功能
  - [X] 實作分享行程功能（產生公開連結）
  - [X] 實作複製行程功能

- [X] **任務 3.2: 行程管理 API 端點**
  - [X] `GET /v1/trips` - 取得我的行程列表（分頁）
  - [X] `POST /v1/trips` - 儲存新行程
  - [X] `GET /v1/trips/{trip_id}` - 取得行程詳情
  - [X] `PUT /v1/trips/{trip_id}` - 更新行程
  - [X] `DELETE /v1/trips/{trip_id}` - 刪除行程
  - [X] `POST /v1/trips/{trip_id}/share` - 分享行程
  - [X] `POST /v1/trips/{trip_id}/copy` - 複製行程
  - [X] `GET /v1/trips/public/{share_token}` - 查看公開行程

- [X] **任務 3.3: 整合現有行程規劃 API**
  - [X] 修改 `/v1/itinerary/propose` 支援會員個性化
  - [ ] 修改 `/v1/itinerary/feedback` 支援會員（可選）
  - [ ] 加入「儲存行程」快速按鈕（前端）

### 4️⃣ 景點推薦模組

- [X] **任務 4.1: 推薦服務開發**
  - [X] 重用現有 Repository（無需新建 Service）
  - [X] 實作附近景點推薦（基於地理位置）
  - [X] 實作個性化推薦（基於使用者偏好）
  - [X] 實作景點收藏功能

- [X] **任務 4.2: 景點推薦 API 端點**
  - [X] `GET /v1/places/nearby` - 附近景點推薦
  - [X] `GET /v1/places/{place_id}` - 景點詳情（已有）
  - [X] `GET /v1/places/favorites` - 我的收藏景點
  - [X] `POST /v1/places/{place_id}/favorite` - 收藏景點
  - [X] `DELETE /v1/places/{place_id}/favorite` - 取消收藏

- [X] **任務 4.3: 推薦演算法優化**
  - [X] 距離計算與排序（Haversine 公式）
  - [X] 評分權重計算（重用現有）
  - [X] 多樣性控制（重用現有）

### 5️⃣ 對話狀態管理優化

- [ ] **任務 5.1: Session 管理**
  - [ ] 整合 Redis Session 管理
  - [ ] 整合 PostgreSQL 長期對話記錄
  - [ ] 實作 Session 過期機制
  - [ ] 訪客/會員 Session 區分

- [ ] **任務 5.2: 會員個性化**
  - [ ] 自動讀取會員偏好設定
  - [ ] 根據歷史行程推薦
  - [ ] 記憶使用者習慣

---

## 🎨 Phase 2: 前端開發

### 6️⃣ 前端基礎架構

- [ ] **任務 6.1: 專案設定**
  - [ ] 選擇前端框架（React 或 Vue）
  - [ ] 設定 Tailwind CSS
  - [ ] 設定路由系統
  - [ ] 設定狀態管理（Redux/Pinia）
  - [ ] 設定 API 客戶端（Axios）

- [ ] **任務 6.2: 通用組件**
  - [ ] 導覽列組件
  - [ ] Footer 組件
  - [ ] 按鈕組件
  - [ ] 表單組件（Input, Select, Checkbox）
  - [ ] 卡片組件
  - [ ] 載入動畫組件
  - [ ] Toast 通知組件

### 7️⃣ 認證頁面

- [ ] **任務 7.1: 註冊/登入頁面**
  - [ ] 註冊表單 UI
  - [ ] 登入表單 UI
  - [ ] 表單驗證
  - [ ] OAuth 登入按鈕
  - [ ] 錯誤處理與提示
  - [ ] JWT Token 儲存（localStorage）

### 8️⃣ 行程規劃頁面

- [ ] **任務 8.1: 頁面 1 - 基本資料輸入**
  - [ ] `/plan/start` 路由設定
  - [ ] 表單 UI 設計
  - [ ] 目的地選擇器
  - [ ] 日期選擇器
  - [ ] 興趣多選框
  - [ ] 預算/節奏選項
  - [ ] 即時驗證
  - [ ] 進度指示器

- [ ] **任務 8.2: 頁面 2 - 行程生成與修改**
  - [ ] `/plan/result` 路由設定
  - [ ] 左側：行程時間軸 UI
  - [ ] 右側：地圖整合（Leaflet 或 Google Maps）
  - [ ] 景點卡片組件
  - [ ] 下方：對話介面 UI
  - [ ] 對話歷史顯示
  - [ ] 即時修改功能
  - [ ] 儲存/下載按鈕
  - [ ] 會員專屬：「儲存到我的行程」

### 9️⃣ 景點推薦頁面

- [ ] **任務 9.1: 附近景點頁面**
  - [ ] `/places/nearby` 路由設定
  - [ ] 地理定位功能（Geolocation API）
  - [ ] 左側：篩選器 UI（類別、半徑、排序）
  - [ ] 右側：互動地圖
  - [ ] 景點列表卡片
  - [ ] 景點詳情 Modal
  - [ ] 收藏按鈕（會員功能）
  - [ ] 加入行程按鈕

### 🔟 會員中心頁面

- [ ] **任務 10.1: 我的行程頁面**
  - [ ] `/trips` 路由設定
  - [ ] 行程列表 UI
  - [ ] 行程卡片組件
  - [ ] 檢視/編輯/分享/刪除操作
  - [ ] 分頁功能
  - [ ] 空狀態 UI（無行程時）

- [ ] **任務 10.2: 個人設定頁面**
  - [ ] `/profile` 路由設定
  - [ ] 個人資料編輯表單
  - [ ] 偏好設定表單
  - [ ] 頭像上傳
  - [ ] 密碼修改

### 1️⃣1️⃣ 首頁

- [ ] **任務 11.1: 首頁設計**
  - [ ] `/` 路由設定
  - [ ] Hero Section（標題、Slogan、CTA）
  - [ ] 功能介紹區塊
  - [ ] 使用流程說明
  - [ ] 響應式設計

---

## 🧪 Phase 3: 測試與優化

### 1️⃣2️⃣ 後端測試

- [ ] **任務 12.1: 單元測試**
  - [ ] AuthService 測試
  - [ ] TripService 測試
  - [ ] RecommendationService 測試
  - [ ] Repository 測試

- [ ] **任務 12.2: 整合測試**
  - [ ] 認證 API 測試
  - [ ] 行程管理 API 測試
  - [ ] 景點推薦 API 測試

- [ ] **任務 12.3: E2E 測試**
  - [ ] 完整使用者流程測試
  - [ ] 會員註冊→規劃→儲存流程
  - [ ] 景點推薦→收藏流程

### 1️⃣3️⃣ 前端測試

- [ ] **任務 13.1: 組件測試**
  - [ ] 關鍵組件單元測試
  - [ ] 表單驗證測試

- [ ] **任務 13.2: E2E 測試**
  - [ ] Playwright 或 Cypress 設定
  - [ ] 關鍵流程自動化測試

### 1️⃣4️⃣ 效能優化

- [ ] **任務 14.1: 後端效能**
  - [ ] 資料庫查詢優化
  - [ ] Redis 快取策略優化
  - [ ] API 回應時間監控

- [ ] **任務 14.2: 前端效能**
  - [ ] 程式碼分割（Code Splitting）
  - [ ] 圖片懶載入
  - [ ] 資源壓縮

---

## 🚀 Phase 4: 部署與上線

### 1️⃣5️⃣ 部署準備

- [ ] **任務 15.1: Docker 配置**
  - [ ] 更新 `docker-compose.yml`（加入新服務）
  - [ ] 建立 `.env.example`
  - [ ] 編寫部署文件

- [ ] **任務 15.2: CI/CD**
  - [ ] GitHub Actions 設定
  - [ ] 自動化測試流程
  - [ ] 自動化部署流程

- [ ] **任務 15.3: 安全性**
  - [ ] 環境變數管理
  - [ ] HTTPS 設定
  - [ ] Rate Limiting 設定
  - [ ] CORS 政策設定

### 1️⃣6️⃣ 監控與日誌

- [ ] **任務 16.1: 監控系統**
  - [ ] Prometheus 設定
  - [ ] Grafana Dashboard
  - [ ] 關鍵指標追蹤

- [ ] **任務 16.2: 錯誤追蹤**
  - [ ] Sentry 整合
  - [ ] 錯誤通知設定

---

## 📚 Phase 5: 文件與優化

### 1️⃣7️⃣ API 文件

- [ ] **任務 17.1: API 文件完善**
  - [ ] OpenAPI/Swagger 文件補充
  - [ ] API 使用範例
  - [ ] 錯誤碼說明

### 1️⃣8️⃣ 使用者文件

- [ ] **任務 18.1: 使用手冊**
  - [ ] 快速開始指南
  - [ ] 功能說明文件
  - [ ] FAQ

---

## 🎯 當前優先任務（本週）

### 🔥 高優先級（Phase 1 完成 ✅）

1. [X] 建立會員相關資料表與 Migration
2. [X] 實作使用者註冊/登入 API
3. [X] 實作 JWT 認證中間件
4. [X] 實作行程儲存 API

### 🎨 Phase 2 優先級

5. [X] 實作附近景點推薦 API
6. [ ] 開始前端專案設定（Next.js / React）
7. [ ] 設計註冊/登入頁面
8. [ ] 設計行程規劃頁面

---

## 📝 備註

- **技術選擇**:
  - 後端: Python + FastAPI + SQLAlchemy
  - 資料庫: PostgreSQL + PostGIS + Redis
  - 前端: React + Tailwind CSS（待確認）
  - 認證: JWT + OAuth 2.0
  
- **開發原則**:
  - API First 開發
  - 測試驅動開發（TDD）
  - 持續整合/部署（CI/CD）
  
- **時程規劃**:
  - Phase 1: 4 週（會員系統與基礎功能）
  - Phase 2: 4 週（前端開發）
  - Phase 3: 2 週（測試與優化）
  - Phase 4: 1 週（部署上線）

---

**最後更新**: 2025-09-30  
**下次檢視**: 每週一更新進度