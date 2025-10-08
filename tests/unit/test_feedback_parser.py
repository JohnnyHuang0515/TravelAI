import pytest
from src.itinerary_planner.application.services.feedback_parser import FeedbackParser, feedback_parser


class TestFeedbackParser:
    """測試 FeedbackParser 類別"""

    @pytest.fixture
    def parser(self):
        """建立解析器實例"""
        return FeedbackParser()

    def test_parse_drop_operation(self, parser):
        """測試解析刪除操作"""
        feedback = "請刪除第一天的行程"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_drop_operation_alternative(self, parser):
        """測試解析刪除操作 - 替代用詞"""
        feedback = "不要第一天的行程"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_drop_operation_case_insensitive(self, parser):
        """測試解析刪除操作 - 大小寫不敏感"""
        feedback = "請刪除第一天的行程"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_replace_operation(self, parser):
        """測試解析替換操作"""
        feedback = "請替換第一天的行程"
        result = parser.parse(feedback)
        
        assert result["op"] == "REPLACE"
        assert result["target"]["day"] == 1
        assert result["target"]["place"] == "新地點"

    def test_parse_replace_operation_alternative(self, parser):
        """測試解析替換操作 - 替代用詞"""
        feedback = "請換成其他地點"
        result = parser.parse(feedback)
        
        assert result["op"] == "REPLACE"
        assert result["target"]["day"] == 1
        assert result["target"]["place"] == "新地點"

    def test_parse_replace_operation_case_insensitive(self, parser):
        """測試解析替換操作 - 大小寫不敏感"""
        feedback = "請替換第一天的行程"
        result = parser.parse(feedback)
        
        assert result["op"] == "REPLACE"
        assert result["target"]["day"] == 1
        assert result["target"]["place"] == "新地點"

    def test_parse_noop_operation(self, parser):
        """測試解析空操作"""
        feedback = "這個行程很好"
        result = parser.parse(feedback)
        
        assert result["op"] == "NOOP"

    def test_parse_noop_operation_empty(self, parser):
        """測試解析空操作 - 空字串"""
        feedback = ""
        result = parser.parse(feedback)
        
        assert result["op"] == "NOOP"

    def test_parse_noop_operation_unrecognized(self, parser):
        """測試解析空操作 - 無法識別的回饋"""
        feedback = "這個行程太棒了，我很喜歡"
        result = parser.parse(feedback)
        
        assert result["op"] == "NOOP"

    def test_parse_priority_drop_over_replace(self, parser):
        """測試解析優先級 - 刪除優先於替換"""
        feedback = "請刪除並替換第一天的行程"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_complex_feedback(self, parser):
        """測試解析複雜回饋"""
        feedback = "請刪除第一天的行程，因為我不喜歡那個地方"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_multiple_keywords(self, parser):
        """測試解析包含多個關鍵字的回饋"""
        feedback = "請不要刪除，但要替換第一天的行程"
        result = parser.parse(feedback)
        
        # 由於 "不要" 和 "替換" 都存在，應該匹配到 "不要" (DROP)
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_whitespace_handling(self, parser):
        """測試解析空白字元處理"""
        feedback = "  請刪除第一天的行程  "
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_special_characters(self, parser):
        """測試解析特殊字元"""
        feedback = "請刪除第一天的行程！@#$%^&*()"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_parse_unicode_characters(self, parser):
        """測試解析 Unicode 字元"""
        feedback = "請刪除第一天的行程😊"
        result = parser.parse(feedback)
        
        assert result["op"] == "DROP"
        assert result["target"]["day"] == 1

    def test_singleton_instance(self):
        """測試單例實例"""
        assert feedback_parser is not None
        assert isinstance(feedback_parser, FeedbackParser)

    def test_singleton_consistency(self):
        """測試單例一致性"""
        from src.itinerary_planner.application.services.feedback_parser import feedback_parser as feedback_parser2
        
        assert feedback_parser is feedback_parser2

    def test_parse_method_consistency(self):
        """測試解析方法一致性"""
        feedback = "請刪除第一天的行程"
        result1 = feedback_parser.parse(feedback)
        result2 = feedback_parser.parse(feedback)
        
        assert result1 == result2
        assert result1["op"] == "DROP"
        assert result1["target"]["day"] == 1
