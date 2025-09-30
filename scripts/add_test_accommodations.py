#!/usr/bin/env python3
"""
添加測試住宿資料
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation
from geoalchemy2 import WKTElement
import uuid

def add_test_accommodations():
    """添加測試住宿資料"""
    
    db = SessionLocal()
    try:
        print("🏨 **添加測試住宿資料**")
        print("=" * 40)
        
        # 宜蘭地區的測試住宿資料
        test_accommodations = [
            {
                "id": uuid.uuid4(),
                "name": "宜蘭礁溪溫泉飯店",
                "geom": WKTElement("POINT(121.7730 24.8310)", srid=4326),  # 礁溪
                "type": "hotel",
                "price_range": 4,
                "rating": 4.2,
                "address": "宜蘭縣礁溪鄉溫泉路",
                "amenities": ["溫泉", "停車場", "餐廳", "WiFi"]
            },
            {
                "id": uuid.uuid4(),
                "name": "羅東夜市民宿",
                "geom": WKTElement("POINT(121.7660 24.6770)", srid=4326),  # 羅東
                "type": "homestay",
                "price_range": 2,
                "rating": 3.8,
                "address": "宜蘭縣羅東鎮中正路",
                "amenities": ["WiFi", "停車場"]
            },
            {
                "id": uuid.uuid4(),
                "name": "宜蘭市青年旅館",
                "geom": WKTElement("POINT(121.7530 24.7580)", srid=4326),  # 宜蘭市
                "type": "hostel",
                "price_range": 1,
                "rating": 3.5,
                "address": "宜蘭縣宜蘭市中山路",
                "amenities": ["WiFi", "共用廚房", "洗衣機"]
            },
            {
                "id": uuid.uuid4(),
                "name": "頭城海景飯店",
                "geom": WKTElement("POINT(121.8220 24.8570)", srid=4326),  # 頭城
                "type": "hotel",
                "price_range": 3,
                "rating": 4.0,
                "address": "宜蘭縣頭城鎮濱海路",
                "amenities": ["海景", "停車場", "餐廳", "WiFi"]
            }
        ]
        
        for acc_data in test_accommodations:
            accommodation = Accommodation(**acc_data)
            db.add(accommodation)
            print(f"✅ 添加: {acc_data['name']} ({acc_data['type']})")
        
        db.commit()
        print(f"\n🎉 **成功添加 {len(test_accommodations)} 個測試住宿！**")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_accommodations()
