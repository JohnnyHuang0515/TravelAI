import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from ...domain.models.story import Story, Preference, AccommodationPreference, TimeWindow

# 載入 .env 檔案
load_dotenv()

class GeminiLLMClient:
    """使用 Google Gemini API 的 LLM 客戶端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 客戶端
        
        Args:
            api_key: Gemini API 金鑰，如果未提供則從環境變數 GEMINI_API_KEY 讀取
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        # 配置 Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_text(self, prompt: str) -> str:
        """
        使用 Gemini API 生成文字回應
        
        Args:
            prompt: 輸入提示詞
            
        Returns:
            str: 生成的文字回應
        """
        try:
            # 調用 Gemini API
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating text with Gemini: {e}")
            return "抱歉，我無法處理您的請求。"

    def extract_story_from_text(self, user_input: str) -> Story:
        """
        使用 Gemini API 從使用者輸入中提取 Story 物件
        
        Args:
            user_input: 使用者的自然語言輸入
            
        Returns:
            Story: 解析後的行程故事物件
        """
        try:
            # 構建提示詞
            prompt = self._build_extraction_prompt(user_input)
            
            # 調用 Gemini API
            response = self.model.generate_content(prompt)
            print(f"🤖 Gemini API 回應: {response.text[:200]}...")
            
            # 解析回應
            story_data = self._parse_gemini_response(response.text)
            print(f"📊 解析後的資料: {story_data}")
            
            # 創建 Story 物件
            return self._create_story_from_data(story_data)
            
        except Exception as e:
            print(f"❌ Gemini API 調用失敗: {e}")
            # 回退到簡單的規則解析
            return self._fallback_rule_parsing(user_input)
    
    def _build_extraction_prompt(self, user_input: str) -> str:
        """構建用於提取行程資訊的提示詞"""
        return f"""
你是一個專業的旅遊行程規劃助手。請從以下用戶輸入中提取行程規劃所需的關鍵資訊，並以 JSON 格式回應。

用戶輸入：{user_input}

請提取以下資訊並以 JSON 格式回應：
{{
    "days": 行程天數（數字，預設為1）,
    "themes": 主題偏好（陣列，可選值：["自然風景類", "中式美食", "文化景點", "購物", "娛樂"]）,
    "accommodation_type": 住宿類型（字串，可選值："hotel", "homestay", "hostel"）,
    "start_time": 開始時間（字串，格式："HH:MM"，預設："09:00"）,
    "end_time": 結束時間（字串，格式："HH:MM"，預設："18:00"）,
    "budget_range": 預算範圍（陣列，格式：[最低, 最高]，單位：台幣，預設：null）,
    "special_requirements": 特殊需求（字串，如攝影、深度旅遊等，預設：""）
}}

注意事項：
1. 如果用戶提到"四天三夜"，天數應該是4
2. 如果用戶提到"早上8點開始"，start_time應該是"08:00"
3. 如果用戶提到"晚上8點結束"，end_time應該是"20:00"
4. 如果用戶提到預算"3000-5000元"，budget_range應該是[3000, 5000]
5. 如果用戶提到"攝影師"、"深度旅遊"等，記錄在special_requirements中
6. 只回應 JSON，不要包含其他文字
"""
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """解析 Gemini API 的回應"""
        try:
            # 清理回應文字，移除可能的 markdown 格式
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # 解析 JSON
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失敗: {e}")
            print(f"原始回應: {response_text}")
            # 回退到預設值
            return {
                "days": 1,
                "themes": ["中式美食"],
                "accommodation_type": "hotel",
                "start_time": "09:00",
                "end_time": "18:00",
                "budget_range": None,
                "special_requirements": ""
            }
    
    def _create_story_from_data(self, data: Dict[str, Any]) -> Story:
        """從解析的資料創建 Story 物件"""
        # 創建偏好物件
        preference = Preference(themes=data.get("themes", ["中式美食"]))
        
        # 創建時間窗物件
        time_window = TimeWindow(
            start=data.get("start_time", "09:00"),
            end=data.get("end_time", "18:00")
        )
        
        # 創建住宿偏好物件
        accommodation_type = data.get("accommodation_type") or "hotel"
        accommodation_pref = AccommodationPreference(
            type=accommodation_type,
            budget_range=data.get("budget_range"),
            location_preference="near_attractions"
        )
        
        # 創建 Story 物件
        return Story(
            days=data.get("days", 1),
            preference=preference,
            accommodation=accommodation_pref,
            daily_window=time_window,
            date_range=["2024-01-01", "2024-01-02"]  # 預設日期範圍
        )
    
    def _fallback_rule_parsing(self, user_input: str) -> Story:
        """回退到簡單的規則解析"""
        print("🔄 使用規則解析作為備用方案")
        
        # 簡單的規則解析邏輯
        days = 1
        themes = ["中式美食"]
        accommodation_type = "hotel"
        start_time = "09:00"
        end_time = "18:00"
        
        # 檢查天數
        if "四天" in user_input or "4天" in user_input:
            days = 4
        elif "三天" in user_input or "3天" in user_input:
            days = 3
        elif "兩天" in user_input or "2天" in user_input:
            days = 2
        
        # 檢查主題
        if any(keyword in user_input for keyword in ["自然風景", "瀑布", "山景", "攝影"]):
            themes.append("自然風景類")
        
        # 檢查時間
        if "早上8點" in user_input or "8點" in user_input:
            start_time = "08:00"
        if "晚上8點" in user_input or "8點結束" in user_input:
            end_time = "20:00"
        
        # 創建物件
        preference = Preference(themes=themes)
        time_window = TimeWindow(start=start_time, end=end_time)
        accommodation_pref = AccommodationPreference(type=accommodation_type or "hotel")
        
        return Story(
            days=days,
            preference=preference,
            accommodation=accommodation_pref,
            daily_window=time_window,
            date_range=["2024-01-01", "2024-01-02"]
        )

# 建立單例（需要設定環境變數 GEMINI_API_KEY）
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "test-key-for-demo":
        gemini_llm_client = GeminiLLMClient()
        print("✅ Gemini API 客戶端初始化成功")
    else:
        print("⚠️ GEMINI_API_KEY 未設定或為測試值，將使用規則解析")
        gemini_llm_client = None
except Exception as e:
    print(f"⚠️ Gemini API 初始化失敗: {e}")
    gemini_llm_client = None
