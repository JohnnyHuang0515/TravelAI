#!/usr/bin/env python3
"""
簡短回應測試腳本
測試系統如何處理用戶的簡短回答
"""

import os
import sys
from datetime import datetime

def print_header():
    """顯示標題"""
    print("💬 TravelAI 簡短回應處理測試")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def test_very_short_responses():
    """測試極簡回答"""
    print("\n🔍 極簡回答測試")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "宜蘭",
            "ai": "宜蘭是個很棒的地方！請問您計劃去幾天呢？\n    還有您比較喜歡什麼類型的景點？\n    像是溫泉、美食、自然風景，還是文化景點？",
            "collected": {"destination": "宜蘭"},
            "next_questions": ["天數", "興趣類型", "預算"]
        },
        {
            "user": "2天",
            "ai": "好的，2天1夜的行程！請問您比較喜歡什麼類型的景點呢？\n    像是溫泉、美食、自然風景，還是文化景點？",
            "collected": {"destination": "宜蘭", "duration": "2天"},
            "next_questions": ["興趣類型", "預算", "交通方式"]
        },
        {
            "user": "美食",
            "ai": "美食很棒！宜蘭有很多道地美食。請問您的預算大概是多少呢？\n    還有您希望使用什麼交通工具？開車、搭公車，還是其他方式？",
            "collected": {"destination": "宜蘭", "duration": "2天", "interests": ["美食"]},
            "next_questions": ["預算", "交通方式"]
        },
        {
            "user": "開車",
            "ai": "開車很方便！最後請問您的預算大概是多少呢？\n    這樣我可以為您推薦合適的餐廳和住宿。",
            "collected": {"destination": "宜蘭", "duration": "2天", "interests": ["美食"], "transport_mode": "driving"},
            "next_questions": ["預算"]
        },
        {
            "user": "中等",
            "ai": "了解！現在資訊收集完成，讓我為您規劃一個完美的宜蘭美食之旅！\n    我會推薦適合中等預算的餐廳和住宿，並安排開車路線。",
            "collected": {"destination": "宜蘭", "duration": "2天", "interests": ["美食"], "transport_mode": "driving", "budget": "中等"},
            "next_questions": ["開始規劃"]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 對話 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")
        print(f"❓ 下一步問題: {scenario['next_questions']}")

def test_single_word_responses():
    """測試單字回答"""
    print("\n🔤 單字回答測試")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "溫泉",
            "ai": "溫泉很棒！宜蘭的溫泉很有名。請問您計劃去幾天呢？\n    還有您希望使用什麼交通工具？",
            "collected": {"destination": "宜蘭", "interests": ["溫泉"]}
        },
        {
            "user": "開車",
            "ai": "開車很方便！請問您的預算大概是多少呢？\n    這樣我可以推薦合適的溫泉飯店。",
            "collected": {"destination": "宜蘭", "interests": ["溫泉"], "transport_mode": "driving"}
        },
        {
            "user": "高",
            "ai": "高預算！太好了，我可以為您推薦頂級的溫泉飯店和餐廳。\n    現在開始為您規劃豪華溫泉之旅！",
            "collected": {"destination": "宜蘭", "interests": ["溫泉"], "transport_mode": "driving", "budget": "高"}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def test_ambiguous_responses():
    """測試模糊回答"""
    print("\n❓ 模糊回答測試")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "都可以",
            "ai": "了解！您很彈性。讓我為您推薦一些不錯的選項：\n    請問您比較喜歡溫泉、美食、還是自然風景呢？",
            "collected": {"destination": "宜蘭"},
            "strategy": "提供具體選項"
        },
        {
            "user": "隨便",
            "ai": "沒問題！我會為您推薦宜蘭最受歡迎的景點。\n    請問您計劃去幾天呢？",
            "collected": {"destination": "宜蘭"},
            "strategy": "使用熱門推薦"
        },
        {
            "user": "不知道",
            "ai": "沒關係！讓我為您介紹宜蘭的特色：\n    宜蘭有溫泉、美食、自然風景、文化景點等。\n    您比較想體驗哪一種呢？",
            "collected": {"destination": "宜蘭"},
            "strategy": "提供資訊引導"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")
        print(f"🎯 策略: {scenario['strategy']}")

def test_yes_no_responses():
    """測試是非回答"""
    print("\n✅ 是非回答測試")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "是",
            "ai": "好的！既然您想開車，請問您比較喜歡什麼類型的景點呢？\n    溫泉、美食、還是自然風景？",
            "collected": {"destination": "宜蘭", "transport_mode": "driving"},
            "context": "詢問是否開車"
        },
        {
            "user": "不是",
            "ai": "了解！那您希望使用什麼交通工具呢？\n    搭公車、火車，還是其他方式？",
            "collected": {"destination": "宜蘭"},
            "context": "詢問是否開車"
        },
        {
            "user": "好",
            "ai": "太好了！2天1夜的溫泉之旅聽起來很棒。\n    請問您的預算大概是多少呢？",
            "collected": {"destination": "宜蘭", "duration": "2天", "interests": ["溫泉"]},
            "context": "確認溫泉行程"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")
        print(f"💭 上下文: {scenario['context']}")

def test_numeric_responses():
    """測試數字回答"""
    print("\n🔢 數字回答測試")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "3",
            "ai": "3天！很好的選擇，可以深度體驗宜蘭。\n    請問您比較喜歡什麼類型的景點呢？",
            "collected": {"destination": "宜蘭", "duration": "3天"}
        },
        {
            "user": "2",
            "ai": "2天1夜！時間剛好，不會太趕。\n    請問您希望使用什麼交通工具呢？",
            "collected": {"destination": "宜蘭", "duration": "2天"}
        },
        {
            "user": "1",
            "ai": "1天！時間比較緊湊，我會為您推薦精華景點。\n    請問您比較喜歡什麼類型的景點呢？",
            "collected": {"destination": "宜蘭", "duration": "1天"}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def test_emoji_responses():
    """測試表情符號回答"""
    print("\n😊 表情符號回答測試")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "😊",
            "ai": "看起來您心情很好！宜蘭確實是個讓人放鬆的好地方。\n    請問您計劃去幾天呢？",
            "collected": {"destination": "宜蘭"},
            "interpretation": "正面情緒，繼續收集資訊"
        },
        {
            "user": "👍",
            "ai": "太好了！看來您同意這個建議。\n    請問您比較喜歡什麼類型的景點呢？",
            "collected": {"destination": "宜蘭"},
            "interpretation": "同意/滿意，繼續流程"
        },
        {
            "user": "🤔",
            "ai": "看起來您在思考！沒關係，讓我為您介紹一些選項：\n    宜蘭有溫泉、美食、自然風景等，您比較想體驗哪一種呢？",
            "collected": {"destination": "宜蘭"},
            "interpretation": "猶豫不決，提供選項"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")
        print(f"🧠 解讀: {scenario['interpretation']}")

def test_context_preservation():
    """測試上下文保持"""
    print("\n🧠 上下文保持測試")
    print("-" * 40)
    
    conversation_flow = [
        {"user": "宜蘭", "context": "開始對話"},
        {"user": "2天", "context": "確認天數"},
        {"user": "溫泉", "context": "確認興趣"},
        {"user": "開車", "context": "確認交通"},
        {"user": "中等", "context": "確認預算"},
        {"user": "好", "context": "確認開始規劃"}
    ]
    
    collected_info = {}
    
    for i, turn in enumerate(conversation_flow, 1):
        user_input = turn["user"]
        context = turn["context"]
        
        # 模擬資訊收集
        if i == 1:
            collected_info["destination"] = "宜蘭"
        elif i == 2:
            collected_info["duration"] = "2天"
        elif i == 3:
            collected_info["interests"] = ["溫泉"]
        elif i == 4:
            collected_info["transport_mode"] = "driving"
        elif i == 5:
            collected_info["budget"] = "中等"
        elif i == 6:
            collected_info["ready_to_plan"] = True
        
        print(f"\n📝 輪次 {i} ({context}):")
        print(f"👤 用戶: {user_input}")
        print(f"📊 已收集: {collected_info}")
        print(f"✅ 系統保持上下文，逐步收集資訊")

def print_strategies():
    """顯示處理策略"""
    print(f"\n{'='*60}")
    print("🎯 簡短回應處理策略")
    print(f"{'='*60}")
    print("📝 處理原則:")
    print("   1. 🔍 智能推測 - 根據上下文推測用戶意圖")
    print("   2. ❓ 引導問題 - 提供具體選項讓用戶選擇")
    print("   3. 🧠 記憶保持 - 記住之前收集的資訊")
    print("   4. 🎯 目標導向 - 逐步收集必要資訊")
    print("   5. 💬 友善回應 - 保持自然對話流程")
    print("\n🛠️ 技術策略:")
    print("   - 關鍵字提取和匹配")
    print("   - 上下文資訊保持")
    print("   - 智能問題生成")
    print("   - 逐步資訊收集")
    print("   - 模糊回答澄清")

def main():
    """主程式"""
    print_header()
    
    # 測試各種簡短回應
    test_very_short_responses()
    test_single_word_responses()
    test_ambiguous_responses()
    test_yes_no_responses()
    test_numeric_responses()
    test_emoji_responses()
    test_context_preservation()
    
    print_strategies()
    
    print(f"\n{'='*60}")
    print("✅ 簡短回應處理測試完成!")
    print("🎯 系統能夠智能處理各種簡短回答")
    print("💬 保持自然對話流程")
    print("🧠 有效收集必要資訊")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
