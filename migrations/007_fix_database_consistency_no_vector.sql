-- Migration: 007_fix_database_consistency_no_vector.sql
-- 描述: 修正資料庫設計一致性问题（不包含向量功能）
-- 日期: 2025-01-27
-- 版本: v2.1

BEGIN;

-- ============================================================================
-- 1. 移除重複的 Google OAuth 欄位
-- ============================================================================

-- 移除重複的 google_id 欄位（統一使用 provider_id）
ALTER TABLE users DROP COLUMN IF EXISTS google_id;

-- 移除相關的索引
DROP INDEX IF EXISTS idx_users_google_id;

-- ============================================================================
-- 2. 統一時間戳記類型為 TIMESTAMPTZ
-- ============================================================================

-- 更新 users 表的時間戳記類型
ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';
ALTER TABLE users ALTER COLUMN last_login TYPE TIMESTAMPTZ USING last_login AT TIME ZONE 'UTC';

-- 更新 user_preferences 表的時間戳記類型
ALTER TABLE user_preferences ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';
ALTER TABLE user_preferences ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC';

-- 更新 user_trips 表的時間戳記類型
ALTER TABLE user_trips ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';
ALTER TABLE user_trips ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC';

-- 更新 trip_days 表的時間戳記類型
ALTER TABLE trip_days ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';

-- 更新 trip_visits 表的時間戳記類型
ALTER TABLE trip_visits ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';

-- 更新 place_favorites 表的時間戳記類型
ALTER TABLE place_favorites ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';

-- 更新 conversation_sessions 表的時間戳記類型
ALTER TABLE conversation_sessions ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';
ALTER TABLE conversation_sessions ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC';
ALTER TABLE conversation_sessions ALTER COLUMN expires_at TYPE TIMESTAMPTZ USING expires_at AT TIME ZONE 'UTC';

-- 更新 feedback_events 表的時間戳記類型
ALTER TABLE feedback_events ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';

-- 更新 places 表的時間戳記類型
ALTER TABLE places ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';
ALTER TABLE places ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC';

-- 更新 accommodations 表的時間戳記類型
ALTER TABLE accommodations ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC';
ALTER TABLE accommodations ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC';

-- ============================================================================
-- 3. 修正約束條件一致性
-- ============================================================================

-- 移除舊的約束
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_auth_method;

-- 新增統一的約束條件
ALTER TABLE users ADD CONSTRAINT check_auth_method CHECK (
    (provider = 'email' AND password_hash IS NOT NULL) OR
    (provider IN ('google', 'facebook') AND provider_id IS NOT NULL)
);

-- ============================================================================
-- 4. 新增必要的索引
-- ============================================================================

-- 為 provider_id 建立索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_users_provider_id ON users(provider_id) WHERE provider_id IS NOT NULL;

-- ============================================================================
-- 5. 更新觸發器函數以支援 TIMESTAMPTZ
-- ============================================================================

-- 更新觸發器函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 確保所有觸發器都使用新的函數
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

-- 為 places 和 accommodations 表新增觸發器
DROP TRIGGER IF EXISTS update_places_updated_at ON places;
CREATE TRIGGER update_places_updated_at
    BEFORE UPDATE ON places
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_accommodations_updated_at ON accommodations;
CREATE TRIGGER update_accommodations_updated_at
    BEFORE UPDATE ON accommodations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;

-- ============================================================================
-- Migration 完成
-- ============================================================================

-- 驗證查詢
SELECT 
    schemaname,
    tablename,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE schemaname = 'public'
  AND table_name IN ('users', 'places', 'user_trips', 'conversation_sessions')
  AND column_name IN ('created_at', 'updated_at', 'last_login', 'expires_at')
ORDER BY table_name, column_name;
