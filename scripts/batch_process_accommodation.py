#!/usr/bin/env python3
"""
批量處理住宿資料 - 地址解析並匯入資料庫
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

def process_hotel_data():
    """處理宜蘭縣旅館名冊"""
    
    print("🏨 **處理宜蘭縣旅館名冊**")
    print("=" * 50)
    
    # 讀取資料
    hotel_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣旅館名冊.json"
    
    with open(hotel_file, 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    
    print(f"📊 原始資料: {len(hotels)} 筆")
    
    # 提取地址
    addresses = []
    hotel_info = {}
    
    for hotel in hotels:
        name = hotel.get("中文名稱", "")
        address = hotel.get("營業地址", "")
        phone = hotel.get("電話", "")
        
        if name and address:
            addresses.append(address)
            hotel_info[address] = {
                "name": name,
                "phone": phone,
                "type": "hotel"
            }
    
    print(f"📍 需要解析的地址: {len(addresses)} 筆")
    
    # 批量地址解析
    geocoded_results = geocoding_service.batch_geocode(addresses)
    
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
                        address=address,
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

def process_homestay_data():
    """處理宜蘭縣民宿名冊"""
    
    print("\n🏠 **處理宜蘭縣民宿名冊**")
    print("=" * 50)
    
    # 讀取資料
    homestay_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣民宿名冊.json"
    
    with open(homestay_file, 'r', encoding='utf-8') as f:
        homestays = json.load(f)
    
    print(f"📊 原始資料: {len(homestays)} 筆")
    
    # 提取地址 (只處理前100筆避免API限制)
    addresses = []
    homestay_info = {}
    
    for i, homestay in enumerate(homestays[:100]):  # 限制100筆
        name = homestay.get("中文名稱", "")
        address = homestay.get("營業地址", "")
        phone = homestay.get("電話", "")
        
        if name and address:
            addresses.append(address)
            homestay_info[address] = {
                "name": name,
                "phone": phone,
                "type": "homestay"
            }
    
    print(f"📍 需要解析的地址: {len(addresses)} 筆 (限制100筆)")
    
    # 批量地址解析
    geocoded_results = geocoding_service.batch_geocode(addresses)
    
    # 匯入資料庫
    db = SessionLocal()
    try:
        imported_count = 0
        
        for address, (lat, lon) in geocoded_results.items():
            if address in homestay_info:
                info = homestay_info[address]
                
                # 檢查是否在宜蘭範圍
                if 24.4 <= lat <= 25.0 and 121.4 <= lon <= 122.0:
                    accommodation = Accommodation(
                        id=uuid.uuid4(),
                        name=info["name"],
                        geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                        type=info["type"],
                        price_range=2,  # 民宿通常較便宜
                        rating=3.5,  # 預設評分
                        address=address,
                        phone=info["phone"],
                        amenities=["WiFi"]  # 預設設施
                    )
                    
                    db.add(accommodation)
                    imported_count += 1
        
        db.commit()
        print(f"\n✅ **民宿匯入完成**: {imported_count} 筆")
        
    except Exception as e:
        print(f"❌ 匯入錯誤: {e}")
        db.rollback()
    finally:
        db.close()
    
    return imported_count

def main():
    """主執行函數"""
    
    print("🚀 **開始批量處理住宿資料**")
    print("=" * 60)
    
    # 處理旅館資料
    hotel_count = process_hotel_data()
    
    # 處理民宿資料
    homestay_count = process_homestay_data()
    
    # 檢查總數
    db = SessionLocal()
    try:
        total_count = db.query(Accommodation).count()
        print(f"\n🎉 **處理完成！**")
        print(f"  🏨 新增旅館: {hotel_count} 筆")
        print(f"  🏠 新增民宿: {homestay_count} 筆")
        print(f"  📊 資料庫總數: {total_count} 筆")
    finally:
        db.close()

if __name__ == "__main__":
    main()
