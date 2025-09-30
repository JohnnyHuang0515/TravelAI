from typing import List, Optional, Tuple
from ...domain.models.story import Story, AccommodationPreference
from ...domain.models.itinerary import Accommodation
from ...infrastructure.persistence.orm_models import Accommodation as OrmAccommodation
from ...infrastructure.persistence.database import SessionLocal
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography

class AccommodationPlanner:
    """住宿規劃服務"""
    
    def select_accommodation(
        self, 
        story: Story, 
        attraction_locations: List[Tuple[float, float]]
    ) -> Optional[Accommodation]:
        """
        根據故事偏好和景點位置選擇最佳住宿
        
        Args:
            story: 使用者故事，包含住宿偏好
            attraction_locations: 景點位置列表 [(lat, lon), ...]
        
        Returns:
            選擇的住宿或 None
        """
        if not story.accommodation:
            return None
        
        db = SessionLocal()
        try:
            # 構建查詢
            query = db.query(OrmAccommodation)
            
            # 根據住宿類型篩選
            if story.accommodation.type != "any":
                query = query.filter(OrmAccommodation.type == story.accommodation.type)
            
            # 根據預算篩選
            if story.accommodation.budget_range:
                min_budget, max_budget = story.accommodation.budget_range
                if min_budget:
                    query = query.filter(OrmAccommodation.price_range >= min_budget)
                if max_budget:
                    query = query.filter(OrmAccommodation.price_range <= max_budget)
            
            # 根據評分篩選（至少3.0分）
            query = query.filter(OrmAccommodation.rating >= 3.0)
            
            # 根據地理位置偏好篩選
            if story.accommodation.location_preference == "near_attractions" and attraction_locations:
                # 計算景點的中心點
                center_lat = sum(loc[0] for loc in attraction_locations) / len(attraction_locations)
                center_lon = sum(loc[1] for loc in attraction_locations) / len(attraction_locations)
                
                # 在景點中心10公里範圍內搜尋
                point = func.ST_MakePoint(center_lon, center_lat)
                geography_point = func.ST_SetSRID(point, 4326).cast(Geography)
                query = query.filter(
                    ST_DWithin(
                        OrmAccommodation.geom.cast(Geography),
                        geography_point,
                        10000  # 10公里
                    )
                )
            
            # 按評分排序
            query = query.order_by(OrmAccommodation.rating.desc())
            
            # 取第一個結果
            accommodation = query.first()
            
            if accommodation:
                return Accommodation(
                    place_id=str(accommodation.id),
                    name=accommodation.name,
                    check_in=accommodation.check_in_time.strftime("%H:%M"),
                    check_out=accommodation.check_out_time.strftime("%H:%M"),
                    nights=story.days - 1,  # 住宿天數 = 行程天數 - 1
                    type=accommodation.type
                )
            
            return None
            
        except Exception as e:
            print(f"住宿選擇錯誤: {e}")
            return None
        finally:
            db.close()
    
    def get_accommodation_location(self, accommodation_id: str) -> Optional[Tuple[float, float]]:
        """獲取住宿的座標位置"""
        db = SessionLocal()
        try:
            accommodation = db.query(OrmAccommodation).filter(
                OrmAccommodation.id == accommodation_id
            ).first()
            
            if accommodation and accommodation.geom:
                # 提取座標
                lat = db.query(func.ST_Y(accommodation.geom)).scalar()
                lon = db.query(func.ST_X(accommodation.geom)).scalar()
                return (lat, lon)
            
            return None
            
        except Exception as e:
            print(f"獲取住宿位置錯誤: {e}")
            return None
        finally:
            db.close()

# 建立單例
accommodation_planner = AccommodationPlanner()
