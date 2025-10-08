"""
重排序服務單元測試
"""
import pytest
from unittest.mock import Mock

from src.itinerary_planner.application.services.rerank_service import RerankService
from src.itinerary_planner.domain.models.story import Story, Preference
from tests.test_orm_models import Place


class TestRerankService:
    """重排序服務測試類別"""
    
    @pytest.fixture
    def rerank_service(self):
        """建立重排序服務實例"""
        return RerankService()
    
    @pytest.fixture
    def sample_story(self):
        """測試用的故事"""
        preference = Preference(
            themes=["文化", "歷史"],
            travel_pace="moderate",
            budget_level="medium"
        )
        return Story(
            days=3,
            preference=preference,
            accommodation=None
        )
    
    @pytest.fixture
    def sample_places(self):
        """測試用的地點列表"""
        place1 = Mock(spec=Place)
        place1.id = "place1"
        place1.name = "台北101"
        place1.rating = 4.5
        place1.categories = ["觀光", "文化"]
        place1.price_level = 2
        
        place2 = Mock(spec=Place)
        place2.id = "place2"
        place2.name = "故宮博物院"
        place2.rating = 4.8
        place2.categories = ["博物館", "歷史"]
        place2.price_level = 1
        
        place3 = Mock(spec=Place)
        place3.id = "place3"
        place3.name = "夜市"
        place3.rating = 4.2
        place3.categories = ["美食", "購物"]
        place3.price_level = 1
        
        return [place1, place2, place3]
    
    def test_rerank_structured_only(self, rerank_service, sample_story, sample_places):
        """測試只有結構化結果的重排序"""
        # 執行測試
        result = rerank_service.rerank(sample_places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 3
        assert result[0].id == "place2"  # 第一個結果（評分最高）
        assert result[1].id == "place1"  # 第二個結果
        assert result[2].id == "place3"  # 第三個結果
    
    def test_rerank_semantic_only(self, rerank_service, sample_story, sample_places):
        """測試只有語義化結果的重排序"""
        # 執行測試
        result = rerank_service.rerank([], sample_places, sample_story)
        
        # 驗證結果
        assert len(result) == 3
        assert result[0].id == "place2"  # 第一個結果（評分最高）
        assert result[1].id == "place1"  # 第二個結果
        assert result[2].id == "place3"  # 第三個結果
    
    def test_rerank_combined_results(self, rerank_service, sample_story, sample_places):
        """測試合併結構化和語義化結果的重排序"""
        # 建立不同的語義化結果
        semantic_places = sample_places[1:]  # 只包含後兩個地點
        
        # 執行測試
        result = rerank_service.rerank(sample_places, semantic_places, sample_story)
        
        # 驗證結果
        assert len(result) == 3
        # 應該包含所有地點，但順序可能不同
        place_ids = [place.id for place in result]
        assert "place1" in place_ids
        assert "place2" in place_ids
        assert "place3" in place_ids
    
    def test_rerank_duplicate_places(self, rerank_service, sample_story, sample_places):
        """測試重複地點的處理"""
        # 結構化和語義化結果包含相同地點
        structured_places = sample_places[:2]  # 前兩個地點
        semantic_places = sample_places[1:]    # 後兩個地點（有重複）
        
        # 執行測試
        result = rerank_service.rerank(structured_places, semantic_places, sample_story)
        
        # 驗證結果
        assert len(result) == 3
        # 每個地點只應該出現一次
        place_ids = [place.id for place in result]
        assert len(set(place_ids)) == 3  # 沒有重複
    
    def test_rerank_empty_results(self, rerank_service, sample_story):
        """測試空結果的重排序"""
        # 執行測試
        result = rerank_service.rerank([], [], sample_story)
        
        # 驗證結果
        assert len(result) == 0
    
    def test_rerank_large_results(self, rerank_service, sample_story):
        """測試大量結果的重排序（超過50個）"""
        # 建立大量地點
        large_places = []
        for i in range(60):
            place = Mock(spec=Place)
            place.id = f"place{i}"
            place.name = f"地點{i}"
            place.rating = 4.0
            place.categories = ["觀光"]
            place.price_level = 1
            large_places.append(place)
        
        # 執行測試
        result = rerank_service.rerank(large_places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 50  # 應該只返回前50個
    
    def test_rerank_rating_boost(self, rerank_service, sample_story):
        """測試評分加成的重排序"""
        # 建立不同評分的地點
        high_rating_place = Mock(spec=Place)
        high_rating_place.id = "high_rating"
        high_rating_place.name = "高評分地點"
        high_rating_place.rating = 4.9
        high_rating_place.categories = ["觀光"]
        high_rating_place.price_level = 1
        
        low_rating_place = Mock(spec=Place)
        low_rating_place.id = "low_rating"
        low_rating_place.name = "低評分地點"
        low_rating_place.rating = 3.0
        low_rating_place.categories = ["觀光"]
        low_rating_place.price_level = 1
        
        places = [low_rating_place, high_rating_place]
        
        # 執行測試
        result = rerank_service.rerank(places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 2
        # 高評分地點應該排在前面
        assert result[0].id == "high_rating"
        assert result[1].id == "low_rating"
    
    def test_rerank_category_match(self, rerank_service, sample_story):
        """測試類別匹配的重排序"""
        # 建立匹配和不匹配類別的地點
        matching_place = Mock(spec=Place)
        matching_place.id = "matching"
        matching_place.name = "匹配地點"
        matching_place.rating = 4.0
        matching_place.categories = ["文化", "歷史"]
        matching_place.price_level = 1
        
        non_matching_place = Mock(spec=Place)
        non_matching_place.id = "non_matching"
        non_matching_place.name = "不匹配地點"
        non_matching_place.rating = 4.0
        non_matching_place.categories = ["美食", "購物"]
        non_matching_place.price_level = 1
        
        places = [non_matching_place, matching_place]
        
        # 執行測試
        result = rerank_service.rerank(places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 2
        # 匹配類別的地點應該排在前面
        assert result[0].id == "matching"
        assert result[1].id == "non_matching"
    
    def test_rerank_budget_match(self, rerank_service, sample_story):
        """測試預算匹配的重排序"""
        # 建立不同價格等級的地點
        budget_place = Mock(spec=Place)
        budget_place.id = "budget"
        budget_place.name = "預算地點"
        budget_place.rating = 4.0
        budget_place.categories = ["觀光"]
        budget_place.price_level = 1
        
        expensive_place = Mock(spec=Place)
        expensive_place.id = "expensive"
        expensive_place.name = "昂貴地點"
        expensive_place.rating = 4.0
        expensive_place.categories = ["觀光"]
        expensive_place.price_level = 4
        
        places = [expensive_place, budget_place]
        
        # 執行測試
        result = rerank_service.rerank(places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 2
        # 預算匹配的地點應該排在前面（medium 預算更匹配 expensive）
        assert result[0].id == "expensive"
        assert result[1].id == "budget"
    
    def test_rerank_structured_vs_semantic(self, rerank_service, sample_story, sample_places):
        """測試結構化結果優先於語義化結果"""
        # 建立相同地點但不同來源
        structured_place = sample_places[0]
        semantic_place = sample_places[0]  # 相同地點
        
        # 執行測試
        result = rerank_service.rerank([structured_place], [semantic_place], sample_story)
        
        # 驗證結果
        assert len(result) == 1
        assert result[0].id == "place1"
    
    def test_rerank_rank_penalty(self, rerank_service, sample_story, sample_places):
        """測試排名懲罰的重排序"""
        # 建立大量地點
        many_places = []
        for i in range(10):
            place = Mock(spec=Place)
            place.id = f"place{i}"
            place.name = f"地點{i}"
            place.rating = 4.0
            place.categories = ["觀光"]
            place.price_level = 1
            many_places.append(place)
        
        # 執行測試
        result = rerank_service.rerank(many_places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 10
        # 前面的地點應該有更高的分數
        assert result[0].id == "place0"  # 第一個應該排在前面
    
    def test_rerank_mixed_quality(self, rerank_service, sample_story):
        """測試混合品質結果的重排序"""
        # 建立不同品質的地點
        high_quality = Mock(spec=Place)
        high_quality.id = "high"
        high_quality.name = "高品質地點"
        high_quality.rating = 4.8
        high_quality.categories = ["文化", "歷史"]
        high_quality.price_level = 1
        
        medium_quality = Mock(spec=Place)
        medium_quality.id = "medium"
        medium_quality.name = "中等品質地點"
        medium_quality.rating = 4.0
        medium_quality.categories = ["觀光"]
        medium_quality.price_level = 2
        
        low_quality = Mock(spec=Place)
        low_quality.id = "low"
        low_quality.name = "低品質地點"
        low_quality.rating = 3.0
        low_quality.categories = ["美食"]
        low_quality.price_level = 3
        
        places = [low_quality, medium_quality, high_quality]
        
        # 執行測試
        result = rerank_service.rerank(places, [], sample_story)
        
        # 驗證結果
        assert len(result) == 3
        # 高品質地點應該排在前面
        assert result[0].id == "high"
        assert result[1].id == "medium"
        assert result[2].id == "low"
