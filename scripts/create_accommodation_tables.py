#!/usr/bin/env python3
"""
建立住宿資料庫表
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from sqlalchemy import text

def create_accommodation_tables():
    """建立住宿相關的資料庫表"""
    
    db = SessionLocal()
    try:
        print("🏨 **建立住宿資料庫表**")
        print("=" * 40)
        
        # 建立 accommodations 表
        create_accommodations_sql = """
        CREATE TABLE IF NOT EXISTS accommodations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            geom GEOMETRY(Point, 4326),
            type TEXT NOT NULL,  -- 'hotel', 'hostel', 'homestay'
            price_range INT,  -- 1-5 星級或價格區間
            rating NUMERIC(2,1),
            check_in_time TIME DEFAULT '15:00',
            check_out_time TIME DEFAULT '11:00',
            amenities TEXT[],  -- 設施列表
            address TEXT,
            phone TEXT,
            website TEXT,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        """
        
        db.execute(text(create_accommodations_sql))
        print("✅ 建立 accommodations 表")
        
        # 建立索引
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS accommodations_geom_idx ON accommodations USING GIST (geom);",
            "CREATE INDEX IF NOT EXISTS accommodations_type_idx ON accommodations (type);",
            "CREATE INDEX IF NOT EXISTS accommodations_rating_idx ON accommodations (rating);"
        ]
        
        for idx_sql in indexes_sql:
            db.execute(text(idx_sql))
        print("✅ 建立索引")
        
        # 建立 itinerary_accommodations 關聯表
        create_itinerary_accommodations_sql = """
        CREATE TABLE IF NOT EXISTS itinerary_accommodations (
            itinerary_id UUID,
            accommodation_id UUID REFERENCES accommodations(id),
            day_date DATE,
            check_in TIMESTAMPTZ,
            check_out TIMESTAMPTZ,
            PRIMARY KEY (itinerary_id, day_date)
        );
        """
        
        db.execute(text(create_itinerary_accommodations_sql))
        print("✅ 建立 itinerary_accommodations 關聯表")
        
        db.commit()
        print("\n🎉 **住宿資料庫表建立完成！**")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_accommodation_tables()
