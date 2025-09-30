#!/usr/bin/env python3
"""
完整流程測試
測試從註冊、登入、規劃行程、儲存行程、景點推薦的完整流程
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """列印區塊標題"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(status_code, data):
    """列印結果"""
    print(f"📥 狀態碼: {status_code}")
    if isinstance(data, dict) or isinstance(data, list):
        print(f"📋 回應:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"📋 回應: {data}")

class TravelPlanningTest:
    """旅遊規劃完整流程測試"""
    
    def __init__(self):
        self.access_token = None
        self.user_email = None
        self.trip_id = None
        self.share_token = None
    
    def test_1_register(self):
        """測試 1: 註冊新使用者"""
        print_section("測試 1: 註冊新使用者")
        
        self.user_email = f"traveler_{int(datetime.now().timestamp())}@example.com"
        
        response = requests.post(
            f"{BASE_URL}/v1/auth/register",
            json={
                "email": self.user_email,
                "password": "securePass123",
                "username": "小明"
            }
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data['access_token']
            print(f"✅ 註冊成功！Token: {self.access_token[:50]}...")
            return True
        else:
            print("❌ 註冊失敗")
            return False
    
    def test_2_set_preferences(self):
        """測試 2: 設定使用者偏好"""
        print_section("測試 2: 設定使用者偏好")
        
        response = requests.put(
            f"{BASE_URL}/v1/auth/me/preferences",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "favorite_themes": ["美食", "自然景觀", "文化"],
                "travel_pace": "relaxed",
                "budget_level": "moderate",
                "default_daily_start": "09:00",
                "default_daily_end": "18:00"
            }
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            print("✅ 偏好設定成功！")
            return True
        else:
            print("❌ 偏好設定失敗")
            return False
    
    def test_3_plan_itinerary(self):
        """測試 3: 規劃行程（會員個性化）"""
        print_section("測試 3: 規劃行程（會員個性化）")
        
        response = requests.post(
            f"{BASE_URL}/v1/itinerary/propose",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "session_id": f"session_{datetime.now().timestamp()}",
                "text": "我想去宜蘭玩兩天，10月1日出發"
            }
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            data = response.json()
            # 儲存行程資料供後續使用
            self.itinerary_data = data
            print("✅ 行程規劃成功！")
            print(f"   行程天數: {len(data.get('days', []))} 天")
            return True
        else:
            print("❌ 行程規劃失敗")
            return False
    
    def test_4_save_trip(self):
        """測試 4: 儲存行程"""
        print_section("測試 4: 儲存行程到我的行程")
        
        if not hasattr(self, 'itinerary_data'):
            print("⚠️ 跳過：沒有可儲存的行程資料")
            return False
        
        response = requests.post(
            f"{BASE_URL}/v1/trips",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "title": "我的宜蘭兩日遊",
                "description": "美食與自然之旅",
                "destination": "宜蘭",
                "itinerary_data": self.itinerary_data,
                "is_public": False
            }
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 201:
            data = response.json()
            self.trip_id = data['id']
            print(f"✅ 行程儲存成功！Trip ID: {self.trip_id}")
            return True
        else:
            print("❌ 行程儲存失敗")
            return False
    
    def test_5_get_my_trips(self):
        """測試 5: 取得我的行程列表"""
        print_section("測試 5: 取得我的行程列表")
        
        response = requests.get(
            f"{BASE_URL}/v1/trips?page=1&page_size=10",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 取得行程列表成功！共 {data['total']} 筆行程")
            return True
        else:
            print("❌ 取得行程列表失敗")
            return False
    
    def test_6_share_trip(self):
        """測試 6: 分享行程"""
        print_section("測試 6: 分享行程")
        
        if not self.trip_id:
            print("⚠️ 跳過：沒有可分享的行程")
            return False
        
        response = requests.post(
            f"{BASE_URL}/v1/trips/{self.trip_id}/share",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            data = response.json()
            self.share_token = data['share_token']
            print(f"✅ 分享成功！分享連結: {data['share_url']}")
            return True
        else:
            print("❌ 分享失敗")
            return False
    
    def test_7_view_public_trip(self):
        """測試 7: 查看公開行程（無需登入）"""
        print_section("測試 7: 查看公開行程（訪客）")
        
        if not self.share_token:
            print("⚠️ 跳過：沒有分享 Token")
            return False
        
        response = requests.get(
            f"{BASE_URL}/v1/trips/public/{self.share_token}"
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            print("✅ 訪客查看公開行程成功！")
            return True
        else:
            print("❌ 查看公開行程失敗")
            return False
    
    def test_8_nearby_places(self):
        """測試 8: 附近景點推薦"""
        print_section("測試 8: 附近景點推薦")
        
        # 宜蘭火車站座標
        response = requests.get(
            f"{BASE_URL}/v1/places/nearby?lat=24.7021&lon=121.9575&radius=5000&limit=5",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 找到 {data['total']} 個附近景點")
            
            # 儲存第一個景點 ID 供收藏測試
            if data.get('places') and len(data['places']) > 0:
                self.test_place_id = data['places'][0]['id']
            
            return True
        else:
            print("❌ 附近景點推薦失敗")
            return False
    
    def test_9_favorite_place(self):
        """測試 9: 收藏景點"""
        print_section("測試 9: 收藏景點")
        
        if not hasattr(self, 'test_place_id'):
            print("⚠️ 跳過：沒有可收藏的景點")
            return False
        
        response = requests.post(
            f"{BASE_URL}/v1/places/{self.test_place_id}/favorite",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"notes": "很想去的景點"}
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            print("✅ 收藏景點成功！")
            return True
        else:
            print("❌ 收藏景點失敗")
            return False
    
    def test_10_get_favorites(self):
        """測試 10: 取得收藏清單"""
        print_section("測試 10: 取得我的收藏景點")
        
        response = requests.get(
            f"{BASE_URL}/v1/places/favorites",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        print_result(response.status_code, response.json())
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 取得收藏清單成功！共 {data['total']} 個收藏")
            return True
        else:
            print("❌ 取得收藏清單失敗")
            return False
    
    def run_all_tests(self):
        """執行所有測試"""
        print("\n🚀 開始執行完整流程測試")
        print(f"📍 API URL: {BASE_URL}")
        print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            self.test_1_register,
            self.test_2_set_preferences,
            self.test_3_plan_itinerary,
            self.test_4_save_trip,
            self.test_5_get_my_trips,
            self.test_6_share_trip,
            self.test_7_view_public_trip,
            self.test_8_nearby_places,
            self.test_9_favorite_place,
            self.test_10_get_favorites
        ]
        
        results = []
        for test in tests:
            try:
                success = test()
                results.append((test.__name__, success))
            except Exception as e:
                print(f"\n❌ 測試異常: {str(e)}")
                results.append((test.__name__, False))
        
        # 總結
        print_section("測試總結")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"\n測試結果: {passed}/{total} 通過")
        print("\n詳細結果:")
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
        
        print(f"\n通過率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有測試通過！系統運作正常！")
        else:
            print(f"\n⚠️ 有 {total - passed} 個測試失敗，請檢查")

if __name__ == '__main__':
    test = TravelPlanningTest()
    test.run_all_tests()
