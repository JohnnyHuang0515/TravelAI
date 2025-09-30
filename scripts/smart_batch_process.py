#!/usr/bin/env python3
"""
智能批量處理住宿資料 - 使用快取和去重策略
"""

import sys
import os
import json
import uuid
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.services.geocoding_service import geocoding_service
from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation
from geoalchemy2 import WKTElement

def load_existing_accommodations():
    """載入現有住宿資料，避免重複"""
    
    db = SessionLocal()
    try:
        existing = db.query(Accommodation.name, Accommodation.address).all()
        existing_set = set()
        for name, addr in existing:
            existing_set.add((name.lower().strip(), addr.lower().strip()))
        return existing_set
    finally:
        db.close()

def clean_and_deduplicate_addresses(data_list, data_type):
    """清理並去重地址"""
    
    unique_addresses = {}
    
    for item in data_list:
        name = item.get("中文名稱", "").strip()
        address = item.get("營業地址", "").strip()
        phone = item.get("電話", "").strip()
        
        if not name or not address:
            continue
            
        # 清理地址 - 移除門牌號碼
        import re
        clean_address = re.sub(r'\d+[-\d]*號.*$', '', address)
        clean_address = re.sub(r'\d+[-\d]*樓.*$', '', clean_address)
        clean_address = clean_address.strip()
        
        # 確保包含宜蘭
        if "宜蘭" not in clean_address:
            clean_address = f"宜蘭縣{clean_address}"
        
        # 使用清理後的地址作為key
        if clean_address not in unique_addresses:
            unique_addresses[clean_address] = {
                "name": name,
                "phone": phone,
                "type": data_type,
                "original_address": address
            }
    
    return unique_addresses

def batch_geocode_with_cache(addresses, cache_file="geocoding_cache.json"):
    """帶快取的批量地址解析"""
    
    # 載入快取
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except:
            cache = {}
    
    # 檢查哪些地址需要解析
    to_geocode = []
    results = {}
    
    for addr in addresses:
        if addr in cache:
            results[addr] = cache[addr]
        else:
            to_geocode.append(addr)
    
    print(f"📋 快取命中: {len(results)} 筆")
    print(f"🔄 需要解析: {len(to_geocode)} 筆")
    
    if to_geocode:
        # 分批處理，避免API限制
        batch_size = 20
        for i in range(0, len(to_geocode), batch_size):
            batch = to_geocode[i:i+batch_size]
            print(f"  🔄 處理批次 {i//batch_size + 1}: {len(batch)} 筆")
            
            batch_results = geocoding_service.batch_geocode(batch)
            
            # 更新快取和結果
            for addr, coords in batch_results.items():
                cache[addr] = coords
                results[addr] = coords
            
            # 儲存快取
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            
            # 避免API限制
            if i + batch_size < len(to_geocode):
                time.sleep(2)
    
    return results

def import_accommodations(accommodation_data, geocoded_results):
    """匯入住宿資料到資料庫"""
    
    db = SessionLocal()
    try:
        imported_count = 0
        skipped_count = 0
        
        for address, (lat, lon) in geocoded_results.items():
            if address not in accommodation_data:
                continue
                
            info = accommodation_data[address]
            
            # 檢查座標是否在宜蘭範圍
            if not (24.4 <= lat <= 25.0 and 121.4 <= lon <= 122.0):
                skipped_count += 1
                continue
            
            # 檢查是否已存在
            existing = db.query(Accommodation).filter(
                Accommodation.name.ilike(f"%{info['name']}%")
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # 創建新記錄
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
        
        print(f"✅ 成功匯入: {imported_count} 筆")
        print(f"⏭️ 跳過重複: {skipped_count} 筆")
        
        return imported_count
        
    except Exception as e:
        print(f"❌ 匯入錯誤: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def process_hotels():
    """處理旅館資料"""
    
    print("🏨 **處理宜蘭縣旅館名冊**")
    print("=" * 50)
    
    hotel_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣旅館名冊.json"
    
    with open(hotel_file, 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    
    print(f"📊 原始資料: {len(hotels)} 筆")
    
    # 清理並去重
    hotel_data = clean_and_deduplicate_addresses(hotels, "hotel")
    print(f"📍 去重後: {len(hotel_data)} 筆")
    
    # 地址解析
    addresses = list(hotel_data.keys())
    geocoded_results = batch_geocode_with_cache(addresses)
    
    # 匯入資料庫
    imported = import_accommodations(hotel_data, geocoded_results)
    
    return imported

def process_homestays():
    """處理民宿資料"""
    
    print("\n🏡 **處理宜蘭縣民宿名冊**")
    print("=" * 50)
    
    homestay_file = "/home/johnny/專案/比賽資料/docs/宜蘭縣民宿名冊.json"
    
    with open(homestay_file, 'r', encoding='utf-8') as f:
        homestays = json.load(f)
    
    print(f"📊 原始資料: {len(homestays)} 筆")
    
    # 只處理前100筆避免API限制
    homestays = homestays[:100]
    print(f"🔄 實際處理: {len(homestays)} 筆")
    
    # 清理並去重
    homestay_data = clean_and_deduplicate_addresses(homestays, "homestay")
    print(f"📍 去重後: {len(homestay_data)} 筆")
    
    # 地址解析
    addresses = list(homestay_data.keys())
    geocoded_results = batch_geocode_with_cache(addresses)
    
    # 匯入資料庫
    imported = import_accommodations(homestay_data, geocoded_results)
    
    return imported

def main():
    """主執行函數"""
    
    print("🚀 **智能批量處理住宿資料**")
    print("=" * 60)
    
    # 載入現有資料
    existing = load_existing_accommodations()
    print(f"📋 現有住宿: {len(existing)} 筆")
    
    # 處理旅館
    hotel_count = process_hotels()
    
    # 處理民宿
    homestay_count = process_homestays()
    
    print(f"\n🎉 **處理完成！**")
    print(f"  🏨 新增旅館: {hotel_count} 筆")
    print(f"  🏡 新增民宿: {homestay_count} 筆")
    print(f"  📊 總計新增: {hotel_count + homestay_count} 筆")

if __name__ == "__main__":
    main()
