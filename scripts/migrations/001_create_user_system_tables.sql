-- Migration: 001_create_user_system_tables.sql
-- 描述: 建立會員系統相關資料表
-- 日期: 2025-09-30
-- 版本: v2.0

BEGIN;

-- ============================================================================
-- 1. 使用者表 (users)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    password_hash VARCHAR(255),  -- 密碼雜湊（bcrypt）
    provider VARCHAR(50),  -- 'email', 'google', 'facebook'
    provider_id VARCHAR(255),  -- OAuth provider 的使用者 ID
    profile JSONB DEFAULT '{}',  -- {avatar, phone, bio, birth_date, gender, ...}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,  -- Email 是否已驗證
    CONSTRAINT check_auth_method CHECK (
        (provider = 'email' AND password_hash IS NOT NULL) OR
        (provider IN ('google', 'facebook') AND provider_id IS NOT NULL)
    )
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_provider ON users(provider, provider_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE users IS '使用者帳號資料表';
COMMENT ON COLUMN users.provider IS '認證提供者: email, google, facebook';
COMMENT ON COLUMN users.profile IS 'JSON 格式的使用者個人資料';

-- ============================================================================
-- 2. 使用者偏好設定表 (user_preferences)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    favorite_themes TEXT[],  -- ['美食', '自然', '文化', '歷史', '購物', '夜生活']
    travel_pace VARCHAR(20) DEFAULT 'moderate',  -- 'relaxed', 'moderate', 'packed'
    budget_level VARCHAR(20) DEFAULT 'moderate',  -- 'budget', 'moderate', 'luxury'
    default_daily_start TIME DEFAULT '09:00',  -- 預設每日開始時間
    default_daily_end TIME DEFAULT '18:00',  -- 預設每日結束時間
    custom_settings JSONB DEFAULT '{}',  -- 其他自訂設定
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id),
    CONSTRAINT check_travel_pace CHECK (travel_pace IN ('relaxed', 'moderate', 'packed')),
    CONSTRAINT check_budget_level CHECK (budget_level IN ('budget', 'moderate', 'luxury'))
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id);

COMMENT ON TABLE user_preferences IS '使用者旅遊偏好設定';
COMMENT ON COLUMN user_preferences.favorite_themes IS '喜愛的旅遊主題陣列';

-- ============================================================================
-- 3. 使用者行程記錄表 (user_trips)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    destination VARCHAR(255),  -- 主要目的地（如：宜蘭、台北）
    duration_days INT NOT NULL CHECK (duration_days > 0),
    start_date DATE,
    end_date DATE,
    itinerary_data JSONB NOT NULL,  -- 完整的行程 JSON 資料
    is_public BOOLEAN DEFAULT FALSE,  -- 是否公開分享
    share_token VARCHAR(64) UNIQUE,  -- 分享連結的 Token
    view_count INT DEFAULT 0,  -- 瀏覽次數
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT check_dates CHECK (end_date >= start_date)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_user_trips_user_id ON user_trips(user_id);
CREATE INDEX IF NOT EXISTS idx_user_trips_created ON user_trips(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_trips_public ON user_trips(is_public) WHERE is_public = TRUE;
CREATE INDEX IF NOT EXISTS idx_user_trips_destination ON user_trips(destination);
CREATE INDEX IF NOT EXISTS idx_user_trips_share_token ON user_trips(share_token) WHERE share_token IS NOT NULL;

COMMENT ON TABLE user_trips IS '使用者儲存的行程記錄';
COMMENT ON COLUMN user_trips.itinerary_data IS '完整的行程資料（JSON 格式）';
COMMENT ON COLUMN user_trips.share_token IS '公開分享的 Token';

-- ============================================================================
-- 4. 行程天數明細表 (trip_days)
-- ============================================================================

CREATE TABLE IF NOT EXISTS trip_days (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES user_trips(id) ON DELETE CASCADE,
    day_number INT NOT NULL CHECK (day_number > 0),  -- 第幾天
    date DATE NOT NULL,
    accommodation_id UUID REFERENCES accommodations(id) ON DELETE SET NULL,
    notes TEXT,  -- 當日備註
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trip_id, day_number)
);

