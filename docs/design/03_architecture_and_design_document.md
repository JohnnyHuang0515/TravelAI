# 整合性架構與設計文件 - 智慧旅遊行程規劃器

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-09-24`
**主要作者 (Lead Author):** `Gemini`
**審核者 (Reviewers):** `使用者`
**狀態 (Status):** `草稿 (Draft)`

---

## 目錄

- [1. 架構總覽](#1-架構總覽)
- [2. DDD 戰略設計](#2-ddd-戰略設計)
- [3. 技術選型與決策](#3-技術選型與決策)
- [4. 詳細設計](#4-詳細設計)
- [5. 資料庫設計](#5-資料庫設計)
- [6. 風險與緩解](#6-風險與緩解)

---

## 1. 架構總覽

本專案採用以 API 為中心的微服務化架構，透過 Docker Compose 進行部署，各服務分工明確，易於擴展與維護。

### 1.1 C4 模型：容器圖 (Container Diagram)

此圖描述了系統由哪些可部署單元組成，以及它們之間的互動關係。

```mermaid
graph TD
    subgraph "使用者"
        Client[對話式客戶端]
    end

    subgraph "系統邊界"
        APIGateway[API Gateway / FastAPI]
        
        subgraph "核心服務"
            NLU[NLU 抽取 (LLM)]
            Planner[輕量規劃器]
            Generator[回答生成 (LLM)]
        end

        subgraph "支撐服務"
            Retriever[檢索服務]
            TravelTime[交通時間服務]
        end

        subgraph "資料與快取"
            Postgres[(Postgres + PostGIS)]
            VectorDB[(向量資料庫)]
            Redis[(Redis 快取)]
        end

        subgraph "外部依賴"
            OSRM[OSRM 引擎]
        end
    end

    Client --> APIGateway
    APIGateway --> NLU
    APIGateway --> Planner
    APIGateway --> Generator
    
    Planner --> Retriever
    Planner --> TravelTime
    
    Retriever --> Postgres
    Retriever --> VectorDB
    Retriever --> Redis
    
    TravelTime --> OSRM
    TravelTime --> Redis

    classDef user fill:#cce5ff,stroke:#333;
    classDef system fill:#e6f3ff,stroke:#333;
    classDef service fill:#d5f5e3,stroke:#333;
    classDef data fill:#fff0b3,stroke:#333;
    classDef external fill:#f5e6cc,stroke:#333;

    class Client user;
    class APIGateway system;
    class NLU,Planner,Generator service;
    class Retriever,TravelTime service;
    class Postgres,VectorDB,Redis data;
    class OSRM external;
