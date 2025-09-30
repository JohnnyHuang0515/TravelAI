#!/usr/bin/env python3
"""
資料庫初始化腳本
用於 Docker Compose 啟動時自動初始化資料庫
"""

import os
import sys
import time
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# 加入專案路徑
sys.path.append(str(Path(__file__).parent.parent))

def get_db_url():
    """從環境變數取得資料庫連線 URL"""
    return os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:password@postgres:5432/itinerary_db'
    )

def wait_for_database(max_retries=30, delay=2):
    """等待資料庫啟動"""
    print("🔄 等待資料庫啟動...")
    
    for attempt in range(max_retries):
        try:
            db_url = get_db_url()
            engine = create_engine(db_url)
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ 資料庫連接成功！")
            engine.dispose()
            return True
            
        except OperationalError as e:
            print(f"⏳ 嘗試 {attempt + 1}/{max_retries}: 資料庫尚未就緒...")
            time.sleep(delay)
        except Exception as e:
            print(f"❌ 資料庫連接錯誤: {e}")
            time.sleep(delay)
    
    print("❌ 資料庫啟動超時！")
    return False

def enable_postgis():
    """啟用 PostGIS 擴展"""
    print("🗺️ 啟用 PostGIS 擴展...")
    
    db_url = get_db_url()
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # 啟用 PostGIS 擴展
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology;"))
            conn.commit()
            print("✅ PostGIS 擴展啟用成功！")
            
    except Exception as e:
        print(f"❌ PostGIS 擴展啟用失敗: {e}")
        return False
    finally:
        engine.dispose()
    
    return True

def create_tables():
    """建立資料表"""
    print("🏗️ 建立資料表...")
    
    try:
        # 導入 ORM 模型
        from src.itinerary_planner.infrastructure.persistence.orm_models import Base
        from src.itinerary_planner.infrastructure.persistence.database import engine
        
        # 建立所有資料表
        Base.metadata.create_all(bind=engine)
        print("✅ 資料表建立成功！")
        
        # 顯示建立的表
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename;
            """))
            
            tables = [row[0] for row in result]
            print(f"📊 已建立 {len(tables)} 個資料表:")
            for table in tables:
                print(f"   - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ 資料表建立失敗: {e}")
        return False

def run_migrations():
    """執行資料庫遷移"""
    print("🔄 執行資料庫遷移...")
    
    migrations_dir = Path(__file__).parent / 'migrations'
    
    if not migrations_dir.exists():
        print("⚠️ migrations 目錄不存在，跳過遷移")
        return True
    
    db_url = get_db_url()
    engine = create_engine(db_url)
    
    try:
        # 執行所有 SQL 遷移檔案
        migration_files = sorted(migrations_dir.glob('*.sql'))
        
        for migration_file in migration_files:
            # 跳過參考檔案
            if 'reference' in migration_file.name.lower():
                print(f"⏭️ 跳過參考檔案: {migration_file.name}")
                continue
                
            print(f"📖 執行遷移: {migration_file.name}")
            
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read().strip()
            
            # 跳過空檔案或只有註解的檔案
            if not sql_content or sql_content.startswith('--'):
                print(f"⏭️ 跳過空檔案: {migration_file.name}")
                continue
            
            with engine.connect() as conn:
                conn.execute(text(sql_content))
                conn.commit()
            
            print(f"✅ 遷移完成: {migration_file.name}")
        
        print("✅ 所有遷移執行完成！")
        return True
        
    except Exception as e:
        print(f"❌ 遷移執行失敗: {e}")
        return False
    finally:
        engine.dispose()

def main():
    """主程式"""
    print("=" * 60)
    print("🚀 智慧旅遊系統 - 資料庫初始化")
    print("=" * 60)
    print()
    
    # 1. 等待資料庫啟動
    if not wait_for_database():
        sys.exit(1)
    
    # 2. 啟用 PostGIS 擴展
    if not enable_postgis():
        sys.exit(1)
    
    # 3. 建立資料表
    if not create_tables():
        sys.exit(1)
    
    # 4. 執行遷移
    if not run_migrations():
        sys.exit(1)
    
    print()
    print("🎉 資料庫初始化完成！")
    print("系統已準備就緒，可以開始使用。")
    print("=" * 60)

if __name__ == '__main__':
    main()
