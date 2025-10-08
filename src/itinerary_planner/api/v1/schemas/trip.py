"""
行程相關的 Pydantic Schemas
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date


# ============================================================================
# 請求 Schemas
# ============================================================================

class SaveTripRequest(BaseModel):
    """儲存行程請求"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    destination: str
    itinerary_data: dict
    is_public: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "title": "宜蘭兩日遊",
                "description": "美食與自然之旅",
                "destination": "宜蘭",
                "itinerary_data": {
                    "days": [
                        {
                            "day": 1,
                            "date": "2025-10-01",
                            "visits": []
                        }
                    ]
                },
                "is_public": False
            }
        }


class UpdateTripRequest(BaseModel):
    """更新行程請求"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    itinerary_data: Optional[dict] = None
    is_public: Optional[bool] = None


class CopyTripRequest(BaseModel):
    """複製行程請求"""
    new_title: Optional[str] = None


# ============================================================================
# 回應 Schemas
# ============================================================================

class TripSummaryResponse(BaseModel):
    """行程摘要回應（列表用）"""
    id: str
    title: str
    description: Optional[str]
    destination: str
    duration_days: int
    start_date: Optional[date]
    end_date: Optional[date]
    is_public: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "trip_001",
                "title": "宜蘭兩日遊",
                "description": "美食與自然之旅",
                "destination": "宜蘭",
                "duration_days": 2,
                "start_date": "2025-10-01",
                "end_date": "2025-10-02",
                "is_public": False,
                "view_count": 0,
                "created_at": "2025-09-30T10:00:00Z",
                "updated_at": "2025-09-30T10:00:00Z"
            }
        }
    }


class TripDetailResponse(BaseModel):
    """行程詳細回應"""
    id: str
    user_id: str
    title: str
    description: Optional[str]
    destination: str
    duration_days: int
    start_date: Optional[date]
    end_date: Optional[date]
    itinerary_data: dict
    is_public: bool
    share_token: Optional[str]
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class TripListResponse(BaseModel):
    """行程列表回應（分頁）"""
    trips: List[TripSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "trips": [],
                "total": 5,
                "page": 1,
                "page_size": 10,
                "total_pages": 1
            }
        }
    }


class ShareTripResponse(BaseModel):
    """分享行程回應"""
    share_url: str
    share_token: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "share_url": "https://app.com/trips/public/abc123...",
                "share_token": "abc123..."
            }
        }
    }


class MessageResponse(BaseModel):
    """通用訊息回應"""
    message: str
