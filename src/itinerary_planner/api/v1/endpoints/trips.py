"""
行程管理 API 端點
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ....infrastructure.persistence.database import get_db
from ....application.services.trip_service import TripService
from ....infrastructure.persistence.orm_models import User
from ..schemas.trip import (
    SaveTripRequest,
    UpdateTripRequest,
    CopyTripRequest,
    TripSummaryResponse,
    TripDetailResponse,
    TripListResponse,
    ShareTripResponse,
    MessageResponse
)
from ..dependencies.auth import get_current_user


router = APIRouter(prefix="/trips", tags=["行程管理"])


def get_trip_service(db: Session = Depends(get_db)) -> TripService:
    """取得行程服務"""
    return TripService(db)


# ============================================================================
# 行程 CRUD
# ============================================================================

@router.post("", response_model=TripDetailResponse, status_code=status.HTTP_201_CREATED)
async def save_trip(
    request: SaveTripRequest,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    儲存新行程
    
    - **title**: 行程標題
    - **destination**: 目的地
    - **itinerary_data**: 完整的行程 JSON
    - **description**: 行程描述（可選）
    - **is_public**: 是否公開分享
    """
    trip = trip_service.save_trip(
        user_id=str(current_user.id),
        title=request.title,
        destination=request.destination,
        itinerary_data=request.itinerary_data,
        description=request.description,
        is_public=request.is_public
    )
    
    return TripDetailResponse.model_validate(trip)


@router.get("", response_model=TripListResponse)
async def get_my_trips(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(10, ge=1, le=50, description="每頁數量"),
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    取得我的行程列表（分頁）
    
    - **page**: 頁碼（從 1 開始）
    - **page_size**: 每頁數量（1-50）
    """
    result = trip_service.get_user_trips(
        user_id=str(current_user.id),
        page=page,
        page_size=page_size
    )
    
    return TripListResponse(
        trips=[TripSummaryResponse.model_validate(trip) for trip in result['trips']],
        total=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )


@router.get("/{trip_id}", response_model=TripDetailResponse)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    取得行程詳情
    
    只能查看自己的行程或公開的行程
    """
    try:
        trip = trip_service.get_trip(trip_id, str(current_user.id))
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限存取此行程"
        )
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或無權限查看"
        )
    
    return TripDetailResponse.model_validate(trip)


@router.put("/{trip_id}", response_model=TripDetailResponse)
async def update_trip(
    trip_id: str,
    request: UpdateTripRequest,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    更新行程
    
    只能更新自己的行程
    """
    # 只更新有提供的欄位
    update_data = request.model_dump(exclude_none=True)
    
    trip = trip_service.update_trip(
        trip_id=trip_id,
        user_id=str(current_user.id),
        **update_data
    )
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或無權限修改"
        )
    
    return TripDetailResponse.model_validate(trip)


@router.delete("/{trip_id}", response_model=MessageResponse)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    刪除行程
    
    只能刪除自己的行程
    """
    success = trip_service.delete_trip(
        trip_id=trip_id,
        user_id=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或無權限刪除"
        )
    
    return MessageResponse(message="行程已刪除")


# ============================================================================
# 行程分享與複製
# ============================================================================

@router.post("/{trip_id}/share", response_model=ShareTripResponse)
async def share_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    分享行程，生成公開連結
    
    只能分享自己的行程
    """
    share_token = trip_service.share_trip(
        trip_id=trip_id,
        user_id=str(current_user.id)
    )
    
    if not share_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或無權限分享"
        )
    
    # 建立分享連結（這裡使用相對路徑，實際應該是完整 URL）
    share_url = f"/trips/public/{share_token}"
    
    return ShareTripResponse(
        share_url=share_url,
        share_token=share_token
    )


@router.get("/public/{share_token}", response_model=TripDetailResponse)
async def get_public_trip(
    share_token: str,
    trip_service: TripService = Depends(get_trip_service)
):
    """
    查看公開分享的行程
    
    不需要登入
    """
    trip = trip_service.get_public_trip(share_token)
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享連結無效或行程不存在"
        )
    
    return TripDetailResponse.model_validate(trip)


@router.post("/{trip_id}/copy", response_model=TripDetailResponse)
async def copy_trip(
    trip_id: str,
    request: CopyTripRequest,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """
    複製行程到我的行程
    
    可以複製：
    - 自己的行程
    - 公開分享的行程
    """
    new_trip = trip_service.copy_trip(
        trip_id=trip_id,
        new_user_id=str(current_user.id),
        new_title=request.new_title
    )
    
    if not new_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或無法複製"
        )
    
    return TripDetailResponse.model_validate(new_trip)
