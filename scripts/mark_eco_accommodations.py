#!/usr/bin/env python3
"""
標記環保標章旅館 - 為有環保認證的住宿添加特殊標記
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation

def load_eco_hotels():
    """載入環保標章旅館資料"""
    
    eco_file = "/home/johnny/專案/比賽資料/docs/環保標章旅館環境即時通地圖資料.json"
    
    with open(eco_file, 'r', encoding='utf-8') as f:
        eco_hotels = json.load(f)
    
    # 只保留宜蘭地區的環保旅館
    yilan_eco_hotels = []
    for hotel in eco_hotels:
        if hotel.get("county") == "宜蘭縣":
            yilan_eco_hotels.append({
                "name": hotel.get("name", ""),
                "address": hotel.get("address", ""),
                "phone": hotel.get("phone", ""),
                "note": hotel.get("note", ""),  # 環保標章等級
                "lat": float(hotel.get("latitude", 0)),
                "lon": float(hotel.get("longitude", 0))
            })
    
    return yilan_eco_hotels

def update_eco_accommodations():
    """更新住宿資料，標記環保標章旅館"""
    
    print("🌱 **標記環保標章旅館**")
    print("=" * 50)
    
    # 載入環保標章旅館
    eco_hotels = load_eco_hotels()
    print(f"📊 找到 {len(eco_hotels)} 家宜蘭環保標章旅館")
    
    db = SessionLocal()
    try:
        updated_count = 0
        
        for eco_hotel in eco_hotels:
            eco_name = eco_hotel["name"]
            eco_level = eco_hotel["note"]  # 金級、銀級、銅級環保旅館
            
            # 在資料庫中尋找對應的住宿
            accommodations = db.query(Accommodation).filter(
                Accommodation.name.ilike(f"%{eco_name}%")
            ).all()
            
            if accommodations:
                for acc in accommodations:
                    # 更新環保標章資訊
                    if "環保" not in acc.amenities:
                        acc.amenities.append("環保標章")
                    
                    # 添加環保等級標記
                    eco_mark = f"🌱{eco_level}"
                    if eco_mark not in acc.amenities:
                        acc.amenities.append(eco_mark)
                    
                    # 更新評分（環保旅館加分）
                    if float(acc.rating) < 4.0:
                        acc.rating = min(4.5, float(acc.rating) + 0.3)
                    
                    updated_count += 1
                    print(f"  ✅ {acc.name} - {eco_level}")
            else:
                print(f"  ⚠️ 未找到對應住宿: {eco_name}")
        
        db.commit()
        print(f"\n✅ **更新完成**: {updated_count} 家環保標章旅館已標記")
        
    except Exception as e:
        print(f"❌ 更新錯誤: {e}")
        db.rollback()
    finally:
        db.close()
    
    return updated_count

def show_eco_accommodations():
    """顯示所有環保標章住宿"""
    
    print("\n🌱 **環保標章住宿清單**")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 查詢有環保標章的住宿
        from sqlalchemy import func
        eco_accommodations = db.query(Accommodation).filter(
            func.array_to_string(Accommodation.amenities, ',').contains('環保標章')
        ).all()
        
        print(f"📊 總計 {len(eco_accommodations)} 家環保標章住宿")
        
        for i, acc in enumerate(eco_accommodations, 1):
            eco_levels = [amenity for amenity in acc.amenities if "🌱" in amenity]
            eco_level = eco_levels[0] if eco_levels else "環保標章"
            
            print(f"  {i:2d}. {acc.name}")
            print(f"      類型: {acc.type}")
            print(f"      標章: {eco_level}")
            print(f"      評分: {acc.rating}")
            print(f"      地址: {acc.address}")
            print()
        
    finally:
        db.close()

def main():
    """主執行函數"""
    
    print("🚀 **環保標章旅館標記系統**")
    print("=" * 60)
    
    # 更新環保標章住宿
    updated_count = update_eco_accommodations()
    
    # 顯示環保標章住宿清單
    show_eco_accommodations()
    
    print(f"\n🎉 **處理完成！**")
    print(f"  🌱 環保標章旅館: {updated_count} 家已標記")

if __name__ == "__main__":
    main()
