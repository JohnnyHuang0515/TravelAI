from pydantic import BaseModel
from typing import List, Optional

class Place(BaseModel):
    id: str
    name: str
    categories: List[str]
    rating: Optional[float] = None
    stay_minutes: int = 60
    
    class Config:
        from_attributes = True  # 允許從 ORM 模型轉換