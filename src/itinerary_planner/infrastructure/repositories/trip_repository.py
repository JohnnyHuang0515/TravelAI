"""
行程 Repository
處理使用者行程相關的資料庫操作
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import secrets

from ..persistence.orm_models import UserTrip, TripDay, TripVisit


class TripRepository:
    """行程資料存取 Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_trip(
        self,
        user_id: str,
        title: str,
        destination: str,
        duration_days: int,
        start_date: str,
        end_date: str,
        itinerary_data: dict,
        description: str = None,
        is_public: bool = False
    ) -> UserTrip:
        """建立新行程"""
        trip = UserTrip(
            user_id=user_id,
            title=title,
            description=description,
            destination=destination,
            duration_days=duration_days,
            start_date=start_date,
            end_date=end_date,
            itinerary_data=itinerary_data,
            is_public=is_public
        )
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip
    
    def get_by_id(self, trip_id: str) -> Optional[UserTrip]:
        """根據 ID 取得行程"""
        return self.db.query(UserTrip).filter(UserTrip.id == trip_id).first()
    
    def get_user_trips(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[UserTrip]:
        """取得使用者的行程列表"""
        return self.db.query(UserTrip).filter(
            UserTrip.user_id == user_id
        ).order_by(
            desc(UserTrip.created_at)
        ).offset(skip).limit(limit).all()
    
    def count_user_trips(self, user_id: str) -> int:
        """計算使用者的行程數量"""
        return self.db.query(UserTrip).filter(
            UserTrip.user_id == user_id
        ).count()
    
    def update_trip(
        self,
        trip_id: str,
        **kwargs
    ) -> Optional[UserTrip]:
        """更新行程"""
        trip = self.get_by_id(trip_id)
        if not trip:
            return None
        
        for key, value in kwargs.items():
            if hasattr(trip, key) and value is not None:
                setattr(trip, key, value)
        
        trip.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(trip)
        return trip
    
    def delete_trip(self, trip_id: str) -> bool:
        """刪除行程"""
        trip = self.get_by_id(trip_id)
        if not trip:
            return False
        
        self.db.delete(trip)
        self.db.commit()
        return True
    
    def generate_share_token(self, trip_id: str) -> Optional[str]:
        """生成分享 Token"""
        trip = self.get_by_id(trip_id)
        if not trip:
            return None
        
        # 生成隨機 Token
        share_token = secrets.token_urlsafe(32)
        trip.share_token = share_token
        trip.is_public = True
        
        self.db.commit()
        return share_token
    
    def get_by_share_token(self, share_token: str) -> Optional[UserTrip]:
        """根據分享 Token 取得行程"""
        return self.db.query(UserTrip).filter(
            UserTrip.share_token == share_token,
            UserTrip.is_public == True
        ).first()
    
    def increment_view_count(self, trip_id: str):
        """增加瀏覽次數"""
        trip = self.get_by_id(trip_id)
        if trip:
            trip.view_count += 1
            self.db.commit()
    
    def copy_trip(
        self,
        trip_id: str,
        new_user_id: str,
        new_title: str = None
    ) -> Optional[UserTrip]:
        """複製行程"""
        original_trip = self.get_by_id(trip_id)
        if not original_trip:
            return None
        
        # 建立新行程
        new_trip = UserTrip(
            user_id=new_user_id,
            title=new_title or f"{original_trip.title} (副本)",
            description=original_trip.description,
            destination=original_trip.destination,
            duration_days=original_trip.duration_days,
            start_date=original_trip.start_date,
            end_date=original_trip.end_date,
            itinerary_data=original_trip.itinerary_data.copy(),
            is_public=False
        )
        
        self.db.add(new_trip)
        self.db.commit()
        self.db.refresh(new_trip)
        return new_trip


class PlaceFavoriteRepository:
    """景點收藏 Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_favorite(
        self,
        user_id: str,
        place_id: str,
        notes: str = None
    ):
        """加入收藏"""
        from ..persistence.orm_models import PlaceFavorite
        
        # 檢查是否已收藏
        existing = self.db.query(PlaceFavorite).filter(
            PlaceFavorite.user_id == user_id,
            PlaceFavorite.place_id == place_id
        ).first()
        
        if existing:
            return existing
        
        favorite = PlaceFavorite(
            user_id=user_id,
            place_id=place_id,
            notes=notes
        )
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite
    
    def remove_favorite(
        self,
        user_id: str,
        place_id: str
    ) -> bool:
        """取消收藏"""
        from ..persistence.orm_models import PlaceFavorite
        
        favorite = self.db.query(PlaceFavorite).filter(
            PlaceFavorite.user_id == user_id,
            PlaceFavorite.place_id == place_id
        ).first()
        
        if not favorite:
            return False
        
        self.db.delete(favorite)
        self.db.commit()
        return True
    
    def get_user_favorites(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        """取得使用者的收藏景點"""
        from ..persistence.orm_models import PlaceFavorite
        
        return self.db.query(PlaceFavorite).filter(
            PlaceFavorite.user_id == user_id
        ).order_by(
            desc(PlaceFavorite.created_at)
        ).offset(skip).limit(limit).all()
    
    def is_favorited(
        self,
        user_id: str,
        place_id: str
    ) -> bool:
        """檢查是否已收藏"""
        from ..persistence.orm_models import PlaceFavorite
        
        return self.db.query(PlaceFavorite).filter(
            PlaceFavorite.user_id == user_id,
            PlaceFavorite.place_id == place_id
        ).first() is not None
