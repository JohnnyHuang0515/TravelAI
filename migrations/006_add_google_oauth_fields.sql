-- Migration 006: 新增 OAuth 支援欄位
-- 為 users 表新增 OAuth 相關欄位

-- 新增 avatar_url 欄位
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);

-- 為 provider_id 建立索引（統一使用此欄位處理所有 OAuth）
CREATE INDEX IF NOT EXISTS idx_users_provider_id ON users(provider_id) WHERE provider_id IS NOT NULL;

-- 更新約束（統一使用 provider_id 欄位）
ALTER TABLE users DROP CONSTRAINT IF EXISTS check_auth_method;

ALTER TABLE users ADD CONSTRAINT check_auth_method CHECK (
    (provider = 'email' AND password_hash IS NOT NULL) OR
    (provider IN ('google', 'facebook') AND provider_id IS NOT NULL)
);

-- 註解
COMMENT ON COLUMN users.provider_id IS 'OAuth 提供者使用者 ID（統一欄位）';
COMMENT ON COLUMN users.avatar_url IS '使用者頭像 URL';
