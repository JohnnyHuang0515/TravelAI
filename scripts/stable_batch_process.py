#!/usr/bin/env python3
"""
穩定版住宿資料處理 - 使用預設座標和簡化策略
"""

import sys
import os
import json
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation
from geoalchemy2 import WKTElement

# 宜蘭各鄉鎮的預設座標
YILAN_DISTRICTS = {
    "宜蘭市": (24.7580, 121.7530),
    "羅東鎮": (24.6770, 121.7730),
    "蘇澳鎮": (24.5960, 121.8420),
    "頭城鎮": (24.8570, 121.8230),
    "礁溪鄉": (24.8270, 121.7730),
    "壯圍鄉": (24.7470, 121.7930),
    "員山鄉": (24.7470, 121.7230),
    "冬山鄉": (24.6370, 121.7930),
    "五結鄉": (24.6870, 121.8030),
    "三星鄉": (24.6670, 121.6630),
    "大同鄉": (24.5270, 121.6030),
    "南澳鄉": (24.4670, 121.8030)
}

def get_district_coordinates(address):
    """根據地址中的鄉鎮名稱取得座標"""
    
    for district, coords in YILAN_DISTRICTS.items():
        if district in address:
            return coords
    
    # 預設返回宜蘭市座標
    return YILAN_DISTRICTS["宜蘭市"]

def process_hotels_simple():
    """簡化版處理旅館資料"""
    
    print("🏨 **簡化版處理宜蘭縣旅館名冊**")
    print("=" * 50)
    
    hotel_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣旅館名冊.json"
    
    with open(hotel_file, 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    
    print(f"📊 原始資料: {len(hotels)} 筆")
    
    # 只處理前50筆
    hotels = hotels[:50]
    print(f"🔄 實際處理: {len(hotels)} 筆")
    
    db = SessionLocal()
    try:
        imported_count = 0
        
        for hotel in hotels:
            name = hotel.get("中文名稱", "").strip()
            address = hotel.get("營業地址", "").strip()
            phone = hotel.get("電話", "").strip()
            
            if not name or not address:
                continue
            
            # 檢查是否已存在
            existing = db.query(Accommodation).filter(
                Accommodation.name.ilike(f"%{name}%")
            ).first()
            
            if existing:
                continue
            
            # 使用預設座標
            lat, lon = get_district_coordinates(address)
            
            # 創建住宿記錄
            accommodation = Accommodation(
                id=uuid.uuid4(),
                name=name,
                geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                type="hotel",
                price_range=3,  # 預設中檔
                rating=3.5,  # 預設評分
                address=address,
                phone=phone,
                amenities=["WiFi", "停車場", "早餐"]  # 預設設施
            )
            
            db.add(accommodation)
            imported_count += 1
            
            print(f"  ✅ {name} - {address}")
        
        db.commit()
        print(f"\n✅ **旅館匯入完成**: {imported_count} 筆")
        
    except Exception as e:
        print(f"❌ 匯入錯誤: {e}")
        db.rollback()
    finally:
        db.close()
    
    return imported_count

def process_homestays_simple():
    """簡化版處理民宿資料"""
    
    print("\n🏡 **簡化版處理宜蘭縣民宿名冊**")
    print("=" * 50)
    
    homestay_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣民宿名冊.json"
    
    with open(homestay_file, 'r', encoding='utf-8') as f:
        homestays = json.load(f)
    
    print(f"📊 原始資料: {len(homestays)} 筆")
    
    # 只處理前30筆
    homestays = homestays[:30]
    print(f"🔄 實際處理: {len(homestays)} 筆")
    
    db = SessionLocal()
    try:
        imported_count = 0
        
        for homestay in homestays:
            name = homestay.get("中文名稱", "").strip()
            address = homestay.get("營業地址", "").strip()
            phone = homestay.get("電話", "").strip()
            
            if not name or not address:
                continue
            
            # 檢查是否已存在
            existing = db.query(Accommodation).filter(
                Accommodation.name.ilike(f"%{name}%")
            ).first()
            
            if existing:
                continue
            
            # 使用預設座標
            lat, lon = get_district_coordinates(address)
            
            # 創建住宿記錄
            accommodation = Accommodation(
                id=uuid.uuid4(),
                name=name,
                geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                type="homestay",
                price_range=2,  # 預設中低檔
                rating=3.8,  # 預設評分
                address=address,
                phone=phone,
                amenities=["WiFi", "廚房", "洗衣機"]  # 預設設施
            )
            
            db.add(accommodation)
            imported_count += 1
            
            print(f"  ✅ {name} - {address}")
        
        db.commit()
        print(f"\n✅ **民宿匯入完成**: {imported_count} 筆")
        
    except Exception as e:
        print(f"❌ 匯入錯誤: {e}")
        db.rollback()
    finally:
        db.close()
    
    return imported_count

def check_final_status():
    """檢查最終狀態"""
    
    db = SessionLocal()
    try:
        total_count = db.query(Accommodation).count()
        
        # 按類型統計
        from sqlalchemy import func
        type_stats = db.query(
            Accommodation.type,
            func.count(Accommodation.id).label('count')
        ).group_by(Accommodation.type).all()
        
        print(f"\n📊 **最終資料庫狀態**")
        print(f"  📈 總住宿數量: {total_count} 筆")
        
        for type_name, count in type_stats:
            print(f"  - {type_name}: {count} 筆")
        
    finally:
        db.close()

def main():
    """主執行函數"""
    
    print("🚀 **穩定版住宿資料處理**")
    print("=" * 60)
    print("💡 使用預設座標，避免API失敗")
    
    # 處理旅館
    hotel_count = process_hotels_simple()
    
    # 處理民宿
    homestay_count = process_homestays_simple()
    
    # 檢查最終狀態
    check_final_status()
    
    print(f"\n🎉 **處理完成！**")
    print(f"  🏨 新增旅館: {hotel_count} 筆")
    print(f"  🏡 新增民宿: {homestay_count} 筆")
    print(f"  📊 總計新增: {hotel_count + homestay_count} 筆")

if __name__ == "__main__":
    main()
