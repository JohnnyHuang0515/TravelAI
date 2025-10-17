#!/usr/bin/env python3
"""
對話場景測試腳本
測試不同類型的用戶對話和交通工具偏好
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.application.graph import app_graph
from src.itinerary_planner.domain.entities.conversation_state import ConversationState, ConversationStateType

class ConversationTester:
    """對話測試器"""
    
    def __init__(self):
        self.session_counter = 1
    
    def create_session_id(self):
        """創建會話ID"""
        session_id = f"test_session_{self.session_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_counter += 1
        return session_id
    
    async def test_conversation(self, scenario_name: str, user_messages: list):
        """測試對話場景"""
        print(f"\n{'='*80}")
        print(f"🎭 測試場景: {scenario_name}")
        print(f"{'='*80}")
        
        session_id = self.create_session_id()
        
        for i, message in enumerate(user_messages):
            print(f"\n📝 用戶訊息 {i+1}: {message}")
            print("-" * 60)
            
            # 建立狀態
            state = {
                "user_input": message,
                "session_id": session_id
            }
            
            try:
                # 執行圖形
                result = await app_graph.ainvoke(state)
                
                # 顯示結果
                if "ai_response" in result:
                    print(f"🤖 AI 回應: {result['ai_response']}")
                
                if "error" in result:
                    print(f"❌ 錯誤: {result['error']}")
                
                if "conversation_state" in result:
                    conv_state = result["conversation_state"]
                    print(f"📊 收集的資訊: {conv_state.collected_info}")
                    print(f"🔄 對話輪次: {conv_state.turn_count}")
                
                if "itinerary" in result:
                    itinerary = result["itinerary"]
                    print(f"✅ 行程生成完成!")
                    print(f"📅 天數: {itinerary.duration_days}")
                    print(f"🎯 目的地: {itinerary.destination}")
                    print(f"🚗 交通模式: {result.get('transport_mode', 'mixed')}")
                    
                    if itinerary.days:
                        day1 = itinerary.days[0]
                        print(f"📍 第一天景點數: {len(day1.visits)}")
                        for visit in day1.visits[:3]:
                            print(f"   - {visit.place_name} ({visit.arrival_time} - {visit.departure_time})")
                
                print(f"✅ 場景 {scenario_name} 完成")
                
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
                import traceback
                traceback.print_exc()
    
    async def run_all_scenarios(self):
        """執行所有測試場景"""
        print("🚀 開始對話場景測試")
        print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 場景1: 開車族完整對話
        await self.test_conversation(
            "開車族完整對話",
            [
                "我想去宜蘭旅遊",
                "3天2夜",
                "我喜歡美食和自然風景",
                "預算中等",
                "開車去，因為比較方便"
            ]
        )
        
        # 場景2: 大眾運輸環保族
        await self.test_conversation(
            "大眾運輸環保族",
            [
                "我想去宜蘭2天，喜歡文化景點，預算有限，我想搭大眾運輸，比較環保"
            ]
        )
        
        # 場景3: 混合模式彈性族
        await self.test_conversation(
            "混合模式彈性族",
            [
                "宜蘭一日遊",
                "美食為主",
                "混合交通，希望智能選擇最佳方式"
            ]
        )
        
        # 場景4: 親子家庭
        await self.test_conversation(
            "親子家庭",
            [
                "我們一家四口想去宜蘭玩2天",
                "有小孩，希望景點適合親子",
                "開車比較方便帶小孩"
            ]
        )
        
        # 場景5: 背包客
        await self.test_conversation(
            "背包客",
            [
                "我是背包客，想去宜蘭3天",
                "預算很有限",
                "主要靠大眾運輸和步行"
            ]
        )
        
        # 場景6: 多輪詳細對話
        await self.test_conversation(
            "多輪詳細對話",
            [
                "我想規劃宜蘭旅遊",
                "大概2天1夜",
                "我對溫泉很有興趣",
                "還有美食",
                "預算算中等吧",
                "我是開車去的",
                "還有什麼需要知道的嗎？"
            ]
        )
        
        # 場景7: 快速完整輸入
        await self.test_conversation(
            "快速完整輸入",
            [
                "我想去宜蘭3天2夜，喜歡自然風景和溫泉，預算高，開車，適合情侶的景點"
            ]
        )
        
        # 場景8: 環保出行
        await self.test_conversation(
            "環保出行",
            [
                "我想環保出行到宜蘭2天",
                "喜歡生態旅遊",
                "希望減少碳排放"
            ]
        )
        
        print(f"\n{'='*80}")
        print("🎉 所有對話場景測試完成!")
        print(f"{'='*80}")

async def test_specific_scenario():
    """測試特定場景"""
    print("🎯 測試特定對話場景")
    
    tester = ConversationTester()
    
    # 測試一個複雜的對話場景
    await tester.test_conversation(
        "複雜混合對話",
        [
            "你好，我想規劃宜蘭旅遊",
            "大概是3天2夜",
            "我們是情侶，喜歡浪漫的景點",
            "預算算是中等偏高",
            "我想開車，但也可以考慮其他交通方式",
            "主要是想放鬆，不要太趕",
            "有什麼建議嗎？"
        ]
    )

async def test_transport_preferences():
    """測試不同交通工具偏好"""
    print("🚗 測試交通工具偏好對話")
    
    tester = ConversationTester()
    
    transport_scenarios = [
        {
            "name": "開車偏好",
            "messages": [
                "宜蘭2天遊，開車去，喜歡自由行"
            ]
        },
        {
            "name": "大眾運輸偏好", 
            "messages": [
                "宜蘭1天遊，搭公車，經濟實惠"
            ]
        },
        {
            "name": "混合模式",
            "messages": [
                "宜蘭3天，智能選擇交通方式"
            ]
        },
        {
            "name": "環保出行",
            "messages": [
                "宜蘭2天，環保出行，減少碳足跡"
            ]
        }
    ]
    
    for scenario in transport_scenarios:
        await tester.test_conversation(scenario["name"], scenario["messages"])

async def test_edge_cases():
    """測試邊界情況"""
    print("🔍 測試邊界情況")
    
    tester = ConversationTester()
    
    edge_cases = [
        {
            "name": "最少資訊",
            "messages": ["宜蘭"]
        },
        {
            "name": "模糊表達",
            "messages": [
                "我想出去玩",
                "大概幾天都可以",
                "隨便什麼交通方式"
            ]
        },
        {
            "name": "矛盾資訊",
            "messages": [
                "我想去宜蘭1天，但要看很多景點",
                "預算很少，但要住豪華飯店",
                "不想開車，但要到很遠的地方"
            ]
        },
        {
            "name": "多語言混合",
            "messages": [
                "I want to go to 宜蘭 for 2 days",
                "我喜歡 nature 和美食",
                "Budget 是 medium"
            ]
        }
    ]
    
    for case in edge_cases:
        await tester.test_conversation(case["name"], case["messages"])

async def main():
    """主程式"""
    print("🎭 TravelAI 對話場景測試系統")
    print("=" * 80)
    
    try:
        # 測試所有場景
        tester = ConversationTester()
        await tester.run_all_scenarios()
        
        # 測試特定場景
        await test_specific_scenario()
        
        # 測試交通工具偏好
        await test_transport_preferences()
        
        # 測試邊界情況
        await test_edge_cases()
        
        print("\n🎉 所有測試完成!")
        print("📊 測試總結:")
        print("✅ 開車族對話測試")
        print("✅ 大眾運輸對話測試") 
        print("✅ 混合模式對話測試")
        print("✅ 親子家庭對話測試")
        print("✅ 背包客對話測試")
        print("✅ 環保出行對話測試")
        print("✅ 邊界情況測試")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
