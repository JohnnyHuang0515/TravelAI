-- Migration 006: 新增 Google OAuth 欄位
-- 為 users 表新增 Google OAuth 相關欄位

-- 新增 google_id 欄位
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255);

-- 新增 avatar_url 欄位
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);

-- 為 google_id 建立唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL;

-- 更新約束（允許 Google OAuth 使用者不需要密碼）
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_auth_method;

ALTER TABLE users ADD CONSTRAINT check_auth_method CHECK (
    (provider = 'email' AND password_hash IS NOT NULL) OR
    (provider IN ('google', 'facebook') AND (provider_id IS NOT NULL OR google_id IS NOT NULL))
);

-- 註解
COMMENT ON COLUMN users.google_id IS 'Google OAuth 使用者 ID';
COMMENT ON COLUMN users.avatar_url IS '使用者頭像 URL';
