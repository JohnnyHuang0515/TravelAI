from typing import Dict, Any
from ..persistence.database import SessionLocal
from ...domain.models.story import Story, AccommodationPreference

class LLMClient:
    """LLM 客戶端，用於處理自然語言理解任務"""
    
    def __init__(self):
        """初始化 LLM 客戶端，優先使用 Gemini API"""
        try:
            from .gemini_llm_client import gemini_llm_client
            self.gemini_client = gemini_llm_client
            self.use_gemini = gemini_llm_client is not None
            if self.use_gemini:
                print("✅ 使用 Gemini API 進行自然語言理解")
            else:
                print("⚠️ 使用規則解析進行自然語言理解")
        except Exception as e:
            print(f"⚠️ Gemini API 初始化失敗: {e}")
            self.gemini_client = None
            self.use_gemini = False
    
    def extract_story_from_text(self, user_input: str) -> Story:
        """
        從使用者輸入中提取 Story 物件
        優先使用 Gemini API，如果失敗則回退到規則解析
        """
        print(f"🔍 LLM 客戶端調用: use_gemini={self.use_gemini}, gemini_client={self.gemini_client is not None}")
        
        if self.use_gemini and self.gemini_client:
            try:
                return self.gemini_client.extract_story_from_text(user_input)
            except Exception as e:
                print(f"❌ Gemini API 調用失敗: {e}")
                print("🔄 回退到規則解析")
        
        # 回退到規則解析
        return self._rule_based_parsing(user_input)
    
    def _rule_based_parsing(self, user_input: str) -> Story:
        """
        規則解析備用方案
        """
        print(f"🔍 規則解析調用: {user_input[:50]}...")
        # 簡單的規則解析示例
        days = 1
        themes = ["中式美食"]  # 預設為中式美食
        accommodation_type = "hotel"  # 預設為飯店
        
        # 檢查是否提到天數 - 支援更多天數
        if "四天" in user_input or "4天" in user_input:
            days = 4
        elif "三天" in user_input or "3天" in user_input:
            days = 3
        elif "兩天" in user_input or "2天" in user_input:
            days = 2
        elif "五天" in user_input or "5天" in user_input:
            days = 5
        elif "六天" in user_input or "6天" in user_input:
            days = 6
        elif "七天" in user_input or "7天" in user_input:
            days = 7
        
        # 檢查主題偏好 - 更詳細的識別
        themes = []
        
        # 自然風景相關
        if any(keyword in user_input for keyword in ["自然風景", "瀑布", "山景", "湖光山色", "攝影", "風景", "自然"]):
            themes.append("自然風景類")
        
        # 美食相關
        if any(keyword in user_input for keyword in ["美食", "餐廳", "海鮮", "料理", "品嚐", "特色美食"]):
            themes.append("中式美食")
        
        # 文化相關
        if any(keyword in user_input for keyword in ["文化", "歷史", "古蹟", "博物館", "文化景點"]):
            themes.append("文化景點")
        
        # 如果沒有識別到任何主題，使用預設
        if not themes:
            themes = ["中式美食"]
        
        # 檢查住宿偏好
        if "民宿" in user_input or "homestay" in user_input.lower():
            accommodation_type = "homestay"
        elif "青年旅館" in user_input or "hostel" in user_input.lower():
            accommodation_type = "hostel"
        elif "飯店" in user_input or "酒店" in user_input or "hotel" in user_input.lower():
            accommodation_type = "hotel"
        
        # 解析時間偏好
        start_time = "09:00"  # 預設
        end_time = "18:00"    # 預設
        
        # 檢查開始時間
        if "中午12點" in user_input or "12點" in user_input:
            start_time = "12:00"
            print("✅ 規則解析: 找到中午12點")
        elif "早上8點" in user_input or "8點" in user_input or "上午8" in user_input:
            start_time = "08:00"
            print("✅ 規則解析: 找到早上8點")
        elif "早上7點" in user_input or "7點" in user_input:
            start_time = "07:00"
            print("✅ 規則解析: 找到早上7點")
        elif "早上9點" in user_input or "9點" in user_input:
            start_time = "09:00"
            print("✅ 規則解析: 找到早上9點")
        
        # 檢查結束時間
        if "晚上10點" in user_input or "10點結束" in user_input:
            end_time = "22:00"
            print("✅ 規則解析: 找到晚上10點")
        elif "晚上8點" in user_input or "8點結束" in user_input:
            end_time = "20:00"
            print("✅ 規則解析: 找到晚上8點")
        elif "晚上9點" in user_input or "9點結束" in user_input:
            end_time = "21:00"
            print("✅ 規則解析: 找到晚上9點")
        elif "晚上7點" in user_input or "7點結束" in user_input:
            end_time = "19:00"
            print("✅ 規則解析: 找到晚上7點")
        
        print(f"🕐 規則解析時間結果: {start_time} - {end_time}")
        
        # 創建 Story 物件
        from ...domain.models.story import Preference, TimeWindow
        preference = Preference(themes=themes)
        time_window = TimeWindow(start=start_time, end=end_time)
        
        # 創建住宿偏好
        accommodation_pref = AccommodationPreference(
            type=accommodation_type,
            budget_range=None,  # 暫時不解析預算
            location_preference="near_attractions"  # 預設靠近景點
        )
        
        return Story(
            days=days,
            preference=preference,
            accommodation=accommodation_pref,  # 新增住宿偏好
            daily_window=time_window,
            date_range=["2024-01-01", "2024-01-02"]
        )

# 建立單例
llm_client = LLMClient()