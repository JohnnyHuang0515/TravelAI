# API 設計規範 - 智慧旅遊行程規劃器

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-09-24`
**主要作者/設計師:** `Gemini`
**狀態:** `草稿 (Draft)`
**相關 SD 文檔:** `../design/03_architecture_and_design_document.md`

---

## 1. 設計原則與約定

- **API 風格:** RESTful
- **基本 URL:** `/v1`
- **請求與回應格式:** `application/json`
- **命名約定:**
    - 資源路徑: `kebab-case` (e.g., `/travel-time`)
    - JSON 欄位: `snake_case`
- **日期與時間格式:** ISO 8601 (e.g., `2025-09-24T10:00:00Z`)

## 2. 認證與授權

- **機制:** 初期為匿名訪問，可通過 Header 傳遞 `X-Session-ID` 來維持會話。未來可擴展為 OAuth 2.0。

## 3. 錯誤處理

- **標準錯誤回應格式:**
  ```json
  {
    "error": {
      "type": "invalid_request_error",
      "code": "parameter_missing",
      "message": "A required parameter was missing."
    }
  }
  ```
- **通用 HTTP 狀態碼:** `400` (客戶端錯誤), `404` (未找到), `500` (伺服器錯誤)。

## 4. API 端點詳述

### 會話管理

#### `POST /v1/session`
- **描述:** 創建一個新的對話會話。
- **請求體:** (空)
- **成功回應 (200 OK):**
  ```json
  {
    "session_id": "unique_session_string"
  }
  ```

### 核心規劃流程

#### `POST /v1/itinerary/propose` (取代 `/story:parse` 和 `/itinerary:propose`)
- **描述:** 根據使用者的自然語言輸入，一步到位生成一份行程草案。此端點內部會觸發完整的 LangGraph 流程（解析 -> 檢索 -> 規劃）。
- **請求體:**
  ```json
  {
    "session_id": "string",
    "text": "我想去宜蘭玩三天，喜歡大自然和美食。"
  }
  ```
- **成功回應 (200 OK):** 返回 `Itinerary` 物件。
  ```json
  {
    "itinerary": {
      "days": [
        {
          "date": "2025-10-01",
          "visits": [
            {"place_id": "uuid-1", "name": "景點A", "eta": "10:00", "etd": "11:30", "travel_min": 20},
            ...
          ]
        }
      ]
    }
  }
  ```

#### `POST /v1/itinerary/feedback`
- **狀態:** `已實現 (Implemented)`
- **描述:** 接收使用者對行程的修改指令，並返回一個更新後的行程。
- **請求體:**
  ```json
  {
    "session_id": "string",
    "itinerary": {
      "days": [
        {
          "date": "2025-10-01",
          "visits": [
            {"place_id": "uuid-1", "name": "景點A", "eta": "10:00", "etd": "11:30", "travel_minutes": 0},
            {"place_id": "uuid-2", "name": "景點B", "eta": "12:00", "etd": "13:30", "travel_minutes": 30}
          ]
        }
      ]
    },
    "feedback_text": "不要去景點A了"
  }
  ```
- **成功回應 (200 OK):** 返回一個新的、經過修改的 `itinerary` 物件。

### 工具性端點

#### `GET /v1/places/search`
- **描述:** 結構化與語義混合查詢地點。
- **查詢參數:** `q` (語義查詢), `lat`, `lon`, `radius`, `categories` (逗號分隔), `min_rating`。
- **成功回應 (200 OK):**
  ```json
  {
    "places": [
      {"place_id": "uuid-1", "name": "景點A", ...}
    ]
  }
  ```

#### `GET /v1/travel-time/table`
- **描述:** 批次查詢多點之間的交通時間矩陣。
- **查詢參數:** `locations` (分號分隔的 `lat,lon` 對), `mode` (`driving`, `walking`)。
- **成功回應 (200 OK):**
  ```json
  {
    "durations": [
      [0, 1200, 1800],
      [1180, 0, 950],
      [1750, 980, 0]
    ]
  }
  ```
