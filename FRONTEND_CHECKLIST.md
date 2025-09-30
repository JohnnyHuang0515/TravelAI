# 📋 前端開發 Checklist

**快速追蹤版**

---

## 🚀 專案設定

- [ ] 建立 Next.js 14 專案
- [ ] 安裝 Tailwind CSS
- [ ] 安裝 TypeScript
- [ ] 安裝 Axios + Zustand
- [ ] 安裝 React Hook Form + Zod
- [ ] 安裝 Leaflet 地圖
- [ ] 安裝 Lucide Icons
- [ ] 設定 ESLint + Prettier

---

## 🎨 通用組件（10個）

### UI 基礎組件
- [ ] Button.tsx
- [ ] Input.tsx
- [ ] Card.tsx
- [ ] Modal.tsx
- [ ] Loading.tsx
- [ ] Toast.tsx
- [ ] Select.tsx
- [ ] Checkbox.tsx
- [ ] Badge.tsx

### 布局組件
- [ ] Navbar.tsx
- [ ] Footer.tsx

---

## 🔐 認證模組

### 頁面
- [ ] `/login` - 登入頁
- [ ] `/register` - 註冊頁

### 組件
- [ ] LoginForm.tsx
- [ ] RegisterForm.tsx

### 功能
- [ ] authStore（Zustand）
- [ ] API 客戶端（auth.ts）
- [ ] Token 管理
- [ ] 路由守衛

---

## 🗺️ 行程規劃模組

### 頁面
- [ ] `/plan/start` - 基本資料輸入頁
- [ ] `/plan/result` - 行程結果頁

### 核心組件（頁面1）
- [ ] PlanningForm.tsx - 主表單
- [ ] DatePicker.tsx - 日期選擇
- [ ] CategorySelector.tsx - 興趣選擇
- [ ] BudgetSelector.tsx - 預算選擇
- [ ] PaceSelector.tsx - 節奏選擇

### 核心組件（頁面2）
- [ ] TripTimeline.tsx - 時間軸
- [ ] DaySchedule.tsx - 單日行程
- [ ] VisitCard.tsx - 景點卡片
- [ ] PlaceMap.tsx - 地圖
- [ ] ChatBox.tsx - 對話框

### 功能
- [ ] planningStore（Zustand）
- [ ] API 客戶端（planning.ts）
- [ ] 對話邏輯
- [ ] 地圖整合

---

## 📝 會員行程管理

### 頁面
- [ ] `/trips` - 我的行程列表
- [ ] `/trips/[id]` - 行程詳情

### 組件
- [ ] TripCard.tsx - 行程卡片
- [ ] TripList.tsx - 行程列表
- [ ] ShareModal.tsx - 分享彈窗
- [ ] DeleteConfirm.tsx - 刪除確認

### 功能
- [ ] tripStore（Zustand）
- [ ] API 客戶端（trips.ts）
- [ ] 分頁邏輯
- [ ] 分享功能

---

## 📍 景點推薦模組

### 頁面
- [ ] `/places/nearby` - 附近景點
- [ ] `/favorites` - 我的收藏

### 組件
- [ ] PlaceCard.tsx - 景點卡片
- [ ] PlaceList.tsx - 景點列表
- [ ] PlaceFilter.tsx - 篩選器
- [ ] PlaceDetail.tsx - 景點詳情

### 功能
- [ ] 地理定位
- [ ] 地圖視覺化
- [ ] 收藏功能
- [ ] API 客戶端（places.ts）

---

## 👤 個人設定

### 頁面
- [ ] `/profile` - 個人資料
- [ ] `/profile/preferences` - 偏好設定

### 組件
- [ ] ProfileForm.tsx
- [ ] PreferenceForm.tsx
- [ ] PasswordChangeForm.tsx

---

## 🏠 首頁

### 頁面
- [ ] `/` - Landing Page

