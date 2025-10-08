"""
行程規劃服務單元測試
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, time, timedelta
from uuid import uuid4

from src.itinerary_planner.application.services.planning_service import GreedyPlanner
from src.itinerary_planner.domain.models.itinerary import Itinerary, Day, Visit, Accommodation
from src.itinerary_planner.domain.models.story import Story, Preference, TimeWindow
from tests.test_orm_models import Place as OrmPlace


class TestGreedyPlanner:
    """貪婪規劃器測試類別"""
    
    @pytest.fixture
    def planner(self):
        """建立規劃器實例"""
        return GreedyPlanner()
    
    @pytest.fixture
    def sample_story(self):
        """測試用的故事資料"""
        preference = Preference(
            themes=["美食", "景點"]
        )
        daily_window = TimeWindow(start="09:00", end="18:00")
        date_range = ["2025-02-01", "2025-02-02"]
        
        return Story(
            days=2,
            preference=preference,
            daily_window=daily_window,
            date_range=date_range
        )
    
    @pytest.fixture
    def sample_places(self):
        """測試用的景點資料"""
        places = []
        for i in range(3):
            place = Mock(spec=OrmPlace)
            place.id = str(uuid4())
            place.name = f"景點{i+1}"
            place.stay_minutes = 60 + i * 30  # 60, 90, 120 分鐘
            place.rating = 4.0 + i * 0.5  # 4.0, 4.5, 5.0
            places.append(place)
        return places
    
    @pytest.fixture
    def sample_travel_matrix(self):
        """測試用的交通時間矩陣"""
        return [
            [0, 30, 60],    # 從景點1到各景點的時間
            [30, 0, 45],    # 從景點2到各景點的時間
            [60, 45, 0]     # 從景點3到各景點的時間
        ]
    
    @pytest.fixture
    def sample_hours_map(self):
        """測試用的營業時間資料"""
        return {
            "place1": [Mock(weekday=1, open_min=540, close_min=1080)],  # 週一 09:00-18:00
            "place2": [Mock(weekday=1, open_min=600, close_min=1200)],  # 週一 10:00-20:00
            "place3": [Mock(weekday=1, open_min=480, close_min=1020)]   # 週一 08:00-17:00
        }
    
    @patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal')
    @patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository')
    def test_plan_success(self, mock_repo_class, mock_session, planner, sample_story, sample_places, sample_travel_matrix):
        """測試成功規劃行程"""
        # Mock 資料庫和 repository
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_hours_for_places.return_value = {}
        
        # 執行測試
        result = planner.plan(sample_story, sample_places, sample_travel_matrix)
        
        # 驗證結果
        assert isinstance(result, Itinerary)
        assert len(result.days) == 2  # 2 天行程
        
        # 驗證資料庫操作
        assert mock_session.call_count >= 1  # 可能被調用多次
        mock_repo_class.assert_called_once_with(mock_db)
        assert mock_db.close.call_count >= 1  # 可能被調用多次
    
    @patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal')
    @patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository')
    def test_plan_with_hours_map(self, mock_repo_class, mock_session, planner, sample_story, sample_places, sample_travel_matrix, sample_hours_map):
        """測試帶營業時間的行程規劃"""
        # Mock 資料庫和 repository
        mock_db = Mock()
        mock_session.return_value = mock_db
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_hours_for_places.return_value = sample_hours_map
        
        # 執行測試
        result = planner.plan(sample_story, sample_places, sample_travel_matrix)
        
        # 驗證結果
        assert isinstance(result, Itinerary)
        assert len(result.days) == 2
        
        # 驗證 repository 呼叫
        expected_place_ids = [str(p.id) for p in sample_places]
        mock_repo.get_hours_for_places.assert_called_once_with(expected_place_ids)
    
    def test_parse_time_to_minutes(self, planner):
        """測試時間解析功能"""
        # 測試各種時間格式
        assert planner._parse_time_to_minutes("09:00") == 540  # 9 * 60
        assert planner._parse_time_to_minutes("12:30") == 750  # 12 * 60 + 30
        assert planner._parse_time_to_minutes("18:00") == 1080  # 18 * 60
        assert planner._parse_time_to_minutes("00:00") == 0
        assert planner._parse_time_to_minutes("23:59") == 1439
    
    def test_minutes_to_time_str(self, planner):
        """測試分鐘轉時間字串功能"""
        # 測試各種分鐘數
        assert planner._minutes_to_time_str(540) == "09:00"
        assert planner._minutes_to_time_str(750) == "12:30"
        assert planner._minutes_to_time_str(1080) == "18:00"
        assert planner._minutes_to_time_str(0) == "00:00"
        assert planner._minutes_to_time_str(1439) == "23:59"
    
    def test_is_open_with_hours(self, planner, sample_hours_map):
        """測試營業時間檢查功能"""
        # 測試在營業時間內
        assert planner._is_open("place1", 600, 0, sample_hours_map) == True  # 週一 10:00
        assert planner._is_open("place2", 900, 0, sample_hours_map) == True  # 週一 15:00
        
        # 測試在營業時間外
        assert planner._is_open("place1", 500, 0, sample_hours_map) == False  # 週一 08:20 (太早)
        assert planner._is_open("place1", 1100, 0, sample_hours_map) == False  # 週一 18:20 (太晚)
        
        # 測試沒有營業時間資訊的地點
        assert planner._is_open("unknown_place", 600, 0, sample_hours_map) == True
    
    def test_is_open_no_hours(self, planner):
        """測試沒有營業時間資訊的情況"""
        # 沒有營業時間資訊，應該返回 True (假設全天開放)
        assert planner._is_open("any_place", 600, 0, {}) == True
        assert planner._is_open("any_place", 0, 0, {}) == True
        assert planner._is_open("any_place", 1439, 0, {}) == True
    
    def test_find_next_best_visit(self, planner, sample_places, sample_travel_matrix):
        """測試尋找下一個最佳訪問地點"""
        # 建立 place_id_to_idx 映射
        place_id_to_idx = {str(p.id): i for i, p in enumerate(sample_places)}
        visited_place_ids = set()
        hours_map = {}
        
        # 測試找到下一個地點
        result = planner._find_next_best_visit(
            sample_places,
            sample_travel_matrix,
            place_id_to_idx,
            visited_place_ids,
            from_place_idx=0,
            current_time=540,  # 09:00
            day_end_time=1080,  # 18:00
            hours_map=hours_map,
            weekday=0  # 週一
        )
        
        # 應該找到一個地點
        assert result is not None
        place, travel_minutes = result
        assert place in sample_places
        assert travel_minutes >= 0
    
    def test_find_next_best_visit_all_visited(self, planner, sample_places, sample_travel_matrix):
        """測試所有地點都已訪問的情況"""
        # 建立 place_id_to_idx 映射
        place_id_to_idx = {str(p.id): i for i, p in enumerate(sample_places)}
        visited_place_ids = {str(p.id) for p in sample_places}  # 所有地點都已訪問
        hours_map = {}
        
        # 測試找不到地點
        result = planner._find_next_best_visit(
            sample_places,
            sample_travel_matrix,
            place_id_to_idx,
            visited_place_ids,
            from_place_idx=0,
            current_time=540,  # 09:00
            day_end_time=1080,  # 18:00
            hours_map=hours_map,
            weekday=0  # 週一
        )
        
        # 應該返回 None
        assert result is None
    
    def test_find_next_best_visit_time_exceeded(self, planner, sample_places, sample_travel_matrix):
        """測試時間超過的情況"""
        # 建立 place_id_to_idx 映射
        place_id_to_idx = {str(p.id): i for i, p in enumerate(sample_places)}
        visited_place_ids = set()
        hours_map = {}
        
        # 測試時間已經很晚
        result = planner._find_next_best_visit(
            sample_places,
            sample_travel_matrix,
            place_id_to_idx,
            visited_place_ids,
            from_place_idx=0,
            current_time=1200,  # 20:00 (超過結束時間)
            day_end_time=1080,  # 18:00
            hours_map=hours_map,
            weekday=0  # 週一
        )
        
        # 應該返回 None
        assert result is None
    
    @patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal')
    def test_get_accommodation_for_day(self, mock_session, planner, sample_story):
        """測試獲取住宿推薦"""
        # Mock 資料庫會話
        mock_db = Mock()
        mock_session.return_value = mock_db
        
        # Mock 查詢鏈
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None  # 沒有找到住宿
        mock_db.query.return_value = mock_query
        
        # 測試第一天的住宿
        accommodation = planner._get_accommodation_for_day(0, sample_story)
        
        # 應該返回 None（因為沒有找到住宿）
        assert accommodation is None
        mock_session.assert_called_once()
        mock_db.close.assert_called_once()
    
    def test_refine_with_2_opt(self, planner, sample_places, sample_travel_matrix):
        """測試 2-opt 優化"""
        # 建立測試用的行程天數
        visits = [
            Visit(
                place_id=str(sample_places[0].id),
                name=sample_places[0].name,
                eta="09:00",
                etd="10:00",
                travel_minutes=0
            ),
            Visit(
                place_id=str(sample_places[1].id),
                name=sample_places[1].name,
                eta="10:30",
                etd="12:00",
                travel_minutes=30
            )
        ]
        
        day_plan = Day(
            date="2025-02-01",
            visits=visits,
            accommodation=None
        )
        
        place_id_to_idx = {str(p.id): i for i, p in enumerate(sample_places)}
        
        # 執行 2-opt 優化
        planner._refine_with_2_opt(day_plan, sample_places, sample_travel_matrix, place_id_to_idx)
        
        # 驗證行程仍然有效
        assert len(day_plan.visits) == 2
        assert day_plan.visits[0].name == sample_places[0].name
        assert day_plan.visits[1].name == sample_places[1].name
    
    def test_plan_empty_candidates(self, planner, sample_story):
        """測試空候選地點列表"""
        # Mock 資料庫
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session, \
             patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
            
            mock_db = Mock()
            mock_session.return_value = mock_db
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_hours_for_places.return_value = {}
            
            # 執行測試
            result = planner.plan(sample_story, [], [])
            
            # 驗證結果
            assert isinstance(result, Itinerary)
            assert len(result.days) == 2  # 仍然有 2 天，但沒有訪問
    
    def test_plan_single_day(self, planner, sample_places, sample_travel_matrix):
        """測試單天行程"""
        # 建立單天故事
        preference = Preference(themes=["美食"])
        daily_window = TimeWindow(start="10:00", end="16:00")
        date_range = ["2025-02-01", "2025-02-01"]
        
        single_day_story = Story(
            days=1,
            preference=preference,
            daily_window=daily_window,
            date_range=date_range
        )
        
        # Mock 資料庫
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session, \
             patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
            
            mock_db = Mock()
            mock_session.return_value = mock_db
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_hours_for_places.return_value = {}
            
            # 執行測試
            result = planner.plan(single_day_story, sample_places, sample_travel_matrix)
            
            # 驗證結果
            assert isinstance(result, Itinerary)
            assert len(result.days) == 1
    
    def test_plan_without_date_range(self, planner, sample_places, sample_travel_matrix):
        """測試沒有日期範圍的故事"""
        # 建立沒有日期範圍的故事
        preference = Preference(themes=["景點"])
        daily_window = TimeWindow(start="08:00", end="20:00")
        
        story_without_date = Story(
            days=2,
            preference=preference,
            daily_window=daily_window,
            date_range=None
        )
        
        # Mock 資料庫
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session, \
             patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
            
            mock_db = Mock()
            mock_session.return_value = mock_db
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_hours_for_places.return_value = {}
            
            # 執行測試
            result = planner.plan(story_without_date, sample_places, sample_travel_matrix)
            
            # 驗證結果
            assert isinstance(result, Itinerary)
            assert len(result.days) == 2
    
    def test_plan_without_daily_window(self, planner, sample_places, sample_travel_matrix):
        """測試沒有每日時間窗的故事"""
        # 建立沒有每日時間窗的故事
        preference = Preference(themes=["購物"])
        date_range = ["2025-02-01", "2025-02-02"]
        
        story_without_window = Story(
            days=2,
            preference=preference,
            daily_window=None,
            date_range=date_range
        )
        
        # Mock 資料庫
        with patch('src.itinerary_planner.infrastructure.persistence.database.SessionLocal') as mock_session, \
             patch('src.itinerary_planner.infrastructure.repositories.postgres_place_repo.PostgresPlaceRepository') as mock_repo_class:
            
            mock_db = Mock()
            mock_session.return_value = mock_db
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_hours_for_places.return_value = {}
            
            # 執行測試
            result = planner.plan(story_without_window, sample_places, sample_travel_matrix)
            
            # 驗證結果
            assert isinstance(result, Itinerary)
            assert len(result.days) == 2
