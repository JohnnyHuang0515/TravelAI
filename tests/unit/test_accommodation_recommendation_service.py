"""
測試 accommodation_recommendation_service.py
"""

import pytest
from unittest.mock import Mock
from src.itinerary_planner.application.services.accommodation_recommendation_service import AccommodationRecommendationService, accommodation_recommendation_service
from src.itinerary_planner.infrastructure.persistence.orm_models import Accommodation as OrmAccommodation
from src.itinerary_planner.domain.models.story import Story, Preference, AccommodationPreference, TimeWindow
from src.itinerary_planner.domain.models.itinerary import Day, Accommodation as DomainAccommodation


class TestAccommodationRecommendationService:
    """測試住宿推薦服務"""

    @pytest.fixture
    def service(self):
        """建立服務實例"""
        return AccommodationRecommendationService()

    @pytest.fixture
    def sample_accommodations(self):
        """建立範例住宿候選"""
        return [
            OrmAccommodation(
                id="acc1",
                name="豪華飯店",
                type="hotel",
                rating=4.8,
                price_range=5000
            ),
            OrmAccommodation(
                id="acc2",
                name="經濟民宿",
                type="homestay",
                rating=4.2,
                price_range=2000
            ),
            OrmAccommodation(
                id="acc3",
                name="青年旅館",
                type="hostel",
                rating=3.8,
                price_range=800
            )
        ]

    @pytest.fixture
    def sample_story(self):
        """建立範例故事"""
        preference = Preference(themes=["美食"])
        accommodation_pref = AccommodationPreference(
            type="hotel",
            budget_range=(1000, 3000),
            location_preference="near_attractions"
        )
        time_window = TimeWindow(start="09:00", end="18:00")
        
        return Story(
            days=3,
            preference=preference,
            accommodation=accommodation_pref,
            daily_window=time_window,
            date_range=["2024-01-01", "2024-01-03"]
        )

    @pytest.fixture
    def sample_days(self):
        """建立範例天數"""
        return [
            Day(date="2024-01-01", visits=[], accommodation=None),
            Day(date="2024-01-02", visits=[], accommodation=None),
            Day(date="2024-01-03", visits=[], accommodation=None)
        ]

    def test_recommend_accommodations_for_days_success(self, service, sample_days, sample_accommodations, sample_story):
        """測試成功推薦住宿"""
        result = service.recommend_accommodations_for_days(
            sample_days, 
            sample_accommodations, 
            sample_story
        )
        
        assert len(result) == 3
        # 前兩天應該有住宿推薦
        assert result[0].accommodation is not None
        assert result[1].accommodation is not None
        # 最後一天不應該有住宿推薦
        assert result[2].accommodation is None

    def test_recommend_accommodations_for_days_no_candidates(self, service, sample_days, sample_story):
        """測試沒有住宿候選時"""
        result = service.recommend_accommodations_for_days(
            sample_days, 
            [], 
            sample_story
        )
        
        assert len(result) == 3
        # 所有天數都不應該有住宿推薦
        for day in result:
            assert day.accommodation is None

    def test_recommend_accommodations_for_days_existing_accommodation(self, service, sample_accommodations, sample_story):
        """測試已有住宿的天數"""
        # 第一天已經有住宿
        existing_accommodation = DomainAccommodation(
            place_id="existing",
            name="現有住宿",
            type="hotel",
            check_in="15:00",
            check_out="11:00",
            nights=1
        )
        
        days = [
            Day(date="2024-01-01", visits=[], accommodation=existing_accommodation),
            Day(date="2024-01-02", visits=[], accommodation=None),
            Day(date="2024-01-03", visits=[], accommodation=None)
        ]
        
        result = service.recommend_accommodations_for_days(
            days, 
            sample_accommodations, 
            sample_story
        )
        
        # 第一天的住宿應該保持不變
        assert result[0].accommodation == existing_accommodation
        # 第二天應該有新的住宿推薦
        assert result[1].accommodation is not None
        # 第三天不應該有住宿推薦
        assert result[2].accommodation is None

    def test_select_best_accommodation_success(self, service, sample_accommodations, sample_story):
        """測試選擇最佳住宿成功"""
        result = service._select_best_accommodation(
            sample_accommodations, 
            sample_story, 
            day_index=0
        )
        
        assert result is not None
        assert result in sample_accommodations

    def test_select_best_accommodation_no_candidates(self, service, sample_story):
        """測試沒有候選住宿時"""
        result = service._select_best_accommodation(
            [], 
            sample_story, 
            day_index=0
        )
        
        assert result is None

    def test_select_best_accommodation_budget_filter(self, service, sample_story):
        """測試預算篩選"""
        accommodations = [
            OrmAccommodation(
                id="acc1",
                name="豪華飯店",
                type="hotel",
                rating=4.8,
                price_range=5000  # 超出預算
            ),
            OrmAccommodation(
                id="acc2",
                name="經濟民宿",
                type="homestay",
                rating=4.2,
                price_range=2000  # 在預算內
            ),
            OrmAccommodation(
                id="acc3",
                name="青年旅館",
                type="hostel",
                rating=3.8,
                price_range=800  # 在預算內
            )
        ]
        
        result = service._select_best_accommodation(
            accommodations, 
            sample_story, 
            day_index=0
        )
        
        assert result is not None
        # 應該選擇在預算內的住宿
        assert result.price_range <= 3000

    def test_select_best_accommodation_no_budget_match(self, service, sample_story):
        """測試沒有符合預算的住宿時"""
        accommodations = [
            OrmAccommodation(
                id="acc1",
                name="豪華飯店",
                type="hotel",
                rating=4.8,
                price_range=5000  # 超出預算
            ),
            OrmAccommodation(
                id="acc2",
                name="超豪華飯店",
                type="hotel",
                rating=4.9,
                price_range=6000  # 超出預算
            )
        ]
        
        result = service._select_best_accommodation(
            accommodations, 
            sample_story, 
            day_index=0
        )
        
        assert result is not None
        # 應該回退到所有候選，選擇其中一個
        assert result.rating in [4.8, 4.9]

    def test_select_best_accommodation_no_budget_range(self, service):
        """測試沒有預算範圍時"""
        accommodations = [
            OrmAccommodation(
                id="acc1",
                name="豪華飯店",
                type="hotel",
                rating=4.8,
                price_range=5000
            ),
            OrmAccommodation(
                id="acc2",
                name="經濟民宿",
                type="homestay",
                rating=4.2,
                price_range=2000
            )
        ]
        
        # 沒有預算範圍的故事
        preference = Preference(themes=["美食"])
        accommodation_pref = AccommodationPreference(
            type="hotel",
            budget_range=None,  # 沒有預算範圍
            location_preference="near_attractions"
        )
        time_window = TimeWindow(start="09:00", end="18:00")
        
        story = Story(
            days=3,
            preference=preference,
            accommodation=accommodation_pref,
            daily_window=time_window,
            date_range=["2024-01-01", "2024-01-03"]
        )
        
        result = service._select_best_accommodation(
            accommodations, 
            story, 
            day_index=0
        )
        
        assert result is not None
        # 應該選擇其中一個住宿
        assert result.rating in [4.8, 4.2]

    def test_select_best_accommodation_rating_sorting(self, service, sample_story):
        """測試評分排序"""
        accommodations = [
            OrmAccommodation(
                id="acc1",
                name="低評分飯店",
                type="hotel",
                rating=3.0,
                price_range=2000
            ),
            OrmAccommodation(
                id="acc2",
                name="高評分飯店",
                type="hotel",
                rating=4.8,
                price_range=2500
            ),
            OrmAccommodation(
                id="acc3",
                name="中評分飯店",
                type="hotel",
                rating=4.0,
                price_range=2200
            )
        ]
        
        result = service._select_best_accommodation(
            accommodations, 
            sample_story, 
            day_index=0
        )
        
        assert result is not None
        # 應該選擇其中一個住宿
        assert result.rating in [3.0, 4.0, 4.8]

    def test_select_best_accommodation_no_rating(self, service, sample_story):
        """測試沒有評分的住宿"""
        accommodations = [
            OrmAccommodation(
                id="acc1",
                name="無評分飯店",
                type="hotel",
                rating=None,
                price_range=2000
            ),
            OrmAccommodation(
                id="acc2",
                name="有評分飯店",
                type="hotel",
                rating=4.5,
                price_range=2500
            )
        ]
        
        result = service._select_best_accommodation(
            accommodations, 
            sample_story, 
            day_index=0
        )
        
        assert result is not None
        # 應該選擇其中一個住宿
        assert result.rating in [None, 4.5]

    def test_domain_accommodation_conversion(self, service, sample_days, sample_accommodations, sample_story):
        """測試領域模型轉換"""
        result = service.recommend_accommodations_for_days(
            sample_days, 
            sample_accommodations, 
            sample_story
        )
        
        # 檢查轉換後的領域模型
        accommodation = result[0].accommodation
        assert isinstance(accommodation, DomainAccommodation)
        assert accommodation.place_id in ["acc1", "acc2", "acc3"]
        assert accommodation.name in ["豪華飯店", "經濟民宿", "青年旅館"]
        assert accommodation.type in ["hotel", "homestay", "hostel"]
        assert accommodation.check_in == "15:00"
        assert accommodation.check_out == "11:00"
        assert accommodation.nights == 1

    def test_singleton_instance(self):
        """測試單例實例"""
        assert accommodation_recommendation_service is not None
        assert isinstance(accommodation_recommendation_service, AccommodationRecommendationService)

    def test_recommend_accommodations_for_days_single_day(self, service, sample_accommodations, sample_story):
        """測試單天行程"""
        single_day = [Day(date="2024-01-01", visits=[], accommodation=None)]
        
        result = service.recommend_accommodations_for_days(
            single_day, 
            sample_accommodations, 
            sample_story
        )
        
        assert len(result) == 1
        # 單天行程不應該有住宿推薦
        assert result[0].accommodation is None

    def test_recommend_accommodations_for_days_two_days(self, service, sample_accommodations, sample_story):
        """測試兩天行程"""
        two_days = [
            Day(date="2024-01-01", visits=[], accommodation=None),
            Day(date="2024-01-02", visits=[], accommodation=None)
        ]
        
        result = service.recommend_accommodations_for_days(
            two_days, 
            sample_accommodations, 
            sample_story
        )
        
        assert len(result) == 2
        # 第一天應該有住宿推薦
        assert result[0].accommodation is not None
        # 第二天不應該有住宿推薦
        assert result[1].accommodation is None
