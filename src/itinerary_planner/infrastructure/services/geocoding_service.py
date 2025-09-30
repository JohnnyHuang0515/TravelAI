#!/usr/bin/env python3
"""
地址解析服務 - 使用 OpenStreetMap Nominatim API
"""

import requests
import time
import json
from typing import Optional, Tuple, Dict, Any

class GeocodingService:
    """地址解析服務"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'ItineraryPlanner/1.0 (contact@example.com)'
        }
        self.rate_limit_delay = 1.0  # 1秒延遲避免被限制
    
    def geocode_address(self, address: str, country: str = "Taiwan") -> Optional[Tuple[float, float]]:
        """
        將地址轉換為座標
        
        Args:
            address: 地址字串
            country: 國家 (預設台灣)
            
        Returns:
            (lat, lon) 或 None
        """
        try:
            # 清理地址
            clean_address = self._clean_address(address)
            
            params = {
                'q': f"{clean_address}, {country}",
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            response = requests.get(
                self.base_url, 
                params=params, 
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    
                    # 檢查是否在台灣範圍內
                    if 21.5 <= lat <= 25.5 and 119.5 <= lon <= 122.5:
                        return (lat, lon)
            
            return None
            
        except Exception as e:
            print(f"地址解析錯誤: {address} - {e}")
            return None
        finally:
            # 遵守 rate limit
            time.sleep(self.rate_limit_delay)
    
    def _clean_address(self, address: str) -> str:
        """清理地址字串"""
        if not address:
            return ""
        
        # 移除多餘的空格
        address = " ".join(address.split())
        
        # 移除郵遞區號
        import re
        address = re.sub(r'^\d{3,5}\s*', '', address)
        
        # 確保包含"宜蘭縣"
        if "宜蘭" not in address and "宜蘭縣" not in address:
            address = f"宜蘭縣{address}"
        
        # 移除詳細門牌號碼，只保留到路名
        # 例如: "宜蘭縣礁溪鄉溫泉路126-50號" -> "宜蘭縣礁溪鄉溫泉路"
        address = re.sub(r'\d+[-\d]*號.*$', '', address)
        address = re.sub(r'\d+[-\d]*樓.*$', '', address)
        
        return address.strip()
    
    def batch_geocode(self, addresses: list, max_retries: int = 3) -> Dict[str, Tuple[float, float]]:
        """
        批量地址解析
        
        Args:
            addresses: 地址列表
            max_retries: 最大重試次數
            
        Returns:
            {address: (lat, lon)} 字典
        """
        results = {}
        failed_addresses = []
        
        print(f"🔄 開始批量地址解析: {len(addresses)} 筆")
        
        for i, address in enumerate(addresses, 1):
            print(f"  📍 處理 {i}/{len(addresses)}: {address[:50]}...")
            
            for attempt in range(max_retries):
                result = self.geocode_address(address)
                if result:
                    results[address] = result
                    print(f"    ✅ 成功: {result}")
                    break
                else:
                    if attempt < max_retries - 1:
                        print(f"    ⚠️ 重試 {attempt + 1}/{max_retries}")
                        time.sleep(2)  # 重試前等待更久
                    else:
                        failed_addresses.append(address)
                        print(f"    ❌ 失敗: {address}")
        
        print(f"\n📊 **批量解析結果**")
        print(f"  ✅ 成功: {len(results)} 筆")
        print(f"  ❌ 失敗: {len(failed_addresses)} 筆")
        
        if failed_addresses:
            print(f"\n❌ **失敗的地址** (前10筆):")
            for addr in failed_addresses[:10]:
                print(f"  - {addr}")
        
        return results

# 建立單例
geocoding_service = GeocodingService()

def test_geocoding():
    """測試地址解析功能"""
    print("🧪 **測試地址解析功能**")
    print("=" * 40)
    
    test_addresses = [
        "宜蘭縣礁溪鄉溫泉路",
        "宜蘭縣羅東鎮中正路",
        "宜蘭縣宜蘭市中山路",
        "宜蘭縣頭城鎮濱海路"
    ]
    
    for address in test_addresses:
        print(f"\n📍 測試地址: {address}")
        result = geocoding_service.geocode_address(address)
        if result:
            lat, lon = result
            print(f"  ✅ 座標: ({lat:.6f}, {lon:.6f})")
        else:
            print(f"  ❌ 解析失敗")

if __name__ == "__main__":
    test_geocoding()
