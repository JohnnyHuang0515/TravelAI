#!/usr/bin/env python3
"""
資料庫 Migration 執行腳本
使用方法: python3 scripts/run_migration.py [migration_file]
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from datetime import datetime

# 加入專案路徑
sys.path.append(str(Path(__file__).parent.parent))

def get_db_url():
    """從環境變數取得資料庫連線 URL"""
    return os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:password@localhost:5432/itinerary_db'
    )

def run_migration(migration_file: str):
    """執行指定的 Migration SQL 檔案"""
    
    migration_path = Path(__file__).parent / 'migrations' / migration_file
    
    if not migration_path.exists():
        print(f"❌ Migration 檔案不存在: {migration_path}")
        return False
    
    # 讀取 SQL 檔案
    print(f"📖 讀取 Migration: {migration_file}")
    with open(migration_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 連接資料庫
    db_url = get_db_url()
    print(f"🔌 連接資料庫: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            print(f"🚀 開始執行 Migration...")
            start_time = datetime.now()
            
            # 執行 SQL
            conn.execute(text(sql_content))
            conn.commit()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"✅ Migration 執行成功！耗時: {elapsed:.2f} 秒")
            
            # 顯示新建立的表
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename;
            """))
            
            tables = [row[0] for row in result]
            print(f"\n📊 資料庫表格列表 ({len(tables)} 個):")
            for table in tables:
                print(f"   - {table}")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration 執行失敗:")
        print(f"   錯誤訊息: {str(e)}")
        return False
    finally:
        engine.dispose()

def list_migrations():
    """列出所有可用的 Migration 檔案"""
    migrations_dir = Path(__file__).parent / 'migrations'
    
    if not migrations_dir.exists():
        print("❌ migrations 目錄不存在")
        return
    
    migrations = sorted(migrations_dir.glob('*.sql'))
    
    print("📋 可用的 Migration 檔案:")
    for i, migration in enumerate(migrations, 1):
        print(f"   {i}. {migration.name}")

def main():
    """主程式"""
    print("=" * 60)
    print("🗄️  資料庫 Migration 工具")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 scripts/run_migration.py <migration_file>")
        print("  python3 scripts/run_migration.py list")
        print()
        list_migrations()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_migrations()
    else:
        migration_file = command if command.endswith('.sql') else f"{command}.sql"
        success = run_migration(migration_file)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