CREATE INDEX IF NOT EXISTS idx_trip_days_trip ON trip_days(trip_id);
CREATE INDEX IF NOT EXISTS idx_trip_days_date ON trip_days(date);

COMMENT ON TABLE trip_days IS '行程的每日明細';

-- ============================================================================
-- 5. 行程景點訪問記錄表 (trip_visits)
-- ============================================================================

CREATE TABLE IF NOT EXISTS trip_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_day_id UUID REFERENCES trip_days(id) ON DELETE CASCADE,
    place_id UUID REFERENCES places(id) ON DELETE SET NULL,
    visit_order INT NOT NULL CHECK (visit_order > 0),  -- 當天的訪問順序
    eta TIME NOT NULL,  -- Estimated Time of Arrival
    etd TIME NOT NULL,  -- Estimated Time of Departure
    travel_minutes INT DEFAULT 0,  -- 到達該景點的交通時間（分鐘）
    notes TEXT,  -- 使用者對該景點的備註
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trip_day_id, visit_order)
);

CREATE INDEX IF NOT EXISTS idx_trip_visits_day ON trip_visits(trip_day_id);
CREATE INDEX IF NOT EXISTS idx_trip_visits_place ON trip_visits(place_id);

COMMENT ON TABLE trip_visits IS '行程中的景點訪問記錄';

-- ============================================================================
-- 6. 景點收藏表 (place_favorites)
-- ============================================================================

CREATE TABLE IF NOT EXISTS place_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    notes TEXT,  -- 收藏備註
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, place_id)
);

CREATE INDEX IF NOT EXISTS idx_favorites_user ON place_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_place ON place_favorites(place_id);
CREATE INDEX IF NOT EXISTS idx_favorites_created ON place_favorites(created_at DESC);

COMMENT ON TABLE place_favorites IS '使用者收藏的景點';

-- ============================================================================
-- 7. 對話 Session 表 (conversation_sessions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- 可為 NULL（訪客）
    session_id VARCHAR(255) UNIQUE NOT NULL,
    state_data JSONB DEFAULT '{}',  -- LangGraph 狀態資料
    last_user_input TEXT,  -- 最後一次使用者輸入
    last_ai_response TEXT,  -- 最後一次 AI 回應
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,  -- Session 過期時間
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_id ON conversation_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON conversation_sessions(expires_at) WHERE is_active = TRUE;

COMMENT ON TABLE conversation_sessions IS '對話 Session 狀態管理';
COMMENT ON COLUMN conversation_sessions.state_data IS 'LangGraph 完整狀態（JSON）';

-- ============================================================================
-- 8. 使用者回饋記錄表 (feedback_events) - 補強現有表
-- ============================================================================

CREATE TABLE IF NOT EXISTS feedback_events (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    trip_id UUID REFERENCES user_trips(id) ON DELETE SET NULL,
    place_id UUID,
    op VARCHAR(20),  -- 'DROP', 'REPLACE', 'MOVE', 'ADD'
    feedback_text TEXT,  -- 使用者原始回饋文字
    reason TEXT,  -- 修改原因
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT check_op CHECK (op IN ('DROP', 'REPLACE', 'MOVE', 'ADD'))
);

CREATE INDEX IF NOT EXISTS idx_feedback_session ON feedback_events(session_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback_events(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_trip ON feedback_events(trip_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback_events(created_at DESC);

COMMENT ON TABLE feedback_events IS '使用者回饋與修改記錄';

-- ============================================================================
-- 9. 更新觸發器 (Updated_at Trigger)
-- ============================================================================

-- 建立更新時間戳記的函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為需要的表建立觸發器
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_trips_updated_at ON user_trips;
CREATE TRIGGER update_user_trips_updated_at
    BEFORE UPDATE ON user_trips
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_conversation_sessions_updated_at ON conversation_sessions;
CREATE TRIGGER update_conversation_sessions_updated_at
    BEFORE UPDATE ON conversation_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 10. 權限設定（如有需要）
-- ============================================================================

-- 預留給生產環境的權限設定
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

COMMIT;

-- ============================================================================
-- Migration 完成
-- ============================================================================

-- 驗證查詢
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('users', 'user_preferences', 'user_trips', 'trip_days', 
                     'trip_visits', 'place_favorites', 'conversation_sessions', 
                     'feedback_events')
ORDER BY tablename;
