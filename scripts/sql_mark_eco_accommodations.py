#!/usr/bin/env python3
"""
直接標記環保標章旅館 - 使用 SQL 更新
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation
from sqlalchemy import text

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
                "note": hotel.get("note", ""),  # 環保標章等級
            })
    
    return yilan_eco_hotels

def mark_eco_with_sql():
    """使用 SQL 直接標記環保旅館"""
    
    print("🌱 **使用 SQL 標記環保標章旅館**")
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
            
            print(f"\n🔍 處理: {eco_name} - {eco_level}")
            
            # 使用 SQL 直接更新
            sql = text("""
                UPDATE accommodations 
                SET amenities = amenities || ARRAY['環保標章', :eco_mark],
                    rating = LEAST(4.5, rating + 0.3)
                WHERE name ILIKE :name_pattern
            """)
            
            eco_mark = f"🌱{eco_level}"
            name_pattern = f"%{eco_name}%"
            
            result = db.execute(sql, {
                "eco_mark": eco_mark,
                "name_pattern": name_pattern
            })
            
            if result.rowcount > 0:
                print(f"  ✅ 成功更新 {result.rowcount} 筆記錄")
                updated_count += result.rowcount
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
        # 使用 SQL 查詢環保標章住宿
        sql = text("""
            SELECT name, type, rating, amenities, address
            FROM accommodations 
            WHERE amenities && ARRAY['環保標章']
            ORDER BY name
        """)
        
        result = db.execute(sql)
        eco_accommodations = result.fetchall()
        
        print(f"📊 驗證結果: {len(eco_accommodations)} 家環保標章住宿")
        
        for i, row in enumerate(eco_accommodations, 1):
            name, type_name, rating, amenities, address = row
            
            eco_amenities = [amenity for amenity in amenities if "環保" in amenity or "🌱" in amenity]
            
            print(f"  {i:2d}. {name}")
            print(f"      類型: {type_name}")
            print(f"      評分: {rating}")
            print(f"      環保標記: {', '.join(eco_amenities)}")
            print(f"      地址: {address}")
            print()
        
    finally:
        db.close()

def main():
    """主執行函數"""
    
    print("🚀 **環保標章旅館 SQL 標記系統**")
    print("=" * 60)
    
    # 標記環保標章住宿
    updated_count = mark_eco_with_sql()
    
    # 驗證標記結果
    verify_eco_marking()
    
    print(f"\n🎉 **處理完成！**")
    print(f"  🌱 環保標章旅館: {updated_count} 家已標記")

if __name__ == "__main__":
    main()
