from typing import List, Dict
from ...infrastructure.persistence.orm_models import Place
from ...domain.models.story import Story

class RerankService:
    """重排序服務，用於融合結構化和語義化檢索結果"""
    
    def rerank(self, structured_results: List[Place], semantic_results: List[Place], story: Story) -> List[Place]:
        """
        融合並重排序候選地點，考慮多個因素
        """
        # 計算每個地點的綜合評分
        scored_places = {}
        
        # 處理結構化結果
        for i, place in enumerate(structured_results):
            score = self._calculate_score(place, story, is_structured=True, rank=i)
            scored_places[str(place.id)] = (place, score)
        
        # 處理語義化結果
        for i, place in enumerate(semantic_results):
            place_id = str(place.id)
            if place_id in scored_places:
                # 如果已存在，取較高分數
                _, existing_score = scored_places[place_id]
                semantic_score = self._calculate_score(place, story, is_structured=False, rank=i)
                scored_places[place_id] = (place, max(existing_score, semantic_score))
            else:
                score = self._calculate_score(place, story, is_structured=False, rank=i)
                scored_places[place_id] = (place, score)
        
        # 按分數排序
        sorted_places = sorted(scored_places.values(), key=lambda x: x[1], reverse=True)
        
        # 返回前50個候選
        return [place for place, score in sorted_places[:50]]
    
    def _calculate_score(self, place: Place, story: Story, is_structured: bool, rank: int) -> float:
        """
        計算地點的綜合評分
        """
        score = 0.0
        
        # 基礎分數
        if is_structured:
            score += 10.0  # 結構化結果基礎分數
        else:
            score += 5.0   # 語義化結果基礎分數
        
        # 排名懲罰（排名越靠後分數越低）
        score -= rank * 0.1
        
        # 評分加成
        if place.rating:
            score += float(place.rating) * 2.0
        
        # 環保主題優先級提升
        eco_boost = self._calculate_eco_boost(place, story)
        score += eco_boost
        
        # 主題匹配加成
        if story.preference.themes:
            theme_match = self._calculate_theme_match(place, story.preference.themes)
            score += theme_match * 5.0
        
        # 特殊需求匹配
        if hasattr(story, 'special_requirements') and story.special_requirements:
            special_match = self._calculate_special_match(place, story.special_requirements)
            score += special_match * 3.0
        
        return score
    
    def _calculate_eco_boost(self, place: Place, story: Story) -> float:
        """
        計算環保主題優先級提升分數
        """
        eco_boost = 0.0
        
        # 檢查是否為環保相關需求
        is_eco_request = False
        
        # 檢查主題中的環保關鍵詞
        eco_themes = ['環保', '生態', '永續', '綠色', '環境教育', '自然']
        if story.preference.themes:
            for theme in story.preference.themes:
                if any(eco_keyword in theme for eco_keyword in eco_themes):
                    is_eco_request = True
                    break
        
        # 檢查特殊需求中的環保關鍵詞
        eco_keywords = ['環保', '生態', '永續', '綠色', '環境教育', '自然', '有機', '保護區']
        if hasattr(story, 'special_requirements') and story.special_requirements:
            special_req_str = str(story.special_requirements)
            if any(eco_keyword in special_req_str for eco_keyword in eco_keywords):
                is_eco_request = True
                print(f"🌱 檢測到環保需求: {special_req_str}")
        
        # 如果用戶要求環保行程，給予環保景點大幅加分
        if is_eco_request:
            # 檢查景點是否為環保教育設施
            if place.categories and '環保教育' in place.categories:
                eco_boost += 20.0  # 環保教育設施大幅加分
                print(f"🌱 環保教育設施加分: {place.name} (+20.0)")
            
            # 檢查景點標籤中的環保關鍵詞
            if place.tags:
                eco_tag_count = 0
                for tag in place.tags:
                    if any(eco_keyword in tag for eco_keyword in eco_keywords):
                        eco_tag_count += 1
                
                if eco_tag_count > 0:
                    eco_boost += eco_tag_count * 5.0  # 每個環保標籤加5分
                    print(f"🌱 環保標籤加分: {place.name} (+{eco_tag_count * 5.0})")
            
            # 檢查景點名稱中的環保關鍵詞
            place_name_lower = place.name.lower()
            name_eco_count = sum(1 for keyword in eco_keywords if keyword in place_name_lower)
            if name_eco_count > 0:
                eco_boost += name_eco_count * 3.0  # 名稱中的環保關鍵詞加3分
                print(f"🌱 名稱環保關鍵詞加分: {place.name} (+{name_eco_count * 3.0})")
        
        return eco_boost
    
    def _calculate_theme_match(self, place: Place, themes: List[str]) -> float:
        """
        計算主題匹配度
        """
        if not place.categories:
            return 0.0
        
        match_count = 0
        for theme in themes:
            if theme in place.categories:
                match_count += 1
        
        return match_count / len(themes) if themes else 0.0
    
    def _calculate_special_match(self, place: Place, special_requirements: str) -> float:
        """
        計算特殊需求匹配度
        """
        if not place.tags:
            return 0.0
        
        match_keywords = []
        if "攝影" in special_requirements:
            match_keywords.extend(["攝影", "風景", "觀景", "拍照"])
        if "深度旅遊" in special_requirements:
            match_keywords.extend(["深度", "文化", "歷史", "體驗"])
        
        # 大幅擴展環保相關關鍵詞
        eco_requirements = ["環保", "生態", "永續", "綠色", "環境教育", "自然", "有機", "保護區", "教育設施", "生態園區", "博物館", "園區", "中心"]
        if any(eco_req in special_requirements for eco_req in eco_requirements):
            match_keywords.extend([
                "環保", "綠色", "永續", "生態", "環境", "自然", "有機", "保護區", 
                "教育", "設施", "園區", "博物館", "中心", "學習", "導覽", "體驗",
                "森林", "濕地", "農場", "植物", "動物", "水源", "回收", "節能"
            ])
        
        match_count = 0
        for keyword in match_keywords:
            if any(keyword in tag for tag in place.tags):
                match_count += 1
        
        return match_count / len(match_keywords) if match_keywords else 0.0

# 建立單例
rerank_service = RerankService()