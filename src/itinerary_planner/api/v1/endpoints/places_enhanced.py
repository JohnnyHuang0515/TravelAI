"""
景點推薦增強 API
包含附近景點推薦、景點收藏功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from geoalchemy2.shape import to_shape

from ....infrastructure.persistence.database import get_db
from ....infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
from ....infrastructure.repositories.trip_repository import PlaceFavoriteRepository
from ....infrastructure.persistence.orm_models import User, Place
from ..dependencies.auth import get_current_user, get_current_user_optional
from ..schemas.auth import MessageResponse


router = APIRouter(prefix="/places", tags=["景點推薦"])


# ============================================================================
# 附近景點推薦
# ============================================================================

@router.get("/nearby")
async def get_nearby_places(
    lat: float = Query(..., description="緯度"),
    lon: float = Query(..., description="經度"),
    radius: int = Query(5000, ge=100, le=50000, description="搜索半徑（公尺，100-50000）"),
    categories: Optional[List[str]] = Query(None, description="類別篩選"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="最低評分"),
    limit: int = Query(20, ge=1, le=50, description="返回數量"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    取得附近景點推薦
    
    - **lat**: 當前位置緯度
    - **lon**: 當前位置經度
    - **radius**: 搜索半徑（公尺）
    - **categories**: 類別篩選（可選）
    - **min_rating**: 最低評分（可選）
    - **limit**: 返回數量
    
    會員登入後可看到收藏狀態
    """
    try:
        # 使用現有的 Repository
        place_repo = PostgresPlaceRepository(db)
        
        # 執行搜尋
        places = place_repo.search(
            lat=lat,
            lon=lon,
            radius=radius,
            categories=categories,
            min_rating=min_rating
        )
        
        # 限制返回數量
        places = places[:limit]
        
        # 如果是會員，查詢收藏狀態
        favorite_place_ids = set()
        if current_user:
            favorite_repo = PlaceFavoriteRepository(db)
            favorites = favorite_repo.get_user_favorites(str(current_user.id))
            favorite_place_ids = {str(fav.place_id) for fav in favorites}
        
        # 組合結果
        result = []
        for place in places:
            # 計算距離
            from math import radians, cos, sin, asin, sqrt
            
            point = to_shape(place.geom)
            place_lat = point.y
            place_lon = point.x
            
            # Haversine 公式計算距離
            lon1, lat1, lon2, lat2 = map(radians, [lon, lat, place_lon, place_lat])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance_km = 6371 * c
            distance_m = int(distance_km * 1000)
            
            place_data = {
                "id": str(place.id),
                "name": place.name,
                "distance_meters": distance_m,
                "distance_text": f"{distance_km:.1f} 公里" if distance_km >= 1 else f"{distance_m} 公尺",
                "categories": place.categories or [],
                "rating": float(place.rating) if place.rating else None,
                "stay_minutes": place.stay_minutes,
                "price_range": place.price_range,
                "location": {
                    "lat": place_lat,
                    "lon": place_lon
                },
                "is_favorite": str(place.id) in favorite_place_ids if current_user else False
            }
            
            result.append(place_data)
        
        # 按距離排序
        result.sort(key=lambda x: x['distance_meters'])
        
        return {
            "places": result,
            "total": len(result),
            "user_location": {
                "lat": lat,
                "lon": lon
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜尋附近景點時發生錯誤: {str(e)}"
        )


# ============================================================================
# 景點收藏
# ============================================================================

@router.get("/favorites")
async def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取得我的收藏景點
    """
    favorite_repo = PlaceFavoriteRepository(db)
    favorites = favorite_repo.get_user_favorites(str(current_user.id))
    
    # 取得景點詳細資訊
    result = []
    for favorite in favorites:
        place = db.query(Place).filter(Place.id == favorite.place_id).first()
        if place:
            point = to_shape(place.geom)
            result.append({
                "id": str(place.id),
                "name": place.name,
                "categories": place.categories or [],
                "rating": float(place.rating) if place.rating else None,
                "stay_minutes": place.stay_minutes,
                "price_range": place.price_range,
                "location": {
                    "lat": point.y,
                    "lon": point.x
                },
                "notes": favorite.notes,
                "favorited_at": favorite.created_at.isoformat()
            })
    
    return {
        "favorites": result,
        "total": len(result)
    }


@router.post("/{place_id}/favorite", response_model=MessageResponse)
async def add_favorite(
    place_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    收藏景點
    
    - **place_id**: 景點 ID
    - **notes**: 備註（可選）
    """
    # 檢查景點是否存在
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="景點不存在"
        )
    
    favorite_repo = PlaceFavoriteRepository(db)
    favorite_repo.add_favorite(
        user_id=str(current_user.id),
        place_id=place_id,
        notes=notes
    )
    
    return MessageResponse(message="已加入收藏")


@router.delete("/{place_id}/favorite", response_model=MessageResponse)
async def remove_favorite(
    place_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消收藏景點
    """
    favorite_repo = PlaceFavoriteRepository(db)
    success = favorite_repo.remove_favorite(
        user_id=str(current_user.id),
        place_id=place_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未收藏此景點"
        )
    
    return MessageResponse(message="已取消收藏")
