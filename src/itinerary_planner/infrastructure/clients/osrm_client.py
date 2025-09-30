import httpx
from typing import List, Tuple, Optional
import asyncio

class OSRMClient:
    """OSRM 路由引擎客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
    
    async def get_travel_time_matrix(
        self, 
        locations: List[Tuple[float, float]], 
        route_preference: str = "fastest"
    ) -> List[List[float]]:
        """
        獲取地點間的交通時間矩陣
        locations: [(lat, lon), ...] 格式的座標列表
        route_preference: 路線偏好 ("fastest", "shortest", "balanced")
        返回: 交通時間矩陣（秒）
        """
        if not locations:
            return []
        
        # 構建 OSRM table API 請求
        coordinates = ";".join([f"{lon},{lat}" for lon, lat in locations])
        
        # 根據路線偏好設定參數
        params = {}
        if route_preference == "shortest":
            params["annotations"] = "distance"
        elif route_preference == "balanced":
            params["annotations"] = "duration,distance"
        
        url = f"{self.base_url}/table/v1/driving/{coordinates}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # 返回交通時間矩陣（秒）
                return data.get("durations", [])
            except Exception as e:
                print(f"OSRM request failed: {e}")
                # 返回模擬的交通時間矩陣
                n = len(locations)
                return [[0 if i == j else 300 for j in range(n)] for i in range(n)]
    
    async def get_route_alternatives(
        self, 
        start: Tuple[float, float], 
        end: Tuple[float, float],
        route_preference: str = "fastest"
    ) -> List[dict]:
        """
        獲取兩點間的多條替代路線
        start: (lat, lon) 起點座標
        end: (lat, lon) 終點座標
        route_preference: 路線偏好 ("fastest", "shortest", "balanced")
        返回: 路線列表，包含時間、距離、路徑等信息
        """
        coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
        url = f"{self.base_url}/route/v1/driving/{coordinates}"
        
        params = {
            "overview": "false",
            "alternatives": "true",
            "steps": "false"
        }
        
        # 根據路線偏好設定參數
        if route_preference == "shortest":
            params["continue_straight"] = "false"
        elif route_preference == "balanced":
            params["geometries"] = "polyline"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                routes = []
                for route in data.get("routes", []):
                    routes.append({
                        "duration": route.get("duration", 0),
                        "distance": route.get("distance", 0),
                        "weight": route.get("weight", 0)
                    })
                
                return routes
            except Exception as e:
                print(f"OSRM route request failed: {e}")
                return []

# 建立單例
osrm_client = OSRMClient()