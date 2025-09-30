#!/usr/bin/env python3
"""
調試 Gemini API 的時間理解邏輯
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# 載入 .env 檔案
load_dotenv()

def test_gemini_time_understanding():
    """測試 Gemini API 的時間理解"""
    print("🔍 **Gemini API 時間理解調試**")
    print("=" * 50)
    
    # 配置 Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 無法讀取 GEMINI_API_KEY")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # 測試輸入
    user_input = "我計劃中午12點開始行程，晚上10點結束"
    print(f"📝 測試輸入: {user_input}")
    
    # 構建提示詞
    prompt = f"""
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
    
    print(f"\n🤖 **Gemini API 提示詞**:")
    print(prompt[:200] + "...")
    
    try:
        # 調用 Gemini API
        print(f"\n🔄 **調用 Gemini API...**")
        response = model.generate_content(prompt)
        
        print(f"\n📤 **Gemini API 原始回應**:")
        print(response.text)
        
        # 解析回應
        print(f"\n🔍 **解析回應...**")
        try:
            # 清理回應文字
            cleaned_text = response.text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # 解析 JSON
            parsed_data = json.loads(cleaned_text)
            print(f"✅ JSON 解析成功:")
            print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
            
            # 檢查時間理解
            print(f"\n⏰ **時間理解檢查**:")
            start_time = parsed_data.get("start_time", "未設定")
            end_time = parsed_data.get("end_time", "未設定")
            
            print(f"  開始時間: {start_time}")
            print(f"  結束時間: {end_time}")
            
            if start_time == "12:00":
                print("  ✅ 正確識別中午12點")
            else:
                print(f"  ❌ 期望12:00，實際{start_time}")
            
            if end_time == "22:00":
                print("  ✅ 正確識別晚上10點")
            else:
                print(f"  ❌ 期望22:00，實際{end_time}")
            
            # 整體評估
            if start_time == "12:00" and end_time == "22:00":
                print(f"\n🎉 **Gemini API 時間理解完美！**")
            else:
                print(f"\n⚠️ **Gemini API 時間理解需要改進**")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失敗: {e}")
            print(f"原始回應: {response.text}")
            
    except Exception as e:
        print(f"❌ Gemini API 調用失敗: {e}")

def test_simple_time_extraction():
    """測試簡單的時間提取"""
    print(f"\n🔧 **簡單時間提取測試**")
    print("=" * 30)
    
    test_cases = [
        "我計劃中午12點開始行程，晚上10點結束",
        "早上8點開始，晚上8點結束",
        "我想要9點開始，18點結束",
        "7點開始，21點結束"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 測試: {test_input}")
        
        start_time = "09:00"
        end_time = "18:00"
        
        # 檢查開始時間
        if "中午12點" in test_input or "12點" in test_input:
            start_time = "12:00"
        elif "早上8點" in test_input or "8點" in test_input:
            start_time = "08:00"
        elif "9點" in test_input:
            start_time = "09:00"
        elif "7點" in test_input:
            start_time = "07:00"
        
        # 檢查結束時間
        if "晚上10點" in test_input or "10點結束" in test_input:
            end_time = "22:00"
        elif "晚上8點" in test_input or "8點結束" in test_input:
            end_time = "20:00"
        elif "18點" in test_input:
            end_time = "18:00"
        elif "21點" in test_input:
            end_time = "21:00"
        
        print(f"  解析結果: {start_time} - {end_time}")

if __name__ == "__main__":
    test_gemini_time_understanding()
    test_simple_time_extraction()
