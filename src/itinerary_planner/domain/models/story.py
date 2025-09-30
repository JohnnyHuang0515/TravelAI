from pydantic import BaseModel
from typing import List, Optional, Tuple
from datetime import time

class Preference(BaseModel):
    themes: List[str]

class AccommodationPreference(BaseModel):
    type: str  # 'hotel', 'hostel', 'homestay'
    budget_range: Optional[Tuple[int, int]] = None  # (min, max) 價格範圍
    location_preference: str = "any"  # 'city_center', 'near_attractions', 'any'

class TimeWindow(BaseModel):
    start: str  # "HH:MM"
    end: str    # "HH:MM"

class Story(BaseModel):
    days: int
    preference: Preference
    accommodation: Optional[AccommodationPreference] = None  # 新增住宿偏好
    daily_window: Optional[TimeWindow] = None
    date_range: Optional[List[str]] = None