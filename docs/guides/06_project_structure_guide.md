# 專案結構指南 - 智慧旅遊行程規劃器

---

## 1. 核心設計原則

- **按功能組織 (Organize by Feature):** 相關的功能（規劃、檢索）應盡可能放在一起。
- **依賴倒置:** 業務邏輯應依賴抽象（接口），而非具體實現（資料庫）。
- **根目錄簡潔:** 原始碼統一放在 `src/` 目錄下。

## 2. 頂層目錄結構

```plaintext
./
├── configs/              # 環境配置文件 (e.g., settings.toml)
├── data/                 # 初始 POI 資料
├── docs/                 # 所有專案文檔 (PRD, SAD, ADRs...)
├── src/
│   └── itinerary_planner/ # 應用程式主包
├── tests/                # 測試代碼
├── .env                  # 環境變數
├── .gitignore
├── docker compose.yml    # Docker Compose 部署文件
├── Dockerfile            # API 服務的 Dockerfile
└── README.md
```

## 3. `src/itinerary_planner/` 應用程式原始碼結構

採用 Clean Architecture 分層思想。

```plaintext
src/itinerary_planner/
├── __init__.py
├── main.py                 # FastAPI 應用實例與根路由

├── api/                    # Presentation Layer: API 路由/端點
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── endpoints/
│           ├── __init__.py
│           ├── planning.py # /itinerary/*
│           └── places.py   # /places/*

├── core/                   # 跨功能共享的核心邏輯
│   ├── __init__.py
│   └── config.py           # 配置加載

├── domain/                 # Domain Layer: 業務核心
│   ├── __init__.py
│   ├── models/             # Pydantic 模型 (Story, Itinerary, Place)
│   └── interfaces/         # 抽象接口定義
│       ├── __init__.py
│       ├── place_repository.py
│       └── travel_time_calculator.py

├── application/            # Application Layer: 應用程式邏輯
│   ├── __init__.py
│   ├── services/
│   │   └── planning_service.py # 編排規劃流程的 Use Case
│   └── schemas/
│       └── dtos.py           # 數據傳輸對象

└── infrastructure/         # Infrastructure Layer: 外部世界的實現
    ├── __init__.py
    ├── repositories/
    │   └── postgres_place_repo.py # PlaceRepository 的 Postgres 實現
    ├── clients/
    │   ├── __init__.py
    │   ├── osrm_client.py
    │   └── llm_client.py
    └── persistence/
        └── database.py       # 資料庫連線管理
```
