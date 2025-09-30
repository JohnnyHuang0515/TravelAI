"""
行程管理服務
處理使用者行程的 CRUD、分享、複製等業務邏輯
"""

from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from ...infrastructure.repositories.trip_repository import TripRepository
from ...infrastructure.persistence.orm_models import UserTrip


class TripService:
    """行程管理服務"""
    
    def __init__(self, db: Session):
        self.db = db
        self.trip_repo = TripRepository(db)
    
    def save_trip(
        self,
        user_id: str,
        title: str,
        destination: str,
        itinerary_data: dict,
        description: str = None,
        is_public: bool = False
    ) -> UserTrip:
        """
        儲存行程
        
        Args:
            user_id: 使用者 ID
            title: 行程標題
            destination: 目的地
            itinerary_data: 完整的行程 JSON 資料
            description: 行程描述
            is_public: 是否公開
        
        Returns:
            UserTrip 物件
        """
        # 從 itinerary_data 提取資訊
        days = itinerary_data.get('days', [])
        duration_days = len(days)
        
        # 取得開始與結束日期
        start_date = None
        end_date = None
        if days:
            start_date = days[0].get('date')
            end_date = days[-1].get('date')
        
        # 建立行程
        trip = self.trip_repo.create_trip(
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
        
        return trip
    
    def get_user_trips(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict:
        """
        取得使用者的行程列表（分頁）
        
        Returns:
            {
                'trips': [...],
                'total': 100,
                'page': 1,
                'page_size': 10,
                'total_pages': 10
            }
        """
        skip = (page - 1) * page_size
        trips = self.trip_repo.get_user_trips(user_id, skip, page_size)
        total = self.trip_repo.count_user_trips(user_id)
        
        return {
            'trips': trips,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def get_trip(
        self,
        trip_id: str,
        user_id: str = None
    ) -> Optional[UserTrip]:
        """
        取得行程詳情
        
        Args:
            trip_id: 行程 ID
            user_id: 使用者 ID（可選，用於權限檢查）
        """
        trip = self.trip_repo.get_by_id(trip_id)
        
        if not trip:
            return None
        
        # 如果有提供 user_id，檢查是否為擁有者或公開行程
        if user_id:
            if str(trip.user_id) != user_id and not trip.is_public:
                return None
        else:
            # 未登入只能看公開行程
            if not trip.is_public:
                return None
        
        return trip
    
    def update_trip(
        self,
        trip_id: str,
        user_id: str,
        **updates
    ) -> Optional[UserTrip]:
        """
        更新行程
        
        Args:
            trip_id: 行程 ID
            user_id: 使用者 ID
            **updates: 要更新的欄位
        """
        trip = self.trip_repo.get_by_id(trip_id)
        
        # 檢查權限
        if not trip or str(trip.user_id) != user_id:
            return None
        
        return self.trip_repo.update_trip(trip_id, **updates)
    
    def delete_trip(
        self,
        trip_id: str,
        user_id: str
    ) -> bool:
        """
        刪除行程
        
        Args:
            trip_id: 行程 ID
            user_id: 使用者 ID
        """
        trip = self.trip_repo.get_by_id(trip_id)
        
        # 檢查權限
        if not trip or str(trip.user_id) != user_id:
            return False
        
        return self.trip_repo.delete_trip(trip_id)
    
    def share_trip(
        self,
        trip_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        分享行程，生成公開連結
        
        Returns:
            分享 Token，用於建立公開連結
        """
        trip = self.trip_repo.get_by_id(trip_id)
        
        # 檢查權限
        if not trip or str(trip.user_id) != user_id:
            return None
        
        # 如果已經有 share_token，直接返回
        if trip.share_token:
            return trip.share_token
        
        # 生成新的 share_token
        return self.trip_repo.generate_share_token(trip_id)
    
    def get_public_trip(
        self,
        share_token: str
    ) -> Optional[UserTrip]:
        """
        根據分享 Token 取得公開行程
        """
        trip = self.trip_repo.get_by_share_token(share_token)
        
        if trip:
            # 增加瀏覽次數
            self.trip_repo.increment_view_count(str(trip.id))
        
        return trip
    
    def copy_trip(
        self,
        trip_id: str,
        new_user_id: str,
        new_title: str = None
    ) -> Optional[UserTrip]:
        """
        複製行程
        
        Args:
            trip_id: 要複製的行程 ID
            new_user_id: 新擁有者的使用者 ID
            new_title: 新行程標題（可選）
        """
        # 取得原始行程（可以是公開行程）
        original_trip = self.trip_repo.get_by_id(trip_id)
        
        if not original_trip:
            return None
        
        # 檢查是否為公開行程或自己的行程
        if not original_trip.is_public and str(original_trip.user_id) != new_user_id:
            return None
        
        return self.trip_repo.copy_trip(trip_id, new_user_id, new_title)
