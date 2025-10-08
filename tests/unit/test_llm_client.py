"""
測試 llm_client.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.itinerary_planner.infrastructure.clients.llm_client import LLMClient, llm_client
from src.itinerary_planner.domain.models.story import Story, Preference, TimeWindow, AccommodationPreference


class TestLLMClient:
    """測試 LLM 客戶端"""

    def test_llm_client_initialization_with_gemini(self):
        """測試 LLM 客戶端使用 Gemini 初始化"""
        mock_gemini = Mock()
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.gemini_llm_client', mock_gemini):
            client = LLMClient()
            
            assert client.gemini_client == mock_gemini
            assert client.use_gemini is True

    def test_llm_client_initialization_without_gemini(self):
        """測試 LLM 客戶端不使用 Gemini 初始化"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.gemini_llm_client', None):
            client = LLMClient()
            
            assert client.gemini_client is None
            assert client.use_gemini is False

    def test_llm_client_initialization_gemini_error(self):
        """測試 LLM 客戶端 Gemini 初始化錯誤"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.gemini_llm_client', None):
            client = LLMClient()
            
            assert client.gemini_client is None
            assert client.use_gemini is False

    def test_extract_story_from_text_with_gemini_success(self):
        """測試使用 Gemini 成功提取 Story"""
        mock_story = Story(
            days=3,
            preference=Preference(themes=["美食"]),
            accommodation=AccommodationPreference(type="hotel"),
            daily_window=TimeWindow(start="09:00", end="18:00"),
            date_range=["2024-01-01", "2024-01-03"]
        )
        
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.gemini_llm_client', Mock()) as mock_gemini:
            mock_gemini.extract_story_from_text.return_value = mock_story
            
            client = LLMClient()
            client.use_gemini = True
            client.gemini_client = mock_gemini
            
            result = client.extract_story_from_text("我想去台北三天，喜歡美食")
            
            assert result == mock_story
            mock_gemini.extract_story_from_text.assert_called_once_with("我想去台北三天，喜歡美食")

    def test_extract_story_from_text_with_gemini_failure(self):
        """測試使用 Gemini 失敗後回退到規則解析"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.gemini_llm_client', Mock()) as mock_gemini:
            mock_gemini.extract_story_from_text.side_effect = Exception("Gemini API error")
            
            client = LLMClient()
            client.use_gemini = True
            client.gemini_client = mock_gemini
            
            result = client.extract_story_from_text("我想去台北三天，喜歡美食")
            
            assert isinstance(result, Story)
            assert result.days == 3
            assert "中式美食" in result.preference.themes

    def test_extract_story_from_text_rule_based_parsing(self):
        """測試規則解析"""
        client = LLMClient()
        client.use_gemini = False
        
        result = client.extract_story_from_text("我想去台北三天，喜歡美食")
        
        assert isinstance(result, Story)
        assert result.days == 3
        assert "中式美食" in result.preference.themes
        assert result.accommodation.type == "hotel"

    def test_rule_based_parsing_days_detection(self):
        """測試規則解析天數檢測"""
        client = LLMClient()
        
        # 測試不同天數
        test_cases = [
            ("我想去台北兩天", 2),
            ("我想去台北三天", 3),
            ("我想去台北四天", 4),
            ("我想去台北五天", 5),
            ("我想去台北六天", 6),
            ("我想去台北七天", 7),
            ("我想去台北", 1),  # 預設
        ]
        
        for input_text, expected_days in test_cases:
            result = client._rule_based_parsing(input_text)
            assert result.days == expected_days, f"Failed for input: {input_text}"

    def test_rule_based_parsing_themes_detection(self):
        """測試規則解析主題檢測"""
        client = LLMClient()
        
        # 測試自然風景
        result = client._rule_based_parsing("我想看自然風景和瀑布")
        assert "自然風景類" in result.preference.themes
        
        # 測試美食
        result = client._rule_based_parsing("我想品嚐美食和海鮮")
        assert "中式美食" in result.preference.themes
        
        # 測試文化
        result = client._rule_based_parsing("我想參觀博物館和古蹟")
        assert "文化景點" in result.preference.themes
        
        # 測試預設
        result = client._rule_based_parsing("我想去台北")
        assert "中式美食" in result.preference.themes

    def test_rule_based_parsing_accommodation_detection(self):
        """測試規則解析住宿類型檢測"""
        client = LLMClient()
        
        # 測試民宿
        result = client._rule_based_parsing("我想住民宿")
        assert result.accommodation.type == "homestay"
        
        # 測試青年旅館
        result = client._rule_based_parsing("我想住青年旅館")
        assert result.accommodation.type == "hostel"
        
        # 測試飯店
        result = client._rule_based_parsing("我想住飯店")
        assert result.accommodation.type == "hotel"
        
        # 測試預設
        result = client._rule_based_parsing("我想去台北")
        assert result.accommodation.type == "hotel"

    def test_rule_based_parsing_time_detection(self):
        """測試規則解析時間檢測"""
        client = LLMClient()
        
        # 測試開始時間
        result = client._rule_based_parsing("我想早上8點開始")
        assert result.daily_window.start == "08:00"
        
        result = client._rule_based_parsing("我想中午12點開始")
        assert result.daily_window.start == "12:00"
        
        # 測試結束時間
        result = client._rule_based_parsing("我想晚上10點結束")
        assert result.daily_window.end == "22:00"
        
        result = client._rule_based_parsing("我想晚上8點結束")
        assert result.daily_window.end == "20:00"
        
        # 測試預設時間
        result = client._rule_based_parsing("我想去台北")
        assert result.daily_window.start == "09:00"
        assert result.daily_window.end == "18:00"

    def test_rule_based_parsing_complex_input(self):
        """測試規則解析複雜輸入"""
        client = LLMClient()
        
        result = client._rule_based_parsing("我想去台北三天，喜歡自然風景，住民宿，早上7點開始，晚上9點結束")
        
        assert result.days == 3
        assert "自然風景類" in result.preference.themes
        assert result.accommodation.type == "homestay"
        assert result.daily_window.start == "07:00"
        assert result.daily_window.end == "21:00"

    def test_rule_based_parsing_accommodation_preference(self):
        """測試規則解析住宿偏好"""
        client = LLMClient()
        
        result = client._rule_based_parsing("我想去台北")
        
        assert result.accommodation.type == "hotel"
        assert result.accommodation.budget_range is None
        assert result.accommodation.location_preference == "near_attractions"

    def test_rule_based_parsing_story_structure(self):
        """測試規則解析 Story 結構"""
        client = LLMClient()
        
        result = client._rule_based_parsing("我想去台北三天")
        
        assert isinstance(result, Story)
        assert isinstance(result.preference, Preference)
        assert isinstance(result.accommodation, AccommodationPreference)
        assert isinstance(result.daily_window, TimeWindow)
        assert isinstance(result.date_range, list)
        assert len(result.date_range) == 2

    def test_singleton_instance(self):
        """測試單例實例"""
        # 驗證單例實例存在
        assert llm_client is not None
        assert isinstance(llm_client, LLMClient)

    def test_extract_story_from_text_no_gemini_client(self):
        """測試沒有 Gemini 客戶端時的回退"""
        client = LLMClient()
        client.use_gemini = True
        client.gemini_client = None
        
        result = client.extract_story_from_text("我想去台北三天")
        
        assert isinstance(result, Story)
        assert result.days == 3

    def test_rule_based_parsing_edge_cases(self):
        """測試規則解析邊界情況"""
        client = LLMClient()
        
        # 空輸入
        result = client._rule_based_parsing("")
        assert isinstance(result, Story)
        assert result.days == 1
        
        # 只有數字
        result = client._rule_based_parsing("三天")
        assert result.days == 3
        
        # 混合語言
        result = client._rule_based_parsing("我想去台北3天，喜歡hotel")
        assert result.days == 3
        assert result.accommodation.type == "hotel"

    def test_rule_based_parsing_multiple_themes(self):
        """測試規則解析多個主題"""
        client = LLMClient()
        
        result = client._rule_based_parsing("我想看自然風景和品嚐美食")
        
        assert "自然風景類" in result.preference.themes
        assert "中式美食" in result.preference.themes
        assert len(result.preference.themes) == 2
