#!/usr/bin/env python3
"""
測試認證 API
"""

import requests
import json
from datetime import datetime

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def print_header(title):
    """列印標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_register():
    """測試註冊"""
    print_header("測試使用者註冊")
    
    url = f"{BASE_URL}/v1/auth/register"
    data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "testPassword123",
        "username": "test_user"
    }
    
    print(f"📤 請求: POST {url}")
    print(f"📝 資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=data)
    
    print(f"\n📥 狀態碼: {response.status_code}")
    print(f"📋 回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 201:
        print("✅ 註冊成功！")
        return response.json()
    else:
        print("❌ 註冊失敗")
        return None

def test_login(email, password):
    """測試登入"""
    print_header("測試使用者登入")
    
    url = f"{BASE_URL}/v1/auth/login"
    data = {
        "email": email,
        "password": password
    }
    
    print(f"📤 請求: POST {url}")
    print(f"📝 資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=data)
    
    print(f"\n📥 狀態碼: {response.status_code}")
    print(f"📋 回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("✅ 登入成功！")
        return response.json()
    else:
        print("❌ 登入失敗")
        return None

def test_get_me(access_token):
    """測試取得當前使用者資料"""
    print_header("測試取得當前使用者資料")
    
    url = f"{BASE_URL}/v1/auth/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"📤 請求: GET {url}")
    print(f"🔑 Token: {access_token[:50]}...")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n📥 狀態碼: {response.status_code}")
    print(f"📋 回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("✅ 取得使用者資料成功！")
    else:
        print("❌ 取得使用者資料失敗")

def test_get_preferences(access_token):
    """測試取得使用者偏好"""
    print_header("測試取得使用者偏好")
    
    url = f"{BASE_URL}/v1/auth/me/preferences"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"📤 請求: GET {url}")
    
    response = requests.get(url, headers=headers)
    
    print(f"\n📥 狀態碼: {response.status_code}")
    print(f"📋 回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("✅ 取得使用者偏好成功！")
    else:
        print("❌ 取得使用者偏好失敗")

def test_update_preferences(access_token):
    """測試更新使用者偏好"""
    print_header("測試更新使用者偏好")
    
    url = f"{BASE_URL}/v1/auth/me/preferences"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "favorite_themes": ["美食", "自然", "文化"],
        "travel_pace": "relaxed",
        "budget_level": "moderate"
    }
    
    print(f"📤 請求: PUT {url}")
    print(f"📝 資料: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    response = requests.put(url, json=data, headers=headers)
    
    print(f"\n📥 狀態碼: {response.status_code}")
    print(f"📋 回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("✅ 更新使用者偏好成功！")
    else:
        print("❌ 更新使用者偏好失敗")

def test_refresh_token(refresh_token):
    """測試刷新 Token"""
    print_header("測試刷新 Access Token")
    
    url = f"{BASE_URL}/v1/auth/refresh"
    data = {
        "refresh_token": refresh_token
    }
    
    print(f"📤 請求: POST {url}")
    
    response = requests.post(url, json=data)
    
    print(f"\n📥 狀態碼: {response.status_code}")
    print(f"📋 回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("✅ 刷新 Token 成功！")
        return response.json()
    else:
        print("❌ 刷新 Token 失敗")
        return None

def main():
    """主測試流程"""
    print("\n🚀 開始測試認證 API")
    print(f"📍 API URL: {BASE_URL}")
    
    # 1. 測試註冊
    register_result = test_register()
    if not register_result:
        print("\n❌ 註冊失敗，無法繼續測試")
        return
    
    email = register_result['user']['email']
    password = "testPassword123"
    access_token = register_result['access_token']
    refresh_token = register_result['refresh_token']
    
    # 2. 測試登入
    login_result = test_login(email, password)
    if login_result:
        access_token = login_result['access_token']
    
    # 3. 測試取得使用者資料
    test_get_me(access_token)
    
    # 4. 測試取得偏好
    test_get_preferences(access_token)
    
    # 5. 測試更新偏好
    test_update_preferences(access_token)
    
    # 6. 測試刷新 Token
    test_refresh_token(refresh_token)
    
    print("\n" + "=" * 60)
    print("  🎉 所有測試完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
