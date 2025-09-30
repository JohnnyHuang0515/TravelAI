#!/usr/bin/env python3
"""
為資料庫添加 embedding 欄位
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from sqlalchemy import text

def add_embedding_column():
    """為 places 表添加 embedding 欄位"""
    
    db = SessionLocal()
    try:
        # 啟用 pgvector 擴展
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
        
        # 添加 embedding 欄位
        db.execute(text("ALTER TABLE places ADD COLUMN IF NOT EXISTS embedding vector(384)"))
        db.commit()
        
        print("✅ 成功添加 embedding 欄位")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_embedding_column()
