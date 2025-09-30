#!/usr/bin/env python3
"""
匯入住宿資料到 accommodations 表
"""

import sys
import os
import json
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation
from geoalchemy2 import WKTElement

def import_accommodation_data():
    """匯入住宿資料"""
    
    db = SessionLocal()
    try:
        print("🏨 **匯入住宿資料**")
        print("=" * 50)
        
        # 檔案路徑
        eco_hotel_file = "/home/johnny/專案/比賽資料/docs/環保標章旅館環境即時通地圖資料.json"
        
        print(f"📂 讀取檔案: {eco_hotel_file}")
        
        with open(eco_hotel_file, 'r', encoding='utf-8') as f:
            eco_hotels = json.load(f)
        
        print(f"📊 原始資料: {len(eco_hotels)} 筆")
        
        imported_count = 0
        skipped_count = 0
        
        for item in eco_hotels:
            try:
                # 檢查是否有座標
                lat = item.get("latitude")
                lon = item.get("longitude")
                
                if not lat or not lon:
                    skipped_count += 1
                    continue
                
                lat_float = float(lat)
                lon_float = float(lon)
                
                # 檢查是否在宜蘭地區 (大致範圍)
                if not (24.4 <= lat_float <= 25.0 and 121.4 <= lon_float <= 122.0):
                    skipped_count += 1
                    continue
                
                # 檢查縣市是否為宜蘭
                county = item.get("county", "")
                if "宜蘭" not in county:
                    skipped_count += 1
                    continue
                
                # 創建住宿記錄
                accommodation = Accommodation(
                    id=uuid.uuid4(),
                    name=item.get("name", "N/A"),
                    geom=WKTElement(f"POINT({lon_float} {lat_float})", srid=4326),
                    type="hotel",  # 環保旅館都是飯店
                    price_range=3,  # 預設中檔
                    rating=4.0,  # 環保旅館評分較高
                    address=item.get("address", ""),
                    phone=item.get("phone", ""),
                    amenities=["環保認證", "WiFi"]  # 預設設施
                )
                
                db.add(accommodation)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"  ✅ 已處理 {imported_count} 筆...")
                
            except Exception as e:
                print(f"  ❌ 處理錯誤: {e}")
                skipped_count += 1
                continue
        
        # 提交資料
        db.commit()
        
        print(f"\n🎉 **匯入完成！**")
        print(f"  ✅ 成功匯入: {imported_count} 筆")
        print(f"  ❌ 跳過: {skipped_count} 筆")
        
        # 檢查總數
        total_count = db.query(Accommodation).count()
        print(f"  📊 資料庫總數: {total_count} 筆")
        
    except Exception as e:
        print(f"❌ 匯入錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_accommodation_data()
