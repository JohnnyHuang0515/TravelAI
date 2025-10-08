import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.itinerary_planner.infrastructure.clients.gemini_llm_client import GeminiLLMClient
from src.itinerary_planner.domain.models.story import Story, Preference, AccommodationPreference, TimeWindow


class TestGeminiLLMClient:
    """測試 GeminiLLMClient 類別"""

    @pytest.fixture
    def mock_api_key(self):
        """模擬 API 金鑰"""
        return "test-api-key-12345"

    @pytest.fixture
    def client(self, mock_api_key):
        """建立客戶端實例"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.genai') as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            return GeminiLLMClient(api_key=mock_api_key)

    def test_init_with_api_key(self, mock_api_key):
        """測試使用 API 金鑰初始化"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.genai') as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiLLMClient(api_key=mock_api_key)
            
            assert client.api_key == mock_api_key
            mock_genai.configure.assert_called_once_with(api_key=mock_api_key)
            mock_genai.GenerativeModel.assert_called_once_with('gemini-2.0-flash-exp')

    def test_init_with_env_variable(self):
        """測試從環境變數讀取 API 金鑰"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.genai') as mock_genai, \
             patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.os.getenv') as mock_getenv:
            
            mock_getenv.return_value = "env-api-key"
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiLLMClient()
            
            assert client.api_key == "env-api-key"
            mock_getenv.assert_called_once_with("GEMINI_API_KEY")

    def test_init_without_api_key_raises_error(self):
        """測試沒有 API 金鑰時拋出錯誤"""
        with patch('src.itinerary_planner.infrastructure.clients.gemini_llm_client.os.getenv') as mock_getenv:
            mock_getenv.return_value = None
            
            with pytest.raises(ValueError, match="Gemini API key is required"):
                GeminiLLMClient()

    def test_generate_text_success(self, client):
        """測試成功生成文字"""
        mock_response = Mock()
        mock_response.text = "  Generated response text  "
        client.model.generate_content.return_value = mock_response
        
        result = client.generate_text("Test prompt")
        
        assert result == "Generated response text"
        client.model.generate_content.assert_called_once_with("Test prompt")

    def test_generate_text_exception(self, client):
        """測試生成文字時發生異常"""
        client.model.generate_content.side_effect = Exception("API Error")
        
        result = client.generate_text("Test prompt")
        
        assert result == "抱歉，我無法處理您的請求。"

    def test_extract_story_from_text_success(self, client):
        """測試成功從文字提取故事"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "days": 3,
            "themes": ["自然風景類", "中式美食"],
            "accommodation_type": "hotel",
            "start_time": "08:00",
            "end_time": "20:00",
            "budget_range": [3000, 5000],
            "special_requirements": "攝影"
        })
        client.model.generate_content.return_value = mock_response
        
        result = client.extract_story_from_text("我想去台北三天兩夜，喜歡自然風景和美食")
        
        assert isinstance(result, Story)
        assert result.days == 3
        assert "自然風景類" in result.preference.themes
        assert "中式美食" in result.preference.themes
        assert result.accommodation.type == "hotel"
        assert result.daily_window.start == "08:00"
        assert result.daily_window.end == "20:00"
        assert result.accommodation.budget_range == (3000, 5000)

    def test_extract_story_from_text_with_markdown(self, client):
        """測試處理包含 markdown 格式的回應"""
        mock_response = Mock()
        mock_response.text = "```json\n" + json.dumps({
            "days": 2,
            "themes": ["文化景點"],
            "accommodation_type": "homestay"
        }) + "\n```"
        client.model.generate_content.return_value = mock_response
        
        result = client.extract_story_from_text("我想去台南兩天一夜")
        
        assert isinstance(result, Story)
        assert result.days == 2
        assert "文化景點" in result.preference.themes
        assert result.accommodation.type == "homestay"

    def test_extract_story_from_text_json_parse_error(self, client):
        """測試 JSON 解析錯誤時使用預設值"""
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        client.model.generate_content.return_value = mock_response
        
        result = client.extract_story_from_text("Test input")
        
        assert isinstance(result, Story)
        assert result.days == 1
        assert result.preference.themes == ["中式美食"]
        assert result.accommodation.type == "hotel"
        assert result.daily_window.start == "09:00"
        assert result.daily_window.end == "18:00"

    def test_extract_story_from_text_api_exception(self, client):
        """測試 API 調用異常時使用回退解析"""
        client.model.generate_content.side_effect = Exception("API Error")
        
        result = client.extract_story_from_text("我想去台北四天三夜，喜歡自然風景")
        
        assert isinstance(result, Story)
        assert result.days == 4  # 規則解析應該識別出四天
        assert "自然風景類" in result.preference.themes

    def test_build_extraction_prompt(self, client):
        """測試構建提取提示詞"""
        user_input = "我想去台北三天兩夜"
        prompt = client._build_extraction_prompt(user_input)
        
        assert "專業的旅遊行程規劃助手" in prompt
        assert user_input in prompt
        assert "JSON 格式" in prompt
        assert "days" in prompt
        assert "themes" in prompt
        assert "accommodation_type" in prompt

    def test_parse_gemini_response_success(self, client):
        """測試成功解析 Gemini 回應"""
        response_text = json.dumps({
            "days": 2,
            "themes": ["購物"],
            "accommodation_type": "hostel"
        })
        
        result = client._parse_gemini_response(response_text)
        
        assert result["days"] == 2
        assert result["themes"] == ["購物"]
        assert result["accommodation_type"] == "hostel"

    def test_parse_gemini_response_with_markdown(self, client):
        """測試解析包含 markdown 的回應"""
        response_text = "```json\n" + json.dumps({"days": 1}) + "\n```"
        
        result = client._parse_gemini_response(response_text)
        
        assert result["days"] == 1

    def test_parse_gemini_response_invalid_json(self, client):
        """測試解析無效 JSON 時返回預設值"""
        response_text = "Invalid JSON"
        
        result = client._parse_gemini_response(response_text)
        
        assert result["days"] == 1
        assert result["themes"] == ["中式美食"]
        assert result["accommodation_type"] == "hotel"
        assert result["start_time"] == "09:00"
        assert result["end_time"] == "18:00"
        assert result["budget_range"] is None
        assert result["special_requirements"] == ""

    def test_create_story_from_data(self, client):
        """測試從資料創建 Story 物件"""
        data = {
            "days": 3,
            "themes": ["自然風景類", "文化景點"],
            "accommodation_type": "hotel",
            "start_time": "08:00",
            "end_time": "20:00",
            "budget_range": [2000, 4000],
            "special_requirements": "攝影"
        }
        
        result = client._create_story_from_data(data)
        
        assert isinstance(result, Story)
        assert result.days == 3
        assert isinstance(result.preference, Preference)
        assert "自然風景類" in result.preference.themes
        assert "文化景點" in result.preference.themes
        assert isinstance(result.accommodation, AccommodationPreference)
        assert result.accommodation.type == "hotel"
        assert result.accommodation.budget_range == (2000, 4000)
        assert isinstance(result.daily_window, TimeWindow)
        assert result.daily_window.start == "08:00"
        assert result.daily_window.end == "20:00"
        assert result.date_range == ["2024-01-01", "2024-01-02"]

    def test_create_story_from_data_with_defaults(self, client):
        """測試使用預設值創建 Story 物件"""
        data = {}
        
        result = client._create_story_from_data(data)
        
        assert isinstance(result, Story)
        assert result.days == 1
        assert result.preference.themes == ["中式美食"]
        assert result.accommodation.type == "hotel"
        assert result.daily_window.start == "09:00"
        assert result.daily_window.end == "18:00"

    def test_fallback_rule_parsing_basic(self, client):
        """測試基本回退規則解析"""
        result = client._fallback_rule_parsing("我想去台北")
        
        assert isinstance(result, Story)
        assert result.days == 1
        assert result.preference.themes == ["中式美食"]
        assert result.accommodation.type == "hotel"
        assert result.daily_window.start == "09:00"
        assert result.daily_window.end == "18:00"

    def test_fallback_rule_parsing_days(self, client):
        """測試回退規則解析天數"""
        # 測試四天
        result = client._fallback_rule_parsing("我想去台北四天三夜")
        assert result.days == 4
        
        # 測試三天
        result = client._fallback_rule_parsing("我想去台北三天兩夜")
        assert result.days == 3
        
        # 測試兩天
        result = client._fallback_rule_parsing("我想去台北兩天一夜")
        assert result.days == 2

    def test_fallback_rule_parsing_themes(self, client):
        """測試回退規則解析主題"""
        result = client._fallback_rule_parsing("我想去看自然風景和瀑布")
        
        assert "自然風景類" in result.preference.themes
        assert "中式美食" in result.preference.themes  # 預設主題

    def test_fallback_rule_parsing_times(self, client):
        """測試回退規則解析時間"""
        result = client._fallback_rule_parsing("我想早上8點開始，晚上8點結束")
        
        assert result.daily_window.start == "08:00"
        assert result.daily_window.end == "20:00"

    def test_fallback_rule_parsing_complex(self, client):
        """測試複雜回退規則解析"""
        result = client._fallback_rule_parsing("我想去台北四天三夜，喜歡自然風景和攝影，早上8點開始")
        
        assert result.days == 4
        assert "自然風景類" in result.preference.themes
        assert result.daily_window.start == "08:00"
        assert result.daily_window.end == "18:00"  # 預設結束時間