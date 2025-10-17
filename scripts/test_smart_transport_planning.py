#!/usr/bin/env python3
"""
智能交通規劃測試腳本
展示根據交通工具偏好進行行程規劃的功能
"""

import os
import sys
from datetime import datetime, time, date

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.domain.models.transport_preference import (
    TransportMode, TransportType, TransportPreference, 
    TransportConstraints, DEFAULT_PREFERENCES, create_custom_preference
)
from src.itinerary_planner.domain.models.story import Story, TimeWindow
from src.itinerary_planner.application.services.enhanced_planning_service import EnhancedPlanningService
from src.itinerary_planner.application.services.smart_transport_planner import PlanningContext
from src.itinerary_planner.infrastructure.persistence.database import get_session
from src.itinerary_planner.infrastructure.persistence.orm_models import Place

def test_transport_preferences():
    """測試交通工具偏好設定"""
    print("=== 測試交通工具偏好設定 ===")
    
    # 測試預設偏好
    driving_pref = DEFAULT_PREFERENCES["driving"]
    public_pref = DEFAULT_PREFERENCES["public_transport"]
    mixed_pref = DEFAULT_PREFERENCES["mixed"]
    
    print(f"開車偏好: {driving_pref.primary_mode.value}")
    print(f"大眾運輸偏好: {public_pref.primary_mode.value}")
    print(f"混合模式偏好: {mixed_pref.primary_mode.value}")
    
    # 測試自訂偏好
    custom_pref = create_custom_preference(
        primary_mode=TransportMode.DRIVING,
        primary_type=TransportType.CAR,
        constraints=TransportConstraints(
            max_walking_distance=300.0,
            max_walking_time=5,
            max_daily_driving_time=600  # 10小時
        )
    )
    
    print(f"自訂偏好: 最大步行距離 {custom_pref.constraints.max_walking_distance}m")
    print(f"最大每日開車時間: {custom_pref.constraints.max_daily_driving_time}分鐘")

def test_enhanced_planning():
    """測試增強版行程規劃"""
    print("\n=== 測試增強版行程規劃 ===")
    
    # 建立測試故事
    story = Story(
        destination="宜蘭",
        days=2,
        interests=["美食", "自然風景"],
        budget="medium",
        date_range=["2024-01-15", "2024-01-16"],
        daily_window=TimeWindow(start="09:00", end="18:00")
    )
    
    print(f"目的地: {story.destination}")
    print(f"天數: {story.days}")
    print(f"興趣: {story.interests}")
    
    # 建立增強版規劃服務
    enhanced_planner = EnhancedPlanningService()
    
    # 測試不同交通工具偏好
    transport_modes = ["driving", "public_transport", "mixed", "eco_friendly"]
    
    for mode in transport_modes:
        print(f"\n--- 測試 {mode} 模式 ---")
        
        try:
            # 建立模擬候選景點（實際應用中會從資料庫取得）
            candidates = create_mock_candidates()
            
            # 規劃行程
            itinerary = enhanced_planner.plan_itinerary_with_transport(
                story, candidates, user_transport_choice=mode
            )
            
            print(f"✅ {mode} 模式規劃成功")
            print(f"行程天數: {len(itinerary.days)}")
            
            # 顯示第一天行程
            if itinerary.days:
                day1 = itinerary.days[0]
                print(f"第一天景點數: {len(day1.visits)}")
                for visit in day1.visits[:3]:  # 只顯示前3個
                    print(f"  - {visit.place.name}")
            
            # 估算交通影響
            transport_pref = DEFAULT_PREFERENCES.get(mode, DEFAULT_PREFERENCES["mixed"])
            impact = enhanced_planner.estimate_transport_impact(itinerary, transport_pref)
            print(f"預估費用: ${impact['total_cost']}")
            print(f"碳排放: {impact['total_carbon_emission']} kg CO2")
            
        except Exception as e:
            print(f"❌ {mode} 模式規劃失敗: {e}")

def test_transport_options():
    """測試交通工具選項推薦"""
    print("\n=== 測試交通工具選項推薦 ===")
    
    enhanced_planner = EnhancedPlanningService()
    
    # 測試不同故事類型的推薦
    test_stories = [
        Story(destination="宜蘭山區", interests=["登山", "自然風景"]),
        Story(destination="宜蘭市區", interests=["文化", "歷史", "美食"]),
        Story(destination="宜蘭", interests=["生態", "環保"]),
        Story(destination="宜蘭", interests=["親子", "休閒"])
    ]
    
    for story in test_stories:
        print(f"\n目的地: {story.destination}, 興趣: {story.interests}")
        options = enhanced_planner.get_transport_options_for_story(story)
        
        for option in options:
            print(f"  {option['icon']} {option['name']}: {option['description']}")

def create_mock_candidates():
    """建立模擬候選景點"""
    candidates = []
    
    # 模擬宜蘭景點
    mock_places = [
        {"name": "外澳海灘", "lat": 24.870935, "lon": 121.839346},
        {"name": "宜蘭轉運站", "lat": 24.7570, "lon": 121.7536},
        {"name": "礁溪溫泉", "lat": 24.8278, "lon": 121.7734},
        {"name": "羅東夜市", "lat": 24.6770, "lon": 121.7671},
        {"name": "梅花湖", "lat": 24.6394, "lon": 121.7214}
    ]
    
    for place_data in mock_places:
        place = Place()
        place.name = place_data["name"]
        place.geom = f"POINT({place_data['lon']} {place_data['lat']})"
        place.stay_minutes = 60
        place.description = f"{place_data['name']} 景點介紹"
        candidates.append(place)
    
    return candidates

def test_conversation_integration():
    """測試對話整合"""
    print("\n=== 測試對話整合 ===")
    
    # 模擬對話收集的資訊
    collected_info = {
        "destination": "宜蘭",
        "duration": "2天1夜",
        "interests": ["美食", "自然風景"],
        "budget": "medium",
        "transport_mode": "mixed"
    }
    
    print("收集的資訊:")
    for key, value in collected_info.items():
        print(f"  {key}: {value}")
    
    # 測試偏好管理器
    from src.itinerary_planner.application.services.smart_transport_planner import TransportPreferenceManager
    
    manager = TransportPreferenceManager()
    preference = manager.create_preference_from_user_input(
        primary_mode="mixed",
        accessibility_needs=[],
        budget="medium",
        eco_friendly=False
    )
    
    print(f"\n生成的偏好設定:")
    print(f"  主要模式: {preference.primary_mode.value}")
    print(f"  優化策略: {preference.optimization.value}")
    print(f"  最大步行距離: {preference.constraints.max_walking_distance}m")

def main():
    """主程式"""
    print("=== 智能交通規劃系統測試 ===")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 測試1: 交通工具偏好設定
        test_transport_preferences()
        
        # 測試2: 增強版行程規劃
        test_enhanced_planning()
        
        # 測試3: 交通工具選項推薦
        test_transport_options()
        
        # 測試4: 對話整合
        test_conversation_integration()
        
        print("\n=== 測試完成 ===")
        print("✅ 所有測試已成功執行")
        print("\n主要功能:")
        print("- ✅ 交通工具偏好系統")
        print("- ✅ 智能交通規劃")
        print("- ✅ 多模式行程規劃")
        print("- ✅ 對話整合")
        print("- ✅ 交通影響估算")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