```

### 1.2 Clean Architecture 分層

系統內部遵循 Clean Architecture 原則，確保關注點分離：
- **Domain Layer**: 定義核心業務實體（如 `Place`, `Story`, `Itinerary`）和規則。
- **Application Layer**: 編排 Use Cases，如 `ProposeItinerary`、`RefineItinerary`。
- **Infrastructure Layer**: 實現與外部世界的互動，如資料庫訪問 (Repositories)、LLM 客戶端、OSRM 客戶端。

## 2. DDD 戰略設計

- **通用語言 (Ubiquitous Language)**: 行程 (Itinerary), 景點 (Place/POI), 時間窗 (Time Window), 偏好 (Preference), 約束 (Constraint)。
- **限界上下文 (Bounded Contexts)**:
    - **Catalog**: 管理地點（Place）及其屬性（營業時間、標籤等）。
    - **Conversation**: 管理對話狀態，理解使用者故事（Story）與約束（Constraints）。
    - **Mobility**: 負責計算不同地點間的交通時間矩陣。
    - **Planner**: 核心規劃上下文，負責生成與優化行程（Itinerary）。
    - **Scoring**: 根據使用者偏好對候選點進行打分。

## 3. 技術選型與決策

| 分類 | 選用技術 | 選擇理由 | 相關 ADR |
| :--- | :--- | :--- | :--- |
| **後端框架** | Python / FastAPI | 高性能、非同步、自動化 API 文件、Pydantic 強大的型別驗證。 | `ADR-001` |
| **結構化資料庫** | PostgreSQL + PostGIS | 強大的地理空間查詢能力，成熟穩定。 | `ADR-002` |
| **向量資料庫** | Milvus / pgvector | 用於高效的語義相似度檢索。 | `ADR-002` |
| **快取** | Redis | 緩存 OSRM 距離矩陣和熱門查詢結果，降低延遲。 | |
| **路網計算** | OSRM | 開源、高效，可自行部署，適合計算大規模距離矩陣。 | |
| **對話狀態管理**| LangGraph | 適合構建基於 LLM 的、有狀態的、循環的應用程式。 | `ADR-003` |
| **部署** | Docker Compose | 在 MVP 階段能快速、簡單地編排所有服務。 | |

## 4. 詳細設計

### 4.1 對話狀態機 (LangGraph)
- **狀態槽位**: `user_input`, `story`, `structured_candidates`, `semantic_candidates`, `candidates`, `itinerary`, `error`。
- **節點 (Nodes in `graph_nodes.py`):**
    1.  `extract_story`: **(Input: `user_input`)** 呼叫 LLM 客戶端將使用者輸入轉為 `Story` JSON。**(Output: `story`)**
    2.  `retrieve_places_structured`: **(Input: `story`)** 執行並行的結構化檢索。**(Output: `structured_candidates`)**
    3.  `retrieve_places_semantic`: **(Input: `story`)** 執行並行的語義檢索。**(Output: `semantic_candidates`)**
    4.  `rank_and_merge`: **(Input: `structured_candidates`, `semantic_candidates`, `story`)** 融合兩路結果，並使用 `RerankService` 進行重排序。**(Output: `candidates`)**
    5.  `plan_itinerary`: **(Input: `story`, `candidates`)** 異步執行以下操作：
        a. 呼叫 `OSRMClient` 獲取交通時間矩陣。
        b. 使用 `GreedyPlanner` 生成初步行程。
        c. 對每日行程應用 `_refine_with_2_opt` 進行局部優化。
        **(Output: `itinerary`)**
- **回饋處理 (Feedback Handling - not in graph):**
    - `POST /feedback` API 會呼叫 `FeedbackParser` 將自然語言轉為 DSL。
    - `PlanningService` 的 `handle_feedback` 方法會接收 DSL 並對現有 `Itinerary` 物件進行修改。

### 4.2 檢索與重排 (Hybrid Search)
1.  **SQL Filter**: `WHERE ST_DWithin(geom, :origin, :radius) AND categories && :cats AND ...`
2.  **Vector Search**: `embedding.cosine_similarity(query_vec) > :threshold`
3.  **Rerank**: `Score = α*semantic_sim + β*rating + γ*dist_score + ...`，其中 `α,β,γ` 根據 `Story.pace` 等偏好動態調整。

### 4.3 規劃與可行性
- **可行性檢查**:
    - 時間窗：`visit.eta >= poi.open_time AND visit.etd <= poi.close_time`
    - 總時長：`SUM(travel_min + stay_min) <= daily_window`
    - 約束：`must_have` 全覆蓋，`must_not` 不出現。
- **失敗處理**: 自動修補序列（重排 -> 改時長 -> 換天 -> 擴半徑 -> 替代點），若仍失敗則提供選項由使用者裁決。

## 5. 資料庫設計

### 5.1 `places`
```sql
CREATE TABLE places (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    geom GEOMETRY(Point, 4326), -- SRID 4326 for WGS 84
    categories TEXT[],
    tags TEXT[],
    stay_minutes INT DEFAULT 60,
    price_range INT,
    rating NUMERIC(2,1)
);
CREATE INDEX places_geom_idx ON places USING GIST (geom);
CREATE INDEX places_categories_idx ON places USING GIN (categories);
```

### 5.2 `hours`
```sql
CREATE TABLE hours (
    place_id UUID REFERENCES places(id),
    weekday INT, -- 0=Sunday, 1=Monday, ...
    open_min INT, -- minutes from midnight
    close_min INT, -- minutes from midnight (close_min < open_min for overnight)
    PRIMARY KEY (place_id, weekday, open_min)
);
```

### 5.3 `feedback_event`
```sql
CREATE TABLE feedback_event (
  id BIGSERIAL PRIMARY KEY,
  session_id TEXT,
  place_id UUID,
  op TEXT, -- 'DROP', 'REPLACE', 'MOVE'
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## 6. 風險與緩解

| 風險分類 | 風險描述 | 緩解策略 |
| :--- | :--- | :--- |
| **資料品質** | 營業時間不準確或格式混亂 | 優先使用結構化來源，對熱門點人工校核，建立使用者回饋閉環 (`feedback_event`)。 |
| **交通時間** | OSRM 時間未考慮即時路況與尖峰 | 引入分時段、分區域的交通緩衝係數（e.g., `t_final = t_osrm * 1.2`）。 |
| **LLM 漂移** | LLM 輸出格式不穩定 | 對 LLM 的 JSON 輸出強制使用 Pydantic Schema 進行驗證與解析。 |
| **冷啟動** | 新區域或新使用者無快取 | 可預先計算熱門區域的交通時間矩陣；對新使用者採用更通用的推薦策略。 |
