#!/usr/bin/env python3
"""
公車路線規劃使用範例
展示如何使用公車路線規劃服務
"""

import os
import sys
from datetime import time

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.infrastructure.persistence.database import get_session
from src.itinerary_planner.infrastructure.routing.bus_routing_service import BusRoutingService
from src.itinerary_planner.infrastructure.routing.osrm_service import get_osrm_manager

def example_find_nearby_stations():
    """範例：尋找附近的公車站點"""
    print("=== 尋找附近的公車站點 ===")
    
    with get_session() as session:
        service = BusRoutingService(session)
        
        # 以宜蘭轉運站為中心搜尋附近的站點
        yilan_lon = 121.7536
        yilan_lat = 24.7570
        
        stations = service.find_nearby_stations(yilan_lon, yilan_lat, 1000)
        
        print(f"在宜蘭轉運站附近 1000 公尺內找到 {len(stations)} 個公車站點:")
        for station in stations[:5]:  # 只顯示前5個
            print(f"- {station.station_name} ({station.route.route_name})")
        
        return stations

def example_get_route_schedule():
    """範例：取得路線時刻表"""
    print("\n=== 取得路線時刻表 ===")
    
    with get_session() as session:
        service = BusRoutingService(session)
        
        # 取得紅1路線的時刻表
        schedule = service.get_route_schedule("紅1", direction=0)  # 去程
        
        print(f"紅1路線 (去程) 今日班次:")
        for trip in schedule[:10]:  # 只顯示前10班
            print(f"- {trip['departure_time']} 從 {trip['departure_station']} 出發")
        
        return schedule

def example_plan_route():
    """範例：規劃路線"""
    print("\n=== 規劃路線 ===")
    
    # 確保 OSRM 服務運行
    osrm_manager = get_osrm_manager()
    if not osrm_manager.ensure_service_running():
        print("❌ OSRM 服務未運行，無法進行路線規劃")
        print("請先執行: python scripts/start_osrm_service.py")
        return
    
    with get_session() as session:
        service = BusRoutingService(session)
        
        # 從外澳到宜蘭轉運站的路線規劃
        start_lon = 121.839346  # 外澳
        start_lat = 24.870935
        end_lon = 121.7536      # 宜蘭轉運站
        end_lat = 24.7570
        
        departure_time = time(8, 0)  # 早上8點出發
        
        print(f"規劃路線: 外澳 ({start_lat}, {start_lon}) → 宜蘭轉運站 ({end_lat}, {end_lon})")
        print(f"出發時間: {departure_time.strftime('%H:%M')}")
        
        route_plan = service.plan_route(
            start_lon, start_lat, 
            end_lon, end_lat, 
            departure_time
        )
        
        if route_plan:
            print(f"\n✅ 路線規劃成功:")
            print(f"總時間: {route_plan.total_duration_minutes} 分鐘")
            print(f"步行距離: {route_plan.total_distance_meters} 公尺")
            print(f"路線摘要: {route_plan.summary}")
            
            if route_plan.bus_options:
                option = route_plan.bus_options[0]
                print(f"\n公車資訊:")
                print(f"- 路線: {option.route_name}")
                print(f"- 發車時間: {option.departure_time.strftime('%H:%M')}")
                print(f"- 抵達時間: {option.arrival_time.strftime('%H:%M')}")
                print(f"- 行車時間: {option.duration_minutes} 分鐘")
                print(f"- 低地板公車: {'是' if option.is_low_floor else '否'}")
        else:
            print("❌ 路線規劃失敗")

def example_find_direct_routes():
    """範例：尋找直達路線"""
    print("\n=== 尋找直達路線 ===")
    
    with get_session() as session:
        service = BusRoutingService(session)
        
        # 尋找從外澳到宜蘭轉運站的直達路線
        start_station = service.get_station_by_name("外澳")
        end_station = service.get_station_by_name("宜蘭轉運站")
        
        if start_station and end_station:
            print(f"起點站: {start_station.station_name} ({start_station.route.route_name})")
            print(f"終點站: {end_station.station_name} ({end_station.route.route_name})")
            
            departure_time = time(8, 0)
            routes = service.find_direct_routes(start_station, end_station, departure_time)
            
            if routes:
                print(f"\n找到 {len(routes)} 條直達路線:")
                for i, route in enumerate(routes[:3], 1):  # 只顯示前3條
                    print(f"{i}. {route.route_name}: {route.departure_time.strftime('%H:%M')} - {route.arrival_time.strftime('%H:%M')} ({route.duration_minutes}分鐘)")
            else:
                print("❌ 沒有找到直達路線")
        else:
            print("❌ 找不到指定的站點")

def main():
    """主程式"""
    print("=== 公車路線規劃服務使用範例 ===\n")
    
    try:
        # 範例1: 尋找附近站點
        stations = example_find_nearby_stations()
        
        # 範例2: 取得路線時刻表
        schedule = example_get_route_schedule()
        
        # 範例3: 尋找直達路線
        example_find_direct_routes()
        
        # 範例4: 規劃完整路線
        example_plan_route()
        
        print("\n=== 範例執行完成 ===")
        print("所有範例已成功執行！")
        
    except Exception as e:
        print(f"\n❌ 執行範例時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

