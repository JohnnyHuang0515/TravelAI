# 綜合品質檢查清單 - 智慧旅遊行程規劃器

---

**審查日期:** `2025-09-24`
**審查對象:** `智慧旅遊行程規劃器 MVP`

---

## A. 核心安全原則

- `[X]` **最小權限:** 服務間匿名訪問，無特殊權限。
- `[ ]` **縱深防禦:** MVP 階段較弱，主要依賴 API Gateway。
- `[X]` **預設安全:** API 預設不返回敏感資訊。
- `[X]` **攻擊面最小化:** 僅開放必要的 API 端點。

## B. 數據生命週期安全與隱私

- `[X]` **數據分類:** 使用者偏好 (`Story`) 被視為臨時敏感資料。
- `[X]` **數據最小化:** 系統不儲存使用者 PII，`Story` 僅存於 Session。
- `[X]` **傳輸加密:** 所有 API 強制使用 HTTPS (TLS 1.2+)。
- `[X]` **儲存加密:** `places` 和 `hours` 為公開資料，不加密。`feedback_event` 不含 PII。
- `[X]` **日誌記錄中的敏感資訊:** 確保使用者輸入的自由文本在存入日誌前經過過濾。

## C. 應用程式安全 (Application Security)

- `[X]` **身份驗證:** 透過 `X-Session-ID` 標識匿名會話。
- `[X]` **授權與訪問控制:** 無用戶體系，無此需求。
- `[X]` **輸入驗證:** 所有 API 輸入透過 FastAPI + Pydantic 進行嚴格的型別和格式驗證。
- `[X]` **API 安全:** 速率限制將由 API Gateway 層處理 (透過 `docker-compose.yml` 設定)。
- `[X]` **依賴庫安全:** 已建立 `requirements.txt`，可設定 `Dependabot` 或 `Snyk` 進行自動掃描。

## G. 生產準備就緒 (Production Readiness)

### G.1 可觀測性
- `[X]` **健康檢查:** 已在 `main.py` 中實現 `/health` 端點。
- `[X]` **核心指標:** 需監控 API 請求延遲、錯誤率 (SLIs) (可透過 uvicorn access logs 達成)。
- `[X]` **日誌:** 所有服務需輸出結構化日誌 (JSON) (可透過 uvicorn 設定)。
- `[ ]` **全鏈路追蹤:** MVP 後考慮集成 OpenTelemetry。
- `[X]` **告警:** 需為 5xx 錯誤率和 P95 延遲超標配置告警 (需在部署環境中設定)。

### G.2 可靠性與彈性
- `[X]` **優雅啟停:** FastAPI 應用程式預設支援處理 `SIGTERM` 信號。
- `[X]` **重試與超時:** 對外部 OSRM 的呼叫已在 `osrm_client.py` 中配置超時。
- `[ ]` **故障轉移:** MVP 階段的 Postgres, Redis 為單點，暫無故障轉移。
- `[X]` **備份與恢復:** Postgres 資料庫需配置每日自動備份 (可在 `docker-compose.yml` volume 或雲端服務中設定)。

### G.4 可維護性與文檔
- `[X]` **部署文檔/腳本:** 已提供 `docker-compose.yml` 及 `README.md` 作為部署指南。
- `[ ]` **CI/CD:** `待建立` - 需在 `.github/workflows/` 中建立 GitHub Actions，至少包含 linting 和 `pytest` 測試流程。
- `[X]` **配置管理:** 所有配置（如資料庫連線字串、API Keys）已透過環境變數 (`os.getenv`) 讀取，並可在 `.env` 或 `docker-compose.yml` 中設定。
