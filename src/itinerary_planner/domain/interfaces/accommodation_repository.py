from abc import ABC, abstractmethod
from typing import List, Optional
from ...infrastructure.persistence.orm_models import Accommodation as OrmAccommodation

class AccommodationRepository(ABC):
    """住宿倉儲介面"""
    
    @abstractmethod
    def search(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: int = 10000,
        accommodation_type: Optional[str] = None,
        min_rating: Optional[float] = None,
        budget_range: Optional[List[int]] = None,
        eco_friendly: bool = False
    ) -> List[OrmAccommodation]:
        """搜索住宿"""
        pass
    
    @abstractmethod
    def search_by_vector(self, embedding: List[float], top_k: int = 10) -> List[OrmAccommodation]:
        """根據向量相似度搜索住宿"""
        pass
    
    @abstractmethod
    def get_accommodation_by_id(self, accommodation_id: str) -> Optional[OrmAccommodation]:
        """根據 ID 獲取住宿"""
        pass

