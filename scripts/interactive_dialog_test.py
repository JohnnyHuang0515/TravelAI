#!/usr/bin/env python3
"""
互動式對話測試工具
讓使用者可以手動測試不同的對話場景
"""

import os
import sys
import asyncio
from datetime import datetime

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.application.graph import app_graph

class InteractiveDialogTester:
    """互動式對話測試器"""
    
    def __init__(self):
        self.session_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_count = 0
    
    def print_header(self):
        """顯示標題"""
        print("🎭 TravelAI 互動式對話測試工具")
        print("=" * 60)
        print("💡 提示: 輸入 'quit' 或 'exit' 結束測試")
        print("💡 提示: 輸入 'help' 查看幫助")
        print("💡 提示: 輸入 'scenarios' 查看範例對話")
        print("=" * 60)
    
    def print_help(self):
        """顯示幫助資訊"""
        print("\n📖 幫助資訊:")
        print("🚗 交通工具選項:")
        print("   - 開車/自駕/汽車")
        print("   - 大眾運輸/公車/火車/捷運")
        print("   - 混合/彈性/智能")
        print("   - 環保/綠色/低碳")
        print("\n🎯 興趣類型:")
        print("   - 美食、風景、文化、歷史")
        print("   - 溫泉、自然、生態")
        print("   - 親子、情侶、朋友")
        print("\n💰 預算選項:")
        print("   - 有限/學生/經濟")
        print("   - 中等/一般")
        print("   - 不限/豪華/高檔")
    
    def print_scenarios(self):
        """顯示範例對話"""
        print("\n📝 範例對話場景:")
        
        scenarios = [
            "我想去宜蘭開車旅遊2天，喜歡美食和溫泉",
            "宜蘭一日遊，搭公車，預算有限，喜歡文化景點",
            "我想去宜蘭，智能選擇交通方式，3天2夜",
            "宜蘭環保出行，2天，喜歡自然風景",
            "我想去宜蘭豪華遊，開車，預算不限，情侶旅行",
            "宜蘭親子遊，2天，開車，適合小孩的景點",
            "我想去宜蘭攝影，1天，混合交通，風景為主",
            "宜蘭美食之旅，3天，大眾運輸，深度體驗"
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"   {i}. {scenario}")
    
    async def test_user_input(self, user_input: str):
        """測試用戶輸入"""
        self.conversation_count += 1
        
        print(f"\n💬 對話 {self.conversation_count}: {user_input}")
        print("-" * 50)
        
        try:
            state = {
                "user_input": user_input,
                "session_id": self.session_id
            }
            
            result = await app_graph.ainvoke(state)
            
            # 顯示AI回應
            if "ai_response" in result:
                print(f"🤖 AI: {result['ai_response']}")
            
            # 顯示收集的資訊
            if "conversation_state" in result:
                conv_state = result["conversation_state"]
                if conv_state.collected_info:
                    print(f"📊 已收集資訊:")
                    for key, value in conv_state.collected_info.items():
                        print(f"   - {key}: {value}")
                
                print(f"🔄 對話輪次: {conv_state.turn_count}")
            
            # 顯示行程結果
            if "itinerary" in result:
                itinerary = result["itinerary"]
                print(f"\n✅ 行程生成完成!")
                print(f"📅 目的地: {itinerary.destination}")
                print(f"📅 天數: {itinerary.duration_days}")
                print(f"🚗 交通模式: {result.get('transport_mode', 'mixed')}")
                
                if itinerary.days:
                    day1 = itinerary.days[0]
                    print(f"📍 第一天行程 ({len(day1.visits)} 個景點):")
                    for j, visit in enumerate(day1.visits[:5], 1):  # 只顯示前5個
                        print(f"   {j}. {visit.place_name} ({visit.arrival_time} - {visit.departure_time})")
                    
                    if len(day1.visits) > 5:
                        print(f"   ... 還有 {len(day1.visits) - 5} 個景點")
            
            # 顯示錯誤
            if "error" in result:
                print(f"❌ 錯誤: {result['error']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 處理錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run(self):
        """運行互動式測試"""
        self.print_header()
        
        while True:
            try:
                user_input = input("\n💬 請輸入您的對話 (或輸入 'help'/'scenarios'/'quit'): ").strip()
                
                if not user_input:
                    print("❓ 請輸入一些內容")
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("\n👋 感謝使用對話測試工具!")
                    break
                
                if user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                if user_input.lower() == 'scenarios':
                    self.print_scenarios()
                    continue
                
                # 測試用戶輸入
                success = await self.test_user_input(user_input)
                
                if not success:
                    print("⚠️ 對話處理失敗，請重試")
                
            except KeyboardInterrupt:
                print("\n\n👋 使用者中斷，退出測試工具")
                break
            except Exception as e:
                print(f"❌ 發生未預期的錯誤: {e}")

async def quick_demo():
    """快速演示"""
    print("🎭 快速對話演示")
    print("=" * 40)
    
    demo_inputs = [
        "我想去宜蘭開車旅遊2天，喜歡美食",
        "宜蘭一日遊，搭公車，環保出行",
        "我想去宜蘭，智能選擇交通方式",
    ]
    
    tester = InteractiveDialogTester()
    
    for demo_input in demo_inputs:
        print(f"\n📝 演示: {demo_input}")
        print("-" * 30)
        print("🤖 AI會分析並收集:")
        print("   - 目的地: 宜蘭")
        print("   - 天數: 根據輸入")
        print("   - 交通工具: 根據偏好")
        print("   - 興趣: 根據描述")
        print("✅ 然後生成個性化行程")
    
    print("\n🎉 演示完成! 運行 'python3 scripts/interactive_dialog_test.py' 開始互動測試")

async def main():
    """主程式"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        await quick_demo()
    else:
        tester = InteractiveDialogTester()
        await tester.run()

if __name__ == "__main__":
    asyncio.run(main())