### 組件
- [ ] HeroSection.tsx
- [ ] FeatureSection.tsx
- [ ] HowItWorks.tsx
- [ ] CTASection.tsx

---

## 🔧 API 整合（4個模組）

- [ ] `lib/api/client.ts` - Axios 實例 + 攔截器
- [ ] `lib/api/auth.ts` - 認證 API（9個函數）
- [ ] `lib/api/trips.ts` - 行程 API（8個函數）
- [ ] `lib/api/places.ts` - 景點 API（5個函數）
- [ ] `lib/api/planning.ts` - 規劃 API（2個函數）

---

## 📦 狀態管理（3個 Store）

- [ ] `store/authStore.ts` - 認證狀態
- [ ] `store/tripStore.ts` - 行程狀態
- [ ] `store/planningStore.ts` - 規劃狀態

---

## 📊 TypeScript 類型（4個檔案）

- [ ] `types/auth.ts` - User, AuthResponse, LoginRequest, RegisterRequest
- [ ] `types/trip.ts` - Trip, TripSummary, SaveTripRequest
- [ ] `types/place.ts` - Place, PlaceDetail
- [ ] `types/itinerary.ts` - Itinerary, Day, Visit

---

## 🎯 開發順序建議

### 第 1 週（基礎）
1. 專案初始化
2. 通用組件（Button, Input, Card, Modal, Loading, Toast）
3. Navbar + Footer
4. API 客戶端設定

### 第 2 週（認證）
5. 登入頁面
6. 註冊頁面
7. authStore
8. 路由守衛

### 第 3 週（規劃）
9. 行程規劃表單頁
10. 行程結果展示頁
11. 對話功能
12. 地圖整合

### 第 4 週（會員）
13. 我的行程頁面
14. 行程詳情
15. 分享功能
16. 個人設定

### 第 5 週（景點）
17. 附近景點頁面
18. 地圖視覺化
19. 收藏功能

### 第 6 週（優化）
20. 首頁
21. 響應式優化
22. 效能優化
23. 測試與修復

---

## 📏 預估工作量

| 類別 | 數量 | 預估時間 |
|------|------|---------|
| 頁面 | 12 個 | 12 天 |
| 組件 | 40+ 個 | 10 天 |
| API 整合 | 4 模組 | 3 天 |
| 狀態管理 | 3 Store | 2 天 |
| 測試優化 | - | 3 天 |

**總計**: 約 30 個工作天（6 週）

---

## ✅ 驗收標準

### 功能驗收
- [ ] 使用者可以註冊帳號
- [ ] 使用者可以登入
- [ ] 使用者可以規劃行程（訪客+會員）
- [ ] 使用者可以透過對話修改行程
- [ ] 會員可以儲存行程
- [ ] 會員可以查看我的行程
- [ ] 會員可以分享行程
- [ ] 使用者可以查看附近景點
- [ ] 會員可以收藏景點
- [ ] 使用者可以在地圖上看到景點

### 品質驗收
- [ ] 手機、平板、桌面響應式設計
- [ ] 所有表單有驗證
- [ ] 所有操作有 Loading 狀態
- [ ] 所有操作有成功/錯誤提示
- [ ] 圖片有載入優化
- [ ] 無障礙設計（ARIA）

---

## 🎓 學習資源

### Next.js
- 官方文件: https://nextjs.org/docs
- 教學: https://nextjs.org/learn

### Tailwind CSS
- 官方文件: https://tailwindcss.com/docs
- UI 範例: https://tailwindui.com

### React Hook Form
- 官方文件: https://react-hook-form.com

### Leaflet
- 官方文件: https://leafletjs.com
- React Leaflet: https://react-leaflet.js.org

---

## 📞 參考後端 API

詳細 API 文件請參考：
- Swagger UI: http://localhost:8000/docs
- [認證 API 使用指南](./認證API使用指南.md)
- [系統架構設計文件](./系統架構設計文件.md)

---

**準備好開始前端開發了嗎？** 🚀
