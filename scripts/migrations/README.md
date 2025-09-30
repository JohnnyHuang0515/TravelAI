# 資料庫 Migration 指引

## 📁 目錄結構

```
scripts/migrations/
├── 000_existing_tables_reference.sql  # 現有表格參考（僅供參考）
├── 001_create_user_system_tables.sql  # 會員系統表格
└── README.md                          # 本檔案
```

## 🚀 執行 Migration

### 方法 1: 使用 Python 腳本（推薦）

```bash
# 1. 列出所有可用的 Migration
python3 scripts/run_migration.py list

# 2. 執行特定 Migration
python3 scripts/run_migration.py 001_create_user_system_tables.sql

# 或簡寫
python3 scripts/run_migration.py 001_create_user_system_tables
```

### 方法 2: 直接使用 psql

```bash
# 設定環境變數
export DATABASE_URL="postgresql://postgres:password@localhost:5432/itinerary_db"

# 執行 Migration
psql $DATABASE_URL -f scripts/migrations/001_create_user_system_tables.sql
```

## 📋 Migration 清單

### ✅ 000 - 現有表格參考
- **檔案**: `000_existing_tables_reference.sql`
- **狀態**: 僅供參考，不需執行
- **內容**: 記錄現有的 `places`, `hours`, `accommodations` 表格結構

### 🆕 001 - 會員系統表格
- **檔案**: `001_create_user_system_tables.sql`
- **狀態**: 待執行
- **建立表格**:
  1. `users` - 使用者帳號
  2. `user_preferences` - 使用者偏好
  3. `user_trips` - 會員行程記錄
  4. `trip_days` - 行程天數明細
  5. `trip_visits` - 行程景點訪問
  6. `place_favorites` - 景點收藏
  7. `conversation_sessions` - 對話 Session
  8. `feedback_events` - 使用者回饋記錄

## 🔍 驗證 Migration

執行後驗證表格已建立：

```sql
-- 查看所有表格
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;

-- 查看表格大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看表格關聯
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;
```

## 🔄 Rollback（如需回滾）

如果需要刪除 Migration 001 建立的表格：

```sql
-- ⚠️ 警告：此操作會刪除所有會員相關資料
BEGIN;

DROP TABLE IF EXISTS feedback_events CASCADE;
DROP TABLE IF EXISTS conversation_sessions CASCADE;
DROP TABLE IF EXISTS place_favorites CASCADE;
DROP TABLE IF EXISTS trip_visits CASCADE;
DROP TABLE IF EXISTS trip_days CASCADE;
DROP TABLE IF EXISTS user_trips CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 刪除觸發器函數
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

COMMIT;
```

## 📝 新增 Migration 規範

當需要新增 Migration 時，請遵循以下規範：

1. **命名規則**: `{序號}_{描述}.sql`
   - 例如: `002_add_user_avatar_field.sql`

2. **檔案結構**:
   ```sql
   -- Migration: {檔名}
   -- 描述: {簡短說明}
   -- 日期: {YYYY-MM-DD}
   -- 版本: {版本號}
   
   BEGIN;
   
   -- SQL 語句
   
   COMMIT;
   ```

3. **最佳實踐**:
   - 使用 `IF NOT EXISTS` 避免重複建立
   - 加入適當的註解與說明
   - 建立必要的索引
   - 加入資料驗證約束（CHECK, UNIQUE）
   - 最後提供驗證查詢

## 🛠️ 開發環境設定

```bash
# 1. 確保資料庫已啟動
docker-compose up -d db

# 2. 設定環境變數
export DATABASE_URL="postgresql://postgres:password@localhost:5432/itinerary_db"

# 3. 執行 Migration
python3 scripts/run_migration.py 001_create_user_system_tables

# 4. 驗證 ORM 模型
python3 -c "from src.itinerary_planner.infrastructure.persistence.orm_models import *; print('✅ ORM 模型載入成功')"
```

## 📚 相關文件

- [系統架構設計文件](../../docs/系統架構設計文件.md)
- [TODO 清單](../../TODO.md)
- [ORM 模型](../../src/itinerary_planner/infrastructure/persistence/orm_models.py)
