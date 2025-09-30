# Google OAuth 設定指南

本文件說明如何設定 Google OAuth 2.0 登入功能。

## 前置需求

1. Google Cloud Platform 帳號
2. 專案已啟用 Google+ API

## 步驟 1: 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 專案名稱：`TravelAI` (或自訂)

## 步驟 2: 啟用 Google+ API

1. 在左側選單中，選擇「API 和服務」→「程式庫」
2. 搜尋「Google+ API」
3. 點擊「啟用」

## 步驟 3: 建立 OAuth 2.0 用戶端 ID

1. 在左側選單中，選擇「API 和服務」→「憑證」
2. 點擊「建立憑證」→「OAuth 用戶端 ID」
3. 應用程式類型：選擇「網頁應用程式」
4. 名稱：`TravelAI Web Client`
5. 已授權的 JavaScript 來源：
   - `http://localhost:3000` (開發環境)
   - `https://your-production-domain.com` (生產環境)
6. 已授權的重新導向 URI：
   - `http://localhost:8001/v1/auth/oauth/google/callback` (開發環境)
   - `https://api.your-production-domain.com/v1/auth/oauth/google/callback` (生產環境)
7. 點擊「建立」

## 步驟 4: 取得憑證

建立後，會顯示「用戶端 ID」和「用戶端密鑰」，請妥善保存：

- **用戶端 ID**: `1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com`
- **用戶端密鑰**: `GOCSPX-xxxxxxxxxxxxxxxxxxxxxx`

## 步驟 5: 設定環境變數

### 後端 (.env 或環境變數)

```bash
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8001/v1/auth/oauth/google/callback
FRONTEND_URL=http://localhost:3000
```

### 前端 (frontend/.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here
```

## 步驟 6: 執行資料庫 Migration

```bash
# 新增 Google OAuth 欄位
psql -U your_user -d travel_ai -f migrations/006_add_google_oauth_fields.sql
```

## 步驟 7: 測試 OAuth 登入

1. 啟動後端：
```bash
python start_server.py
```

2. 啟動前端：
```bash
cd frontend
npm run dev
```

3. 訪問 http://localhost:3000/login
4. 點擊「使用 Google 登入」按鈕
5. 使用 Google 帳號登入
6. 登入成功後會重定向回應用程式

## 除錯

### 常見問題

**Q: "Error 400: redirect_uri_mismatch"**

A: 確認 Google Cloud Console 中的重新導向 URI 與 `.env` 中的 `GOOGLE_REDIRECT_URI` 完全一致。

**Q: "Invalid state parameter"**

A: State 參數可能已過期（10分鐘），請重新點擊登入按鈕。

**Q: "OAuth callback failed"**

A: 檢查後端日誌，確認：
- Google Client ID 和 Secret 正確
- 資料庫連線正常
- Migration 已執行

### 檢查設定

```bash
# 檢查環境變數
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET

# 測試 OAuth 端點
curl http://localhost:8001/v1/auth/oauth/google
```

## 生產環境注意事項

1. **HTTPS 必要性**：生產環境必須使用 HTTPS
2. **域名配置**：更新 Google Cloud Console 中的授權域名
3. **密鑰管理**：使用密鑰管理服務（如 AWS Secrets Manager）
4. **狀態管理**：建議使用 Redis 儲存 OAuth state，而非記憶體

## 參考資源

- [Google OAuth 2.0 文件](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 最佳實踐](https://oauth.net/2/best-practices/)
