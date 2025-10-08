from typing import List, Optional
from ...infrastructure.persistence.orm_models import Accommodation as OrmAccommodation
from ...domain.models.story import Story
from ...domain.models.itinerary import Day, Accommodation as DomainAccommodation
import random

class AccommodationRecommendationService:
    """住宿推薦服務"""
    
    def recommend_accommodations_for_days(
        self, 
        days: List[Day], 
        accommodation_candidates: List[OrmAccommodation],
        story: Story
    ) -> List[Day]:
        """
        為每天的行程推薦住宿
        """
        if not accommodation_candidates:
            print("⚠️ 沒有住宿候選，跳過住宿推薦")
            return days
        
        # 為除了最後一天外的每一天推薦住宿
        for i, day in enumerate(days[:-1]):  # 最後一天不需要住宿
            if not day.accommodation:  # 如果還沒有住宿
                recommended_accommodation = self._select_best_accommodation(
                    accommodation_candidates, 
                    story,
                    day_index=i
                )
                
                if recommended_accommodation:
                    # 轉換為領域模型
                    domain_accommodation = DomainAccommodation(
                        place_id=str(recommended_accommodation.id),
                        name=recommended_accommodation.name,
                        type=recommended_accommodation.type,
                        check_in="15:00",  # 預設入住時間
                        check_out="11:00",  # 預設退房時間
                        nights=1
                    )
                    day.accommodation = domain_accommodation
                    print(f"🏨 第{i+1}天推薦住宿: {recommended_accommodation.name} (評分: {recommended_accommodation.rating})")
        
        return days
    
    def _select_best_accommodation(
        self, 
        candidates: List[OrmAccommodation], 
        story: Story,
        day_index: int
    ) -> Optional[OrmAccommodation]:
        """
        選擇最適合的住宿
        """
        if not candidates:
            return None
        
        # 簡單的選擇策略：優先選擇評分高的
        # 在實際應用中，可以考慮更多因素如地理位置、預算等
        
        # 過濾符合預算的住宿
        filtered_candidates = candidates
        if story.accommodation.budget_range:
            min_budget, max_budget = story.accommodation.budget_range
            filtered_candidates = [
                acc for acc in candidates 
                if acc.price_range and min_budget <= acc.price_range <= max_budget
            ]
        
        if not filtered_candidates:
            filtered_candidates = candidates  # 如果沒有符合預算的，使用所有候選
        
        # 按評分排序
        sorted_candidates = sorted(
            filtered_candidates, 
            key=lambda x: float(x.rating) if x.rating else 0, 
            reverse=True
        )
        
        # 隨機選擇前3個中的一個，增加多樣性
        top_candidates = sorted_candidates[:3]
        return random.choice(top_candidates) if top_candidates else None

# 建立單例
accommodation_recommendation_service = AccommodationRecommendationService()

