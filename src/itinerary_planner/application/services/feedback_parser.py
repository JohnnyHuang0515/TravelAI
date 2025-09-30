from typing import Dict, Any

class FeedbackParser:
    """回饋解析服務，將自然語言回饋轉換為 DSL"""
    
    def parse(self, feedback_text: str) -> Dict[str, Any]:
        """
        解析使用者回饋為 DSL 指令
        """
        feedback_lower = feedback_text.lower()
        
        # 簡單的規則解析
        if "刪除" in feedback_lower or "不要" in feedback_lower:
            return {
                "op": "DROP",
                "target": {
                    "day": 1  # 預設刪除第一天
                }
            }
        
        if "替換" in feedback_lower or "換成" in feedback_lower:
            return {
                "op": "REPLACE",
                "target": {
                    "day": 1,
                    "place": "新地點"
                }
            }
        
        # 預設返回空操作
        return {"op": "NOOP"}

# 建立單例
feedback_parser = FeedbackParser()