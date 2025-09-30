#!/usr/bin/env python3
"""
檢查環保標章住宿標記結果
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Accommodation

def check_eco_accommodations():
    """檢查環保標章住宿"""
    
    print("🌱 **檢查環保標章住宿**")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 查詢所有住宿，檢查 amenities
        all_accommodations = db.query(Accommodation).all()
        
        eco_count = 0
        eco_accommodations = []
        
        for acc in all_accommodations:
            if acc.amenities and any("環保" in amenity for amenity in acc.amenities):
                eco_count += 1
                eco_accommodations.append(acc)
        
        print(f"📊 找到 {eco_count} 家環保標章住宿")
        
        for i, acc in enumerate(eco_accommodations, 1):
            eco_amenities = [amenity for amenity in acc.amenities if "環保" in amenity or "🌱" in amenity]
            
            print(f"  {i:2d}. {acc.name}")
            print(f"      類型: {acc.type}")
            print(f"      評分: {acc.rating}")
            print(f"      環保標記: {', '.join(eco_amenities)}")
            print(f"      地址: {acc.address}")
            print()
        
    finally:
        db.close()

def main():
    check_eco_accommodations()

if __name__ == "__main__":
    main()
