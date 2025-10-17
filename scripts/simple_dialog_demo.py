#!/usr/bin/env python3
"""
簡化版對話演示
展示不同類型的用戶對話和系統回應模式
"""

import os
import sys
from datetime import datetime

def print_header():
    """顯示標題"""
    print("🎭 TravelAI 對話演示系統")
    print("=" * 60)
    print(f"⏰ 演示時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def demo_driving_conversations():
    """演示開車族對話"""
    print("\n🚗 開車族對話演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "我想去宜蘭開車旅遊3天，喜歡美食和溫泉",
            "ai": "太好了！您選擇開車到宜蘭3天，主要興趣是美食和溫泉。\n    開車確實很適合宜蘭的溫泉景點，可以靈活安排行程。\n    我會為您規劃包含礁溪溫泉、羅東夜市等景點的路線。",
            "collected": {
                "destination": "宜蘭",
                "duration": "3天",
                "transport_mode": "driving",
                "interests": ["美食", "溫泉"],
                "budget": "中等"
            }
        },
        {
            "user": "宜蘭2天1夜，自駕，預算中等，喜歡自然風景",
            "ai": "了解！2天1夜的自駕行程很適合宜蘭。\n    我會推薦太平山、五峰旗瀑布等自然景點，\n    並考慮您的中等預算安排住宿和餐飲。",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天1夜",
                "transport_mode": "driving",
                "interests": ["自然風景"],
                "budget": "中等"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def demo_public_transport_conversations():
    """演示大眾運輸對話"""
    print("\n🚌 大眾運輸對話演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "我想搭公車去宜蘭2天，預算有限，喜歡文化景點",
            "ai": "很好的選擇！搭公車到宜蘭既環保又經濟實惠。\n    我會推薦傳統藝術中心、蘭陽博物館等文化景點，\n    並安排經濟實惠的住宿和餐飲選擇。",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天",
                "transport_mode": "public_transport",
                "interests": ["文化景點"],
                "budget": "有限"
            }
        },
        {
            "user": "宜蘭一日遊，搭大眾運輸，環保出行",
            "ai": "環保出行很棒！我會為您規劃一個綠色旅遊行程，\n    優先使用公車和步行，選擇生態友善的景點，\n    並計算整個行程的碳排放量。",
            "collected": {
                "destination": "宜蘭",
                "duration": "1天",
                "transport_mode": "public_transport",
                "interests": ["環保"],
                "budget": "中等"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def demo_mixed_transport_conversations():
    """演示混合交通對話"""
    print("\n🔄 混合交通對話演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "我想去宜蘭3天，希望智能選擇最佳交通方式",
            "ai": "很棒的想法！智能交通規劃會根據景點距離和便利性\n    為您選擇最適合的交通方式。\n    距離較遠的景點建議開車，市區景點可以搭公車，短距離可以步行。",
            "collected": {
                "destination": "宜蘭",
                "duration": "3天",
                "transport_mode": "mixed",
                "interests": ["智能規劃"],
                "budget": "中等"
            }
        },
        {
            "user": "宜蘭2天，可以開車也可以搭公車，哪個方便就用哪個",
            "ai": "彈性交通規劃！我會根據每個景點的特點\n    為您推薦最適合的交通方式，\n    確保行程既方便又經濟實惠。",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天",
                "transport_mode": "mixed",
                "interests": ["彈性規劃"],
                "budget": "中等"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def demo_eco_friendly_conversations():
    """演示環保出行對話"""
    print("\n🌱 環保出行對話演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "我想環保出行到宜蘭2天，減少碳足跡",
            "ai": "非常棒的環保意識！我會為您規劃一個綠色旅遊行程，\n    優先使用大眾運輸和步行，選擇生態友善的景點，\n    並計算整個行程的碳排放量。",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天",
                "transport_mode": "eco_friendly",
                "interests": ["環保"],
                "budget": "中等"
            }
        },
        {
            "user": "宜蘭一日遊，綠色交通，生態旅遊",
            "ai": "生態旅遊很棒！我會推薦龜山島、冬山河等生態景點，\n    使用公車和步行減少環境影響，\n    並提供生態教育資訊。",
            "collected": {
                "destination": "宜蘭",
                "duration": "1天",
                "transport_mode": "eco_friendly",
                "interests": ["生態旅遊"],
                "budget": "中等"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def demo_special_interest_conversations():
    """演示特殊興趣對話"""
    print("\n🎯 特殊興趣對話演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "我想去宜蘭攝影，2天，開車，喜歡拍風景",
            "ai": "攝影愛好者！宜蘭有很多絕佳的攝影景點，\n    像是龜山島日出、五峰旗瀑布、太平山雲海等。\n    開車確實很方便攜帶攝影器材。",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天",
                "transport_mode": "driving",
                "interests": ["攝影", "風景"],
                "budget": "中等"
            }
        },
        {
            "user": "宜蘭美食之旅，3天，主要搭公車，預算不限",
            "ai": "美食之旅！宜蘭的美食真的很多，像是三星蔥油餅、\n    羅東夜市、礁溪溫泉蛋、鴨賞等。\n    搭公車可以深入當地，體驗最道地的美食。",
            "collected": {
                "destination": "宜蘭",
                "duration": "3天",
                "transport_mode": "public_transport",
                "interests": ["美食"],
                "budget": "不限"
            }
        },
        {
            "user": "宜蘭親子遊，2天，開車，適合小孩的景點",
            "ai": "親子旅遊！宜蘭有很多適合家庭的景點，\n    像是蘭陽博物館、傳統藝術中心、冬山河親水公園等。\n    開車很方便攜帶小孩用品。",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天",
                "transport_mode": "driving",
                "interests": ["親子"],
                "budget": "中等"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def demo_edge_cases():
    """演示邊界情況"""
    print("\n🔍 邊界情況處理演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "我想出去玩",
            "ai": "聽起來您想要放鬆一下！請問您想去哪裡呢？\n    我可以推薦一些不錯的旅遊目的地。\n    您比較喜歡山景、海景，還是城市景點呢？",
            "collected": {}
        },
        {
            "user": "宜蘭",
            "ai": "宜蘭是個很棒的地方！請問您計劃去幾天呢？\n    還有您比較喜歡什麼類型的景點？\n    像是溫泉、美食、自然風景，還是文化景點？",
            "collected": {"destination": "宜蘭"}
        },
        {
            "user": "我想去宜蘭1天，但要看很多景點",
            "ai": "我理解您想要充分利用時間！\n    不過1天確實比較有限，我建議：\n    1. 選擇2-3個精華景點深度遊\n    2. 或者考慮延長到2天\n    您覺得哪個方案比較適合呢？",
            "collected": {
                "destination": "宜蘭",
                "duration": "1天"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def demo_multilingual():
    """演示多語言對話"""
    print("\n🌍 多語言對話演示")
    print("-" * 40)
    
    scenarios = [
        {
            "user": "I want to go to 宜蘭 for 2 days, 喜歡 nature",
            "ai": "Great! 2 days in 宜蘭 for nature lovers!\n    宜蘭有很多很棒的自然景點，\n    像是太平山、五峰旗瀑布、龜山島等。\n    Would you like to drive or take public transport?",
            "collected": {
                "destination": "宜蘭",
                "duration": "2天",
                "interests": ["自然風景"]
            }
        },
        {
            "user": "宜蘭旅遊 3 days, budget medium, 開車 or 公車都可以",
            "ai": "了解！3天的宜蘭旅遊，預算中等。\n    既然您對交通方式很彈性，\n    我會為您智能選擇最佳的交通方式，\n    平衡便利性和經濟性。",
            "collected": {
                "destination": "宜蘭",
                "duration": "3天",
                "budget": "中等",
                "transport_mode": "mixed"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 場景 {i}:")
        print(f"👤 用戶: {scenario['user']}")
        print(f"🤖 AI: {scenario['ai']}")
        print(f"📊 收集資訊: {scenario['collected']}")

def print_summary():
    """顯示總結"""
    print(f"\n{'='*60}")
    print("📊 對話演示總結")
    print(f"{'='*60}")
    print("✅ 開車族對話 - 展示完整資訊收集和個性化回應")
    print("✅ 大眾運輸對話 - 展示環保和經濟考量")
    print("✅ 混合交通對話 - 展示智能交通選擇")
    print("✅ 環保出行對話 - 展示綠色旅遊理念")
    print("✅ 特殊興趣對話 - 展示專業旅遊規劃")
    print("✅ 邊界情況處理 - 展示系統韌性")
    print("✅ 多語言對話 - 展示國際化支援")
    print(f"\n🎯 系統特色:")
    print("   🧠 智能理解用戶意圖")
    print("   🚗 整合多種交通方式")
    print("   💬 自然語言對話")
    print("   🎨 個性化行程規劃")
    print("   🌱 環保旅遊選項")
    print(f"\n🚀 準備就緒！系統可以處理各種複雜的對話場景。")

def main():
    """主程式"""
    print_header()
    
    # 演示各種對話場景
    demo_driving_conversations()
    demo_public_transport_conversations()
    demo_mixed_transport_conversations()
    demo_eco_friendly_conversations()
    demo_special_interest_conversations()
    demo_edge_cases()
    demo_multilingual()
    
    print_summary()

if __name__ == "__main__":
    main()
