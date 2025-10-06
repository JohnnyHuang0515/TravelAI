#!/usr/bin/env python3
"""
後端 OSRM 整合測試腳本
測試後端路由 API 與真實 OSRM 服務的整合
"""

import requests
import json
import time
from typing import Dict, Any

# 測試配置
BACKEND_URL = "http://localhost:8001"
OSRM_URL = "http://localhost:5001"

def test_backend_health():
    """測試後端服務健康狀態"""
    print("🔍 測試後端服務健康狀態...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 後端服務正常運行")
            return True
        else:
            print(f"❌ 後端服務回應異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 無法連接到後端服務: {e}")
        return False

def test_routing_api_health():
    """測試路由 API 健康狀態"""
    print("🔍 測試路由 API 健康狀態...")
    try:
        response = requests.get(f"{BACKEND_URL}/v1/routing/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ 路由 API 健康檢查通過")
                print(f"   OSRM 服務狀態: {data.get('osrm_service')}")
                return True
            else:
                print(f"❌ 路由 API 健康檢查失敗: {data.get('status')}")
                return False
        else:
            print(f"❌ 路由 API 回應異常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 無法連接到路由 API: {e}")
        return False

def test_route_calculation():
    """測試路由計算"""
    print("🗺️ 測試路由計算...")
    try:
        # 台北車站到宜蘭車站
        url = f"{BACKEND_URL}/v1/routing/calculate"
        params = {
            "start_lat": 25.0478,
            "start_lon": 121.5170,
            "end_lat": 24.7548,
            "end_lon": 121.7534,
            "vehicle_type": "car",
            "route_preference": "fastest",
            "traffic_conditions": "normal",
            "alternatives": True
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                main_route = data["routes"][0]
                print("✅ 路由計算成功")
                print(f"   距離: {main_route['distance']/1000:.2f} km")
                print(f"   時間: {main_route['duration']/60:.1f} 分鐘")
                print(f"   替代路線: {len(data['routes'])-1} 條")
                return True
            else:
                print(f"❌ 路由計算失敗: {data.get('code', 'Unknown error')}")
                return False
        else:
            print(f"❌ 路由計算 API 回應異常: {response.status_code}")
            print(f"   回應內容: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 路由計算請求失敗: {e}")
        return False

def test_post_route_calculation():
    """測試 POST 路由計算"""
    print("📝 測試 POST 路由計算...")
    try:
        url = f"{BACKEND_URL}/v1/routing/calculate"
        payload = {
            "start": {"lat": 25.0478, "lon": 121.5170},
            "end": {"lat": 24.7548, "lon": 121.7534},
            "vehicle_type": "car",
            "route_preference": "fastest",
            "traffic_conditions": "normal",
            "alternatives": True
        }
        
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                main_route = data["routes"][0]
                print("✅ POST 路由計算成功")
                print(f"   距離: {main_route['distance']/1000:.2f} km")
                print(f"   時間: {main_route['duration']/60:.1f} 分鐘")
                return True
            else:
                print(f"❌ POST 路由計算失敗: {data.get('code', 'Unknown error')}")
                return False
        else:
            print(f"❌ POST 路由計算 API 回應異常: {response.status_code}")
            print(f"   回應內容: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ POST 路由計算請求失敗: {e}")
        return False

def test_multiple_vehicles():
    """測試多種交通工具路由"""
    print("🚗 測試多種交通工具路由...")
    try:
        vehicles = ["car", "motorcycle", "bus"]
        results = {}
        
        for vehicle in vehicles:
            url = f"{BACKEND_URL}/v1/routing/calculate"
            params = {
                "start_lat": 25.0478,
                "start_lon": 121.5170,
                "end_lat": 24.7548,
                "end_lon": 121.7534,
                "vehicle_type": vehicle,
                "route_preference": "fastest",
                "traffic_conditions": "normal",
                "alternatives": False
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    results[vehicle] = {
                        "distance": route["distance"] / 1000,
                        "duration": route["duration"] / 60
                    }
                else:
                    print(f"❌ {vehicle} 路由計算失敗")
                    return False
            else:
                print(f"❌ {vehicle} 路由計算 API 回應異常: {response.status_code}")
                return False
        
        print("✅ 多種交通工具路由計算成功")
        for vehicle, result in results.items():
            print(f"   {vehicle}: {result['distance']:.2f} km, {result['duration']:.1f} 分鐘")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 多種交通工具路由計算請求失敗: {e}")
        return False

def test_traffic_conditions():
    """測試交通狀況影響"""
    print("🚦 測試交通狀況影響...")
    try:
        traffic_conditions = ["light", "normal", "heavy"]
        results = {}
        
        for condition in traffic_conditions:
            url = f"{BACKEND_URL}/v1/routing/calculate"
            params = {
                "start_lat": 25.0478,
                "start_lon": 121.5170,
                "end_lat": 24.7548,
                "end_lon": 121.7534,
                "vehicle_type": "car",
                "route_preference": "fastest",
                "traffic_conditions": condition,
                "alternatives": False
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    results[condition] = {
                        "distance": route["distance"] / 1000,
                        "duration": route["duration"] / 60
                    }
                else:
                    print(f"❌ {condition} 交通狀況路由計算失敗")
                    return False
            else:
                print(f"❌ {condition} 交通狀況路由計算 API 回應異常: {response.status_code}")
                return False
        
        print("✅ 交通狀況影響測試成功")
        for condition, result in results.items():
            print(f"   {condition}: {result['distance']:.2f} km, {result['duration']:.1f} 分鐘")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 交通狀況影響測試請求失敗: {e}")
        return False

def test_isochrone():
    """測試等時線計算"""
    print("⏰ 測試等時線計算...")
    try:
        url = f"{BACKEND_URL}/v1/routing/isochrone"
        params = {
            "center_lat": 25.0478,
            "center_lon": 121.5170,
            "max_time_minutes": 30,
            "vehicle_type": "car"
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ 等時線計算成功")
            print(f"   回應數據類型: {type(data)}")
            return True
        else:
            print(f"❌ 等時線計算 API 回應異常: {response.status_code}")
            print(f"   回應內容: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 等時線計算請求失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 後端 OSRM 整合測試開始")
    print("=" * 50)
    
    tests = [
        ("後端服務健康檢查", test_backend_health),
        ("路由 API 健康檢查", test_routing_api_health),
        ("路由計算 (GET)", test_route_calculation),
        ("路由計算 (POST)", test_post_route_calculation),
        ("多種交通工具路由", test_multiple_vehicles),
        ("交通狀況影響", test_traffic_conditions),
        ("等時線計算", test_isochrone)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試異常: {e}")
            results.append((test_name, False))
    
    # 總結結果
    print("\n" + "=" * 50)
    print("📊 測試結果總結")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！後端 OSRM 整合功能正常運行")
    else:
        print("⚠️ 部分測試失敗，請檢查相關服務")

if __name__ == "__main__":
    main()
