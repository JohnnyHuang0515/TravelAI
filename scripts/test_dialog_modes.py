#!/usr/bin/env python3
"""
對話模式測試腳本
快速測試不同的用戶對話模式和交通工具偏好
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.application.graph import app_graph

async def test_single_conversation(user_input: str, scenario_name: str = "測試對話"):
    """測試單次對話"""
    print(f"\n{'='*60}")
    print(f"🎭 {scenario_name}")
    print(f"💬 用戶: {user_input}")
    print("-" * 60)
    
    session_id = f"test_{datetime.now().strftime('%H%M%S')}"
    
    try:
        state = {
            "user_input": user_input,
            "session_id": session_id
        }
        
        result = await app_graph.ainvoke(state)
        
        if "ai_response" in result:
            print(f"🤖 AI: {result['ai_response']}")
        
        if "conversation_state" in result:
            conv_state = result["conversation_state"]
            if conv_state.collected_info:
                print(f"📊 已收集資訊: {conv_state.collected_info}")
        
        if "itinerary" in result:
            itinerary = result["itinerary"]
            print(f"✅ 行程生成成功!")
            print(f"   📅 {itinerary.destination} {itinerary.duration_days}天")
            print(f"   🚗 交通: {result.get('transport_mode', 'mixed')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

async def test_driving_scenarios():
    """測試開車族對話"""
    print("\n🚗 開車族對話測試")
    
    scenarios = [
        "我想去宜蘭開車旅遊3天，喜歡美食和溫泉",
        "宜蘭2天1夜，自駕，預算中等，喜歡自然風景",
        "我想開車去宜蘭玩，有什麼推薦的景點嗎？",
        "宜蘭一日遊，開車，主要想泡溫泉和吃美食",
        "我開車去宜蘭，希望規劃一個輕鬆的行程"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"開車族 {i}")

async def test_public_transport_scenarios():
    """測試大眾運輸對話"""
    print("\n🚌 大眾運輸對話測試")
    
    scenarios = [
        "我想搭公車去宜蘭2天，預算有限，喜歡文化景點",
        "宜蘭一日遊，搭大眾運輸，環保出行",
        "我想坐公車去宜蘭玩，有什麼路線建議嗎？",
        "宜蘭3天2夜，大眾運輸，學生預算",
        "我想體驗宜蘭的在地交通，搭公車深度遊"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"大眾運輸 {i}")

async def test_mixed_transport_scenarios():
    """測試混合交通對話"""
    print("\n🔄 混合交通對話測試")
    
    scenarios = [
        "宜蘭2天，希望智能選擇最佳交通方式",
        "我想去宜蘭旅遊，可以開車也可以搭公車，哪個方便就用哪個",
        "宜蘭3天，混合交通，彈性規劃",
        "我想去宜蘭，交通方式不限，希望行程最優化",
        "宜蘭一日遊，智能交通規劃，效率優先"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"混合交通 {i}")

async def test_eco_friendly_scenarios():
    """測試環保出行對話"""
    print("\n🌱 環保出行對話測試")
    
    scenarios = [
        "我想環保出行到宜蘭2天，減少碳足跡",
        "宜蘭一日遊，綠色交通，生態旅遊",
        "我想低碳旅遊去宜蘭，有什麼建議？",
        "宜蘭3天，環保出行，喜歡自然景點",
        "我想綠色旅遊去宜蘭，大眾運輸優先"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"環保出行 {i}")

async def test_special_interest_scenarios():
    """測試特殊興趣對話"""
    print("\n🎯 特殊興趣對話測試")
    
    scenarios = [
        "我想去宜蘭攝影，2天，開車，喜歡拍風景",
        "宜蘭美食之旅，3天，主要搭公車，預算不限",
        "我想去宜蘭泡溫泉，1天，混合交通",
        "宜蘭親子遊，2天，開車，適合小孩的景點",
        "我想去宜蘭體驗文化，3天，大眾運輸，深度旅遊"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"特殊興趣 {i}")

async def test_budget_scenarios():
    """測試不同預算對話"""
    print("\n💰 預算對話測試")
    
    scenarios = [
        "我想去宜蘭旅遊，預算很有限，學生族",
        "宜蘭2天，預算中等，開車，希望物超所值",
        "我想豪華遊宜蘭3天，預算不限，開車",
        "宜蘭一日遊，預算有限，大眾運輸",
        "我想去宜蘭，預算中等偏高，混合交通"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"預算 {i}")

async def test_duration_scenarios():
    """測試不同天數對話"""
    print("\n📅 天數對話測試")
    
    scenarios = [
        "我想去宜蘭半日遊，開車",
        "宜蘭一日遊，大眾運輸，美食為主",
        "宜蘭2天1夜，混合交通，放鬆行程",
        "我想去宜蘭深度遊5天，開車，文化景點",
        "宜蘭週末遊，2天，環保出行"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"天數 {i}")

async def test_edge_case_scenarios():
    """測試邊界情況"""
    print("\n🔍 邊界情況測試")
    
    scenarios = [
        "宜蘭",
        "我想出去玩",
        "旅遊",
        "我",
        "Help",
        "我不知道要去哪裡",
        "隨便",
        "都可以",
        "不知道",
        "什麼都好"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"邊界 {i}")

async def test_multilingual_scenarios():
    """測試多語言對話"""
    print("\n🌍 多語言對話測試")
    
    scenarios = [
        "I want to go to 宜蘭 for 2 days",
        "我想去宜蘭 2 days, 喜歡 nature",
        "宜蘭旅遊 3 days, budget medium",
        "我想去 宜蘭, like food and hot spring",
        "宜蘭 1 day trip, 開車 or 公車都可以"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        await test_single_conversation(scenario, f"多語言 {i}")

async def main():
    """主程式"""
    print("🎭 TravelAI 對話模式測試")
    print("=" * 60)
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 測試各種對話模式
        await test_driving_scenarios()
        await test_public_transport_scenarios()
        await test_mixed_transport_scenarios()
        await test_eco_friendly_scenarios()
        await test_special_interest_scenarios()
        await test_budget_scenarios()
        await test_duration_scenarios()
        await test_edge_case_scenarios()
        await test_multilingual_scenarios()
        
        print(f"\n{'='*60}")
        print("🎉 所有對話模式測試完成!")
        print("📊 測試總結:")
        print("✅ 開車族對話 (5種)")
        print("✅ 大眾運輸對話 (5種)")
        print("✅ 混合交通對話 (5種)")
        print("✅ 環保出行對話 (5種)")
        print("✅ 特殊興趣對話 (5種)")
        print("✅ 預算對話 (5種)")
        print("✅ 天數對話 (5種)")
        print("✅ 邊界情況 (10種)")
        print("✅ 多語言對話 (5種)")
        print(f"📈 總計測試: 50種對話模式")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
