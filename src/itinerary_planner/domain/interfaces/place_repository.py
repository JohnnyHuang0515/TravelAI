from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models.place import Place

class PlaceRepository(ABC):
    """地點倉儲介面"""
    
    @abstractmethod
    def search(
        self,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: int = 5000,
        categories: Optional[List[str]] = None,
        min_rating: Optional[float] = None
    ) -> List[Any]:
        """搜索地點"""
        pass
    
    @abstractmethod
    def search_by_vector(self, embedding: List[float], top_k: int = 50) -> List[Any]:
        """根據向量相似度搜索地點"""
        pass
    
    @abstractmethod
    def get_hours_for_places(self, place_ids: List[str]) -> Dict[str, List[Any]]:
        """獲取地點的營業時間"""
        pass