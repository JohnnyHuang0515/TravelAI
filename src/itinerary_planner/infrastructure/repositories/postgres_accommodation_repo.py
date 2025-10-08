from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography

from ...domain.interfaces.accommodation_repository import AccommodationRepository
from ...infrastructure.persistence.orm_models import Accommodation as OrmAccommodation

class PostgresAccommodationRepository(AccommodationRepository):
    """住宿倉儲的 Postgres 實現"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def search(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: int = 10000,  # 預設 10 公里
        accommodation_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        budget_range: Optional[List[int]] = None,
        eco_friendly: bool = False
    ) -> List[OrmAccommodation]:
        """
        根據多個條件搜索住宿
        """
        query = self.db.query(OrmAccommodation)
        
        # 地理半徑搜索
        if lat is not None and lon is not None:
            point = func.ST_MakePoint(lon, lat)
            geography_point = func.ST_SetSRID(point, 4326).cast(Geography)
            query = query.filter(
                ST_DWithin(
                    OrmAccommodation.geom.cast(Geography),
                    geography_point,
                    radius
                )
            )
        
        # 住宿類型過濾
        if accommodation_type:
            query = query.filter(OrmAccommodation.type == accommodation_type)
        
        # 最小評分過濾
        if min_rating is not None:
            query = query.filter(OrmAccommodation.rating >= min_rating)
        
        # 預算範圍過濾
        if budget_range and len(budget_range) == 2:
            min_budget, max_budget = budget_range
            # 假設 price_range 是每晚價格（台幣）
            query = query.filter(
                and_(
                    OrmAccommodation.price_range >= min_budget,
                    OrmAccommodation.price_range <= max_budget
                )
            )
        
        # 環保旅館過濾
        if eco_friendly:
            # 假設 amenities 包含環保相關標籤
            query = query.filter(
                OrmAccommodation.amenities.op('&&')(['eco_friendly', 'green_hotel', 'sustainable'])
            )
        
        return query.limit(20).all()  # 限制最多回傳 20 筆
    
    def search_by_vector(self, embedding: List[float], top_k: int = 10) -> List[OrmAccommodation]:
        """
        根據向量相似度搜索住宿
        """
        if not embedding:
            return []
        
        # 使用 pgvector 的餘弦相似度搜尋
        query = self.db.query(OrmAccommodation).filter(
            OrmAccommodation.embedding.isnot(None)
        ).order_by(
            OrmAccommodation.embedding.cosine_distance(embedding)
        ).limit(top_k)
        
        return query.all()
    
    def get_accommodation_by_id(self, accommodation_id: str) -> Optional[OrmAccommodation]:
        """
        根據 ID 獲取住宿
        """
        return self.db.query(OrmAccommodation).filter(
            OrmAccommodation.id == accommodation_id
        ).first()

