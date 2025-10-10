# 🔐 認證 API 使用指南

## 📋 概述

本文件說明如何使用智慧旅遊行程規劃系統的認證 API。

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 安裝新增的認證相關套件
pip install bcrypt==4.1.1 pyjwt==2.8.0 python-jose[cryptography]==3.3.0
```

### 2. 執行 Migration

```bash
# 建立會員系統資料表
python3 scripts/run_migration.py 001_create_user_system_tables
```

### 3. 啟動服務

```bash
# 確保資料庫已啟動
docker compose up -d db redis

# 啟動 API 服務
python3 start_server.py
```

### 4. 測試 API

```bash
# 執行測試腳本
python3 scripts/test_auth_api.py
```

## 📡 API 端點

### 基本資訊

- **Base URL**: `http://localhost:8000/v1`
- **認證方式**: Bearer Token (JWT)
- **Content-Type**: `application/json`

### 端點列表

| 端點 | 方法 | 功能 | 認證 |
|------|------|------|------|
| `/auth/register` | POST | 註冊新使用者 | ❌ |
| `/auth/login` | POST | 使用者登入 | ❌ |
| `/auth/refresh` | POST | 刷新 Access Token | ❌ |
| `/auth/logout` | POST | 登出 | ✅ |
| `/auth/me` | GET | 取得當前使用者資料 | ✅ |
| `/auth/me` | PUT | 更新使用者資料 | ✅ |
| `/auth/me/change-password` | POST | 修改密碼 | ✅ |
| `/auth/me/preferences` | GET | 取得偏好設定 | ✅ |
| `/auth/me/preferences` | PUT | 更新偏好設定 | ✅ |

## 🔧 使用範例

### 1. 註冊新使用者

```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123",
    "username": "traveler_john"
  }'
```

**回應**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "traveler_john",
    "provider": "email",
    "is_verified": false,
    "created_at": "2025-09-30T10:00:00Z",
    "last_login": null
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. 使用者登入

```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securePassword123"
  }'
```

### 3. 取得當前使用者資料

```bash
curl -X GET "http://localhost:8000/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 更新偏好設定

```bash
curl -X PUT "http://localhost:8000/v1/auth/me/preferences" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "favorite_themes": ["美食", "自然", "文化"],
    "travel_pace": "relaxed",
    "budget_level": "moderate"
  }'
```

### 5. 刷新 Access Token

```bash
curl -X POST "http://localhost:8000/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## 🔑 Token 管理

### Access Token
- **有效期**: 1 小時
- **用途**: 訪問受保護的 API
- **儲存**: 前端 localStorage 或 sessionStorage

### Refresh Token
- **有效期**: 7 天
- **用途**: 更新 Access Token
- **儲存**: HttpOnly Cookie（建議）

### Token 格式

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🛡️ 安全性

### 密碼要求
- 最小長度: 8 個字元
- 建議包含: 大小寫字母、數字、特殊字元

### JWT 設定
- 算法: HS256
- Secret: 設定於環境變數 `JWT_SECRET`

### 最佳實踐
1. **HTTPS**: 生產環境必須使用 HTTPS
2. **Token 儲存**: 避免在 localStorage 儲存敏感資料
3. **Token 刷新**: Access Token 過期前自動刷新
4. **登出**: 前端刪除儲存的 Token

## 📊 錯誤處理

### 常見錯誤碼

| 狀態碼 | 說明 | 原因 |
|--------|------|------|
| 400 | Bad Request | 請求格式錯誤 |
| 401 | Unauthorized | Token 無效或過期 |
| 403 | Forbidden | 帳號被停用 |
| 404 | Not Found | 資源不存在 |
| 409 | Conflict | Email 已被註冊 |

### 錯誤回應格式

```json
{
  "detail": "錯誤訊息"
}
```

## 💡 整合範例（JavaScript）

### 註冊與登入

```javascript
// 註冊
async function register(email, password, username) {
  const response = await fetch('http://localhost:8000/v1/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, username }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  
  // 儲存 Token
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data.user;
}

// 登入
async function login(email, password) {
  const response = await fetch('http://localhost:8000/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  const data = await response.json();
  
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  
  return data.user;
}
```

### API 請求攔截器

```javascript
// 自動添加 Token
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  // Token 過期，嘗試刷新
  if (response.status === 401) {
    const newToken = await refreshToken();
    if (newToken) {
      headers['Authorization'] = `Bearer ${newToken}`;
      return fetch(url, { ...options, headers });
    }
  }
  
  return response;
}

// 刷新 Token
async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  
  if (!response.ok) {
    // Refresh Token 也過期，需要重新登入
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return null;
  }
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  
  return data.access_token;
}
```

## 🧪 測試

### 使用 Swagger UI

訪問 `http://localhost:8000/docs` 查看互動式 API 文件。

### 使用 Postman

1. 匯入 API Collection
2. 設定環境變數 `BASE_URL`
3. 執行測試流程

## 📚 相關文件

- [系統架構設計文件](./系統架構設計文件.md)
- [快速開始-資料庫設定](./快速開始-資料庫設定.md)
- [TODO 清單](../TODO.md)
