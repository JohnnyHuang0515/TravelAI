from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography

from ...domain.interfaces.place_repository import PlaceRepository
from ...infrastructure.persistence.orm_models import Place as OrmPlace, Hour as OrmHour

class PostgresPlaceRepository(PlaceRepository):
    """地點倉儲的 Postgres 實現"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def search(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: int = 5000, # 預設 5 公里
        categories: Optional[List[str]] = None,
        min_rating: Optional[float] = None
    ) -> List[OrmPlace]:
        """
        根據多個條件搜索地點。
        """
        query = self.db.query(OrmPlace)

        # 地理半徑搜索
        if lat is not None and lon is not None:
            # 將 point 轉換為 Geography 型別以使用公尺為單位進行計算
            point = func.ST_MakePoint(lon, lat)
            geography_point = func.ST_SetSRID(point, 4326).cast(Geography)
            query = query.filter(
                ST_DWithin(
                    OrmPlace.geom.cast(Geography),
                    geography_point,
                    radius
                )
            )

        # 類別過濾 (使用 PostgreSQL 的 && 操作符 - 交集)
        if categories and len(categories) > 0:
            # 使用 PostgreSQL 的 && 操作符來檢查陣列是否有交集
            query = query.filter(OrmPlace.categories.op('&&')(categories))

        # 最小評分過濾
        if min_rating is not None:
            query = query.filter(OrmPlace.rating >= min_rating)

        return query.limit(100).all() # 限制最多回傳 100 筆

    def search_by_vector(self, embedding: List[float], top_k: int = 50) -> List[OrmPlace]:
        """
        根據向量相似度搜索地點（暫時停用）
        """
        # 暫時移除向量搜尋功能
        return []
        # if not embedding:
        #     return []
        # 
        # # 使用 pgvector 的餘弦相似度搜尋
        # query = self.db.query(OrmPlace).filter(
        #     OrmPlace.embedding.isnot(None)
        # ).order_by(
        #     OrmPlace.embedding.cosine_distance(embedding)
        # ).limit(top_k)
        # 
        # return query.all()

    def get_hours_for_places(self, place_ids: List[str]) -> Dict[str, List[OrmHour]]:
        """
        從資料庫中獲取一批地點的營業時間。
        """
        if not place_ids:
            return {}
        
        hours_data = self.db.query(OrmHour).filter(OrmHour.place_id.in_(place_ids)).all()
        
        result = {pid: [] for pid in place_ids}
        for h in hours_data:
            result[str(h.place_id)].append(h)
            
        return result
