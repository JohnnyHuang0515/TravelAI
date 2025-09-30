#!/usr/bin/env python3
"""
優化版批量處理住宿資料 - 減少API調用，提高成功率
"""

import sys
import os
import json
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.services.geocoding_service import geocoding_service
from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation
from geoalchemy2 import WKTElement

def process_hotel_data_optimized():
    """優化版處理宜蘭縣旅館名冊"""
    
    print("🏨 **優化版處理宜蘭縣旅館名冊**")
    print("=" * 50)
    
    # 讀取資料
    hotel_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣旅館名冊.json"
    
    with open(hotel_file, 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    
    print(f"📊 原始資料: {len(hotels)} 筆")
    
    # 去重地址並提取資訊
    unique_addresses = set()
    hotel_info = {}
    
    for hotel in hotels:
        name = hotel.get("中文名稱", "")
        address = hotel.get("營業地址", "")
        phone = hotel.get("電話", "")
        
        if name and address:
            # 清理地址，只保留到路名
            clean_address = address
            import re
            clean_address = re.sub(r'\d+[-\d]*號.*$', '', clean_address)
            clean_address = re.sub(r'\d+[-\d]*樓.*$', '', clean_address)
            clean_address = clean_address.strip()
            
            if clean_address not in unique_addresses:
                unique_addresses.add(clean_address)
                hotel_info[clean_address] = {
                    "name": name,
                    "phone": phone,
                    "type": "hotel",
                    "original_address": address
                }
    
    print(f"📍 去重後地址: {len(unique_addresses)} 筆")
    
    # 只處理前50筆避免API限制
    addresses_to_process = list(unique_addresses)[:50]
    print(f"🔄 實際處理: {len(addresses_to_process)} 筆")
    
    # 批量地址解析
    geocoded_results = geocoding_service.batch_geocode(addresses_to_process)
    
    # 匯入資料庫
    db = SessionLocal()
    try:
        imported_count = 0
        
        for address, (lat, lon) in geocoded_results.items():
            if address in hotel_info:
                info = hotel_info[address]
                
                # 檢查是否在宜蘭範圍
                if 24.4 <= lat <= 25.0 and 121.4 <= lon <= 122.0:
                    accommodation = Accommodation(
                        id=uuid.uuid4(),
                        name=info["name"],
                        geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                        type=info["type"],
                        price_range=3,  # 預設中檔
                        rating=3.5,  # 預設評分
                        address=info["original_address"],
                        phone=info["phone"],
                        amenities=["WiFi", "停車場"]  # 預設設施
                    )
                    
                    db.add(accommodation)
                    imported_count += 1
        
        db.commit()
        print(f"\n✅ **旅館匯入完成**: {imported_count} 筆")
        
    except Exception as e:
        print(f"❌ 匯入錯誤: {e}")
        db.rollback()
    finally:
        db.close()
    
    return imported_count

def check_current_progress():
    """檢查目前資料庫中的住宿數量"""
    
    db = SessionLocal()
    try:
        total_count = db.query(Accommodation).count()
        
        # 按類型統計
        from sqlalchemy import func
        type_stats = db.query(
            Accommodation.type,
            func.count(Accommodation.id).label('count')
        ).group_by(Accommodation.type).all()
        
        print(f"\n📊 **目前資料庫狀態**")
        print(f"  📈 總住宿數量: {total_count} 筆")
        
        for type_name, count in type_stats:
            print(f"  - {type_name}: {count} 筆")
        
    finally:
        db.close()

def main():
    """主執行函數"""
    
    print("🚀 **優化版批量處理住宿資料**")
    print("=" * 60)
    
    # 檢查目前狀態
    check_current_progress()
    
    # 處理旅館資料
    hotel_count = process_hotel_data_optimized()
    
    # 檢查最終狀態
    check_current_progress()
    
    print(f"\n🎉 **處理完成！**")
    print(f"  🏨 新增旅館: {hotel_count} 筆")

if __name__ == "__main__":
    main()
