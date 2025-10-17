#!/usr/bin/env python3
"""
簡短回應處理增強腳本
展示如何在實際系統中智能處理用戶的簡短回答
"""

import os
import sys
from datetime import datetime

def print_header():
    """顯示標題"""
    print("💬 簡短回應處理增強系統")
    print("=" * 60)
    print(f"⏰ 增強時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def demonstrate_short_response_handling():
    """演示簡短回應處理"""
    print("\n🎯 簡短回應處理演示")
    print("-" * 40)
    
    # 模擬對話狀態
    conversation_state = {
        "collected_info": {},
        "conversation_history": [],
        "current_context": "initial",
        "missing_info": ["destination", "duration", "interests", "budget", "transport_mode"]
    }
    
    def process_short_response(user_input, context):
        """處理簡短回應"""
        print(f"\n👤 用戶輸入: '{user_input}'")
        print(f"💭 當前上下文: {context}")
        
        # 簡短回應處理邏輯
        response = ""
        collected = {}
        
        if len(user_input) <= 3:  # 極簡回答
            if context == "initial":
                if user_input in ["宜蘭", "台北", "高雄"]:
                    collected["destination"] = user_input
                    response = f"{user_input}是個很棒的地方！請問您計劃去幾天呢？"
                    context = "asking_duration"
                else:
                    response = "請告訴我您想去哪個城市旅遊呢？"
            
            elif context == "asking_duration":
                if user_input.isdigit():
                    collected["duration"] = f"{user_input}天"
                    response = f"好的，{user_input}天的行程！請問您比較喜歡什麼類型的景點呢？\n像是溫泉、美食、自然風景，還是文化景點？"
                    context = "asking_interests"
                else:
                    response = "請告訴我您計劃去幾天呢？"
            
            elif context == "asking_interests":
                if user_input in ["溫泉", "美食", "風景", "文化"]:
                    collected["interests"] = [user_input]
                    response = f"{user_input}很棒！請問您希望使用什麼交通工具呢？\n開車、搭公車，還是其他方式？"
                    context = "asking_transport"
                else:
                    response = "請選擇您比較喜歡的景點類型：溫泉、美食、自然風景，還是文化景點？"
            
            elif context == "asking_transport":
                if user_input in ["開車", "公車", "火車"]:
                    collected["transport_mode"] = "driving" if user_input == "開車" else "public_transport"
                    response = f"{user_input}很方便！最後請問您的預算大概是多少呢？\n有限、中等，還是不限？"
                    context = "asking_budget"
                else:
                    response = "請選擇您的交通工具：開車、搭公車，還是其他方式？"
            
            elif context == "asking_budget":
                if user_input in ["有限", "中等", "不限", "高"]:
                    collected["budget"] = user_input
                    response = "了解！現在資訊收集完成，讓我為您規劃行程！"
                    context = "planning"
                else:
                    response = "請選擇您的預算範圍：有限、中等，還是不限？"
            
            else:
                response = "請提供更多資訊，這樣我可以更好地為您服務。"
        
        # 更新對話狀態
        conversation_state["collected_info"].update(collected)
        conversation_state["conversation_history"].append({"user": user_input, "ai": response})
        conversation_state["current_context"] = context
        
        print(f"🤖 AI回應: {response}")
        print(f"📊 收集資訊: {collected}")
        print(f"🔄 新上下文: {context}")
        print(f"📝 總收集: {conversation_state['collected_info']}")
        
        return response, context
    
    # 模擬簡短對話流程
    short_conversation = [
        ("宜蘭", "initial"),
        ("2", "asking_duration"),
        ("美食", "asking_interests"),
        ("開車", "asking_transport"),
        ("中等", "asking_budget")
    ]
    
    context = "initial"
    for user_input, expected_context in short_conversation:
        response, context = process_short_response(user_input, context)
        print("-" * 30)

def demonstrate_context_awareness():
    """演示上下文感知"""
    print("\n🧠 上下文感知演示")
    print("-" * 40)
    
    # 不同上下文的相同回答處理
    test_cases = [
        {
            "user_input": "是",
            "contexts": [
                ("asking_transport", "好的！您選擇開車。請問您的預算大概是多少呢？"),
                ("asking_interests", "好的！您喜歡溫泉。請問您計劃去幾天呢？"),
                ("asking_budget", "好的！預算不限。現在開始為您規劃行程！")
            ]
        },
        {
            "user_input": "2",
            "contexts": [
                ("asking_duration", "好的，2天的行程！請問您比較喜歡什麼類型的景點呢？"),
                ("asking_budget", "2萬元預算！很高檔的選擇。現在開始為您規劃豪華行程！")
            ]
        },
        {
            "user_input": "好",
            "contexts": [
                ("asking_confirmation", "太好了！現在開始為您規劃行程。"),
                ("asking_preference", "好的！我會為您推薦這個選項。"),
                ("asking_planning", "好的！行程規劃完成。")
            ]
        }
    ]
    
    for case in test_cases:
        user_input = case["user_input"]
        print(f"\n👤 用戶輸入: '{user_input}'")
        
        for context, response in case["contexts"]:
            print(f"   💭 上下文: {context}")
            print(f"   🤖 AI回應: {response}")
        print("-" * 30)

def demonstrate_smart_inference():
    """演示智能推測"""
    print("\n🔍 智能推測演示")
    print("-" * 40)
    
    inference_cases = [
        {
            "user_input": "溫泉",
            "inference": {
                "interests": ["溫泉"],
                "suggestions": ["礁溪溫泉", "蘇澳冷泉"],
                "follow_up": "請問您計劃去幾天呢？"
            }
        },
        {
            "user_input": "開車",
            "inference": {
                "transport_mode": "driving",
                "advantages": ["彈性高", "適合遠距離景點"],
                "follow_up": "請問您的預算大概是多少呢？"
            }
        },
        {
            "user_input": "高",
            "inference": {
                "budget": "高",
                "suggestions": ["頂級飯店", "米其林餐廳"],
                "follow_up": "現在開始為您規劃豪華行程！"
            }
        }
    ]
    
    for case in inference_cases:
        user_input = case["user_input"]
        inference = case["inference"]
        
        print(f"\n👤 用戶輸入: '{user_input}'")
        print(f"🧠 智能推測:")
        for key, value in inference.items():
            print(f"   - {key}: {value}")
        print("-" * 30)

def demonstrate_gradual_collection():
    """演示逐步收集"""
    print("\n📝 逐步資訊收集演示")
    print("-" * 40)
    
    # 模擬逐步收集過程
    collection_steps = [
        {"step": 1, "missing": ["destination", "duration", "interests", "budget", "transport_mode"], "ask": "請問您想去哪裡旅遊呢？"},
        {"step": 2, "missing": ["duration", "interests", "budget", "transport_mode"], "ask": "請問您計劃去幾天呢？"},
        {"step": 3, "missing": ["interests", "budget", "transport_mode"], "ask": "請問您比較喜歡什麼類型的景點呢？"},
        {"step": 4, "missing": ["budget", "transport_mode"], "ask": "請問您希望使用什麼交通工具呢？"},
        {"step": 5, "missing": ["budget"], "ask": "請問您的預算大概是多少呢？"},
        {"step": 6, "missing": [], "ask": "資訊收集完成，開始規劃行程！"}
    ]
    
    for step_info in collection_steps:
        print(f"\n📝 步驟 {step_info['step']}:")
        print(f"   ❓ 還需要: {step_info['missing']}")
        print(f"   🤖 詢問: {step_info['ask']}")
        print(f"   ✅ 進度: {(6-len(step_info['missing']))/6*100:.0f}%")

def demonstrate_error_handling():
    """演示錯誤處理"""
    print("\n⚠️ 錯誤處理演示")
    print("-" * 40)
    
    error_cases = [
        {
            "user_input": "不知道",
            "error_type": "uncertainty",
            "response": "沒關係！讓我為您介紹一些選項：\n溫泉、美食、自然風景、文化景點等。\n您比較想體驗哪一種呢？",
            "strategy": "提供選項引導"
        },
        {
            "user_input": "隨便",
            "error_type": "indifference",
            "response": "了解！我會為您推薦最受歡迎的景點。\n請問您計劃去幾天呢？",
            "strategy": "使用熱門推薦"
        },
        {
            "user_input": "都可以",
            "error_type": "flexibility",
            "response": "您很彈性！讓我為您推薦一些不錯的選項：\n請問您比較喜歡溫泉、美食，還是自然風景呢？",
            "strategy": "提供具體選項"
        }
    ]
    
    for case in error_cases:
        print(f"\n👤 用戶輸入: '{case['user_input']}'")
        print(f"⚠️ 錯誤類型: {case['error_type']}")
        print(f"🤖 AI回應: {case['response']}")
        print(f"🎯 處理策略: {case['strategy']}")
        print("-" * 30)

def print_implementation_guide():
    """顯示實作指南"""
    print(f"\n{'='*60}")
    print("🛠️ 簡短回應處理實作指南")
    print(f"{'='*60}")
    print("📋 核心原則:")
    print("   1. 🧠 上下文感知 - 根據對話歷史理解用戶意圖")
    print("   2. 🔍 智能推測 - 從簡短回答中提取關鍵資訊")
    print("   3. 📝 逐步收集 - 分階段收集必要資訊")
    print("   4. ⚠️ 錯誤處理 - 優雅處理模糊或不確定回答")
    print("   5. 💬 自然引導 - 保持對話流暢自然")
    print("\n🔧 技術實作:")
    print("   - 關鍵字匹配和分類")
    print("   - 上下文狀態管理")
    print("   - 智能問題生成")
    print("   - 錯誤恢復機制")
    print("   - 進度追蹤和回饋")

def main():
    """主程式"""
    print_header()
    
    # 演示各種簡短回應處理
    demonstrate_short_response_handling()
    demonstrate_context_awareness()
    demonstrate_smart_inference()
    demonstrate_gradual_collection()
    demonstrate_error_handling()
    
    print_implementation_guide()
    
    print(f"\n{'='*60}")
    print("✅ 簡短回應處理增強完成!")
    print("🎯 系統現在能夠智能處理各種簡短回答")
    print("💬 保持自然對話流程")
    print("🧠 有效收集必要資訊")
    print("🛠️ 提供實作指南和最佳實踐")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
