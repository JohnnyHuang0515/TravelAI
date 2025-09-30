from pydantic import BaseModel
from typing import List, Optional

class Visit(BaseModel):
    place_id: str
    name: str
    eta: str  # "HH:MM"
    etd: str  # "HH:MM"
    travel_minutes: int
    
    class Config:
        from_attributes = True

class Accommodation(BaseModel):
    place_id: str
    name: str
    check_in: str  # "HH:MM"
    check_out: str  # "HH:MM"
    nights: int
    type: str  # 'hotel', 'hostel', 'homestay'
    
    class Config:
        from_attributes = True

class Day(BaseModel):
    date: str # "YYYY-MM-DD"
    visits: List[Visit]
    accommodation: Optional[Accommodation] = None  # 新增住宿資訊
    
    class Config:
        from_attributes = True

class Itinerary(BaseModel):
    days: List[Day]
    
    class Config:
        from_attributes = True
