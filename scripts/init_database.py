#!/usr/bin/env python3
"""
資料庫初始化腳本
功能：
1. 等待資料庫就緒
2. 啟用必要的 PostgreSQL 擴展（PostGIS, pgvector）
3. 建立所有資料表
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_db(database_url: str, max_retries: int = 30, retry_interval: int = 2):
    """
    等待資料庫就緒
    
    Args:
        database_url: 資料庫連接 URL
        max_retries: 最大重試次數
        retry_interval: 重試間隔（秒）
    """
    logger.info("等待資料庫就緒...")
    
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"✅ 資料庫連接成功！")
            engine.dispose()
            return True
        except OperationalError as e:
            if attempt < max_retries:
                logger.warning(f"嘗試 {attempt}/{max_retries} - 資料庫尚未就緒，{retry_interval}秒後重試...")
                time.sleep(retry_interval)
            else:
                logger.error(f"❌ 資料庫連接失敗：{e}")
                return False
    
    return False


def enable_extensions(engine):
    """
    啟用必要的 PostgreSQL 擴展
    
    Args:
        engine: SQLAlchemy engine
    """
    extensions = [
        ('postgis', 'PostGIS 地理空間擴展'),
        # ('vector', 'pgvector 向量擴展'),  # 如果需要向量搜尋功能
    ]
    
    logger.info("檢查並啟用 PostgreSQL 擴展...")
    
    with engine.connect() as conn:
        for ext_name, ext_desc in extensions:
            try:
                # 檢查擴展是否已存在
                result = conn.execute(text(
                    f"SELECT 1 FROM pg_extension WHERE extname = '{ext_name}'"
                ))
                
                if result.fetchone():
                    logger.info(f"✅ {ext_desc} ({ext_name}) 已啟用")
                else:
                    # 啟用擴展
                    conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext_name}"))
                    conn.commit()
                    logger.info(f"✅ 成功啟用 {ext_desc} ({ext_name})")
                    
            except Exception as e:
                logger.warning(f"⚠️  無法啟用 {ext_desc}: {e}")
                # PostGIS 可能需要超級使用者權限，但不應該導致失敗
                # 因為可能已經在資料庫創建時啟用


def create_tables(engine):
    """
    建立所有資料表
    
    Args:
        engine: SQLAlchemy engine
    """
    logger.info("開始建立資料表...")
    
    try:
        # 導入 Base 和所有模型
        from itinerary_planner.infrastructure.persistence.database import Base
        from itinerary_planner.infrastructure.persistence.orm_models import (
            Place, Accommodation, Hour, 
            User, UserPreference,
            UserTrip, TripDay, TripDayItem,
            PlaceFavorite, PlaceVisit,
            ConversationSession, Message, FeedbackEvent
        )
        
        # 建立所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ 資料表建立完成！")
        
        # 顯示已建立的表
        with engine.connect() as conn:
            result = conn.execute(text(
                """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
                """
            ))
            tables = [row[0] for row in result]
            logger.info(f"📊 已建立 {len(tables)} 個資料表：")
            for table in tables:
                logger.info(f"   - {table}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 建立資料表失敗：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主程序"""
    # 從環境變數讀取資料庫 URL
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/itinerary_db"
    )
    
    logger.info("=" * 60)
    logger.info("🚀 TravelAI 資料庫初始化")
    logger.info("=" * 60)
    logger.info(f"資料庫 URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    logger.info("")
    
    # 1. 等待資料庫就緒
    if not wait_for_db(database_url):
        logger.error("❌ 資料庫初始化失敗：無法連接到資料庫")
        sys.exit(1)
    
    # 2. 建立 engine
    engine = create_engine(database_url)
    
    # 3. 啟用擴展
    enable_extensions(engine)
    
    # 4. 建立資料表
    if not create_tables(engine):
        logger.error("❌ 資料庫初始化失敗：無法建立資料表")
        engine.dispose()
        sys.exit(1)
    
    # 5. 完成
    engine.dispose()
    logger.info("")
    logger.info("=" * 60)
    logger.info("🎉 資料庫初始化完成！")
    logger.info("=" * 60)
    logger.info("")
    logger.info("💡 下一步：")
    logger.info("   1. 匯入資料：python scripts/unified_data_importer.py")
    logger.info("   2. 啟動後端：uvicorn src.itinerary_planner.main:app --reload")
    logger.info("")


if __name__ == "__main__":
    main()

