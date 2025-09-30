-- Migration Reference: 000_existing_tables_reference.sql
-- 描述: 現有資料表結構參考（已存在，不需執行）
-- 日期: 2025-09-24（參考用）
-- 版本: v1.0

-- ============================================================================
-- 此檔案僅供參考，記錄系統已存在的資料表結構
-- 請勿執行此腳本
-- ============================================================================

-- ============================================================================
-- 1. 景點表 (places) - 已存在
-- ============================================================================

/*
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    geom GEOMETRY(Point, 4326),  -- WGS84 座標
    categories TEXT[],  -- ['美食', '景點', '住宿']
    tags TEXT[],  -- ['親子', '網美', '戶外']
    stay_minutes INT DEFAULT 60,
    price_range INT,  -- 1-5
    rating NUMERIC(2,1),  -- 0.0-5.0
    description TEXT,
    address TEXT,
    phone VARCHAR(50),
    website VARCHAR(500),
    photo_urls TEXT[],
    source VARCHAR(50),  -- 'tdx', 'google', 'manual'
    source_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX places_geom_idx ON places USING GIST (geom);
CREATE INDEX places_categories_idx ON places USING GIN (categories);
CREATE INDEX places_rating_idx ON places (rating DESC);
*/

-- ============================================================================
-- 2. 營業時間表 (hours) - 已存在
-- ============================================================================

/*
CREATE TABLE hours (
    place_id UUID REFERENCES places(id),
    weekday INT,  -- 0=Sunday, 1=Monday, ..., 6=Saturday
    open_min INT,  -- 從午夜起算的分鐘數
    close_min INT,  -- 從午夜起算的分鐘數
    PRIMARY KEY (place_id, weekday, open_min)
);

CREATE INDEX hours_lookup_idx ON hours (place_id, weekday);
*/

-- ============================================================================
-- 3. 住宿表 (accommodations) - 已存在
-- ============================================================================

/*
CREATE TABLE accommodations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    geom GEOMETRY(Point, 4326),
    type VARCHAR(50) NOT NULL,  -- 'hotel', 'hostel', 'homestay'
    price_range INT,  -- 1-5
    rating NUMERIC(2,1),
    check_in_time TIME DEFAULT '15:00',
    check_out_time TIME DEFAULT '11:00',
    amenities TEXT[],  -- ['WiFi', 'Parking', 'Breakfast', ...]
    address TEXT,
    phone VARCHAR(50),
    website VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX accommodations_geom_idx ON accommodations USING GIST (geom);
CREATE INDEX accommodations_rating_idx ON accommodations (rating DESC);
*/

-- ============================================================================
-- 資料表關係圖
-- ============================================================================

/*
現有結構:
  places (景點)
    ├── hours (營業時間)
    └── [待新增: place_favorites (收藏)]
  
  accommodations (住宿)
    └── [待新增: trip_days (行程天數) - FK]

待新增結構（Migration 001）:
  users (使用者)
    ├── user_preferences (偏好)
    ├── user_trips (行程)
    │   ├── trip_days (天數)
    │   │   └── trip_visits (訪問)
    │   │       └── places (景點) - FK
    │   │   └── accommodations (住宿) - FK
    ├── place_favorites (收藏)
    │   └── places (景點) - FK
    └── conversation_sessions (對話)
*/
