from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ....infrastructure.persistence.database import get_db
from ....infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
from ....domain.models.place import Place as DomainPlace

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search", response_model=List[DomainPlace])
def search_places(
    lat: Optional[float] = Query(None, description="緯度"),
    lon: Optional[float] = Query(None, description="經度"),
    radius: int = Query(5000, description="搜索半徑（公尺）"),
    categories: Optional[List[str]] = Query(None, description="類別（可多選）"),
    min_rating: Optional[float] = Query(None, description="最低評分"),
    db: Session = Depends(get_db)
):
    """
    搜索地點 API 端點。
    """
    try:
        logger.info(f"Search places request: lat={lat}, lon={lon}, radius={radius}, categories={categories}, min_rating={min_rating}")
        
        repo = PostgresPlaceRepository(db)
        places = repo.search(
            lat=lat,
            lon=lon,
            radius=radius,
            categories=categories,
            min_rating=min_rating
        )
        
        logger.info(f"Found {len(places)} places")
        
        # 轉換 ORM 模型為 Domain 模型
        domain_places = []
        for place in places:
            domain_place = DomainPlace(
                id=str(place.id),
                name=place.name,
                categories=place.categories or [],
                rating=float(place.rating) if place.rating else None,
                stay_minutes=place.stay_minutes
            )
            domain_places.append(domain_place)
        
        return domain_places
        
    except Exception as e:
        logger.error(f"Error in search_places: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索地點時發生錯誤: {str(e)}")
