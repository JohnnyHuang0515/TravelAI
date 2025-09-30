#!/usr/bin/env python3
"""
重新標記環保標章旅館 - 確保標記成功保存
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

def mark_eco_accommodations():
    """標記環保標章旅館"""
    
    print("🌱 **重新標記環保標章旅館**")
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
            
            print(f"\n🔍 搜尋: {eco_name}")
            
            # 在資料庫中尋找對應的住宿
            accommodations = db.query(Accommodation).filter(
                Accommodation.name.ilike(f"%{eco_name}%")
            ).all()
            
            if accommodations:
                for acc in accommodations:
                    print(f"  ✅ 找到: {acc.name}")
                    
                    # 確保 amenities 是列表
                    if not acc.amenities:
                        acc.amenities = []
                    
                    # 添加環保標章
                    if "環保標章" not in acc.amenities:
                        acc.amenities.append("環保標章")
                    
                    # 添加環保等級標記
                    eco_mark = f"🌱{eco_level}"
                    if eco_mark not in acc.amenities:
                        acc.amenities.append(eco_mark)
                    
                    # 更新評分（環保旅館加分）
                    current_rating = float(acc.rating)
                    if current_rating < 4.0:
                        new_rating = min(4.5, current_rating + 0.3)
                        acc.rating = new_rating
                        print(f"     評分提升: {current_rating} → {new_rating}")
                    
                    print(f"     環保標記: {eco_mark}")
                    updated_count += 1
            else:
                print(f"  ⚠️ 未找到對應住宿")
        
        # 提交變更
        db.commit()
        print(f"\n✅ **更新完成**: {updated_count} 家環保標章旅館已標記")
        
    except Exception as e:
        print(f"❌ 更新錯誤: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    return updated_count

def verify_eco_marking():
    """驗證環保標記結果"""
    
    print("\n🌱 **驗證環保標記結果**")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 查詢所有住宿
        all_accommodations = db.query(Accommodation).all()
        
        eco_count = 0
        eco_accommodations = []
        
        for acc in all_accommodations:
            if acc.amenities and any("環保" in str(amenity) for amenity in acc.amenities):
                eco_count += 1
                eco_accommodations.append(acc)
        
        print(f"📊 驗證結果: {eco_count} 家環保標章住宿")
        
        for i, acc in enumerate(eco_accommodations, 1):
            eco_amenities = [amenity for amenity in acc.amenities if "環保" in str(amenity) or "🌱" in str(amenity)]
            
            print(f"  {i:2d}. {acc.name}")
            print(f"      類型: {acc.type}")
            print(f"      評分: {acc.rating}")
            print(f"      環保標記: {', '.join(eco_amenities)}")
            print(f"      地址: {acc.address}")
            print()
        
    finally:
        db.close()

def main():
    """主執行函數"""
    
    print("🚀 **環保標章旅館重新標記系統**")
    print("=" * 60)
    
    # 標記環保標章住宿
    updated_count = mark_eco_accommodations()
    
    # 驗證標記結果
    verify_eco_marking()
    
    print(f"\n🎉 **處理完成！**")
    print(f"  🌱 環保標章旅館: {updated_count} 家已標記")

if __name__ == "__main__":
    main()
