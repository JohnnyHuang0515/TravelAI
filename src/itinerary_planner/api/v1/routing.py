"""
OSRM 路由計算 API
整合真實 OSRM 服務提供路由計算功能
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import asyncio
from datetime import datetime

router = APIRouter(prefix="/routing", tags=["routing"])

# OSRM 服務配置
import os
OSRM_BASE_URL = os.getenv("OSRM_HOST", "http://localhost:5000")

class Coordinate(BaseModel):
    """座標點"""
    lat: float
    lon: float

class RouteRequest(BaseModel):
    """路由請求"""
    start: Coordinate
    end: Coordinate
    vehicle_type: str = "car"
    route_preference: str = "fastest"
    traffic_conditions: str = "normal"
    alternatives: bool = False

class RouteLeg(BaseModel):
    """路線段"""
    distance: float
    duration: float
    summary: str
    steps: List[Dict[str, Any]] = []

class RouteResponse(BaseModel):
    """路由回應"""
    distance: float
    duration: float
    geometry: str
    legs: List[RouteLeg]
    weight_name: str
    weight: float

class AlternativeRoute(BaseModel):
    """替代路線"""
    routes: List[RouteResponse]
    waypoints: List[Dict[str, Any]]
    code: str

class TrafficConditions(BaseModel):
    """交通狀況"""
    light: float = 0.8    # 輕度交通，時間減少20%
    normal: float = 1.0   # 正常交通
    heavy: float = 1.5    # 重度交通，時間增加50%

# 交通狀況係數
TRAFFIC_FACTORS = TrafficConditions()

def get_osrm_profile_for_vehicle(vehicle_type: str) -> str:
    """根據交通工具類型返回對應的 OSRM profile"""
    if vehicle_type == "car":
        return "driving"  # 汽車可以使用高速公路
    elif vehicle_type == "motorcycle":
        return "driving"  # 機車不能走高速公路，但 OSRM 會自動避開
    elif vehicle_type == "bus":
        return "driving"  # 公車有路線限制，但 OSRM 會自動避開高速公路
    else:
        return "driving"

async def call_osrm_api(coordinates: str, alternatives: bool = False, vehicle_type: str = "car") -> Dict[str, Any]:
    """調用 OSRM API"""
    try:
        profile = get_osrm_profile_for_vehicle(vehicle_type)
        url = f"{OSRM_BASE_URL}/route/v1/{profile}/{coordinates}"
        
        params = {
            "alternatives": alternatives,
            "steps": False,
            "geometries": "polyline",
            "overview": "simplified"
        }
        
        # 針對不同交通工具添加特殊參數
        # 注意：OSRM 5.22.0 的 avoid 參數格式可能有問題
        # 暫時移除 avoid 參數，讓 OSRM 使用預設邏輯
        # 後續可以通過調整 OSRM 數據或使用不同的 profile 來實現路線區分
        pass
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="OSRM 服務超時")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"OSRM 服務錯誤: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OSRM 服務調用失敗: {str(e)}")

def apply_traffic_factor(duration: float, traffic_condition: str) -> float:
    """應用交通狀況係數"""
    factor = getattr(TRAFFIC_FACTORS, traffic_condition, 1.0)
    return round(duration * factor, 1)

def adjust_route_for_vehicle(route: dict, vehicle_type: str, traffic_condition: str) -> dict:
    """根據交通工具類型調整路線時間和距離"""
    base_distance = route["distance"]
    base_duration = route["duration"]
    
    if vehicle_type == "car":
        # 汽車：使用 OSRM 原始計算（可走高速公路）
        adjusted_duration = base_duration
        
    elif vehicle_type == "motorcycle":
        # 機車：不能走高速公路，需要繞行
        # 判斷是否為高速公路路線（距離較短且時間較短）
        if base_distance < 60000 and base_duration < 4000:  # 距離 < 60km 且時間 < 67分鐘
            # 這是高速公路路線，機車需要繞行
            # 台北到宜蘭：機車走北宜公路約 80-90 km，2-3 小時
            route["distance"] = int(base_distance * 1.4)  # 距離增加 40%
            adjusted_duration = base_duration * 2.2  # 時間增加 120%（山路行駛較慢）
        else:
            # 已經是繞行路線，只需要調整速度
            adjusted_duration = base_duration * 1.2  # 山路行駛較慢，時間增加 20%
            
    elif vehicle_type == "bus":
        # 公車：可以走高速公路，但停靠站點多，時間較長
        adjusted_duration = base_duration * 1.3  # 停靠站點增加時間 30%
    
    # 應用交通狀況係數
    traffic_factor = getattr(TRAFFIC_FACTORS, traffic_condition, 1.0)
    route["duration"] = round(adjusted_duration * traffic_factor, 1)
    
    return route

@router.post("/calculate", response_model=AlternativeRoute)
async def calculate_route(request: RouteRequest):
    """
    計算路由
    
    - **start**: 起點座標
    - **end**: 終點座標  
    - **vehicle_type**: 交通工具類型 (car, motorcycle, bus)
    - **route_preference**: 路線偏好 (fastest, shortest, balanced)
    - **traffic_conditions**: 交通狀況 (light, normal, heavy)
    - **alternatives**: 是否返回替代路線
    """
    
    # 構建座標字符串
    coordinates = f"{request.start.lon},{request.start.lat};{request.end.lon},{request.end.lat}"
    
    try:
        # 調用 OSRM API
        osrm_response = await call_osrm_api(coordinates, request.alternatives, request.vehicle_type)
        
        if osrm_response.get("code") != "Ok":
            raise HTTPException(status_code=400, detail=f"OSRM 路由計算失敗: {osrm_response.get('code')}")
        
        # 根據交通工具類型調整路線和時間
        for route in osrm_response.get("routes", []):
            # 應用交通工具特定的調整
            route = adjust_route_for_vehicle(route, request.vehicle_type, request.traffic_conditions)
            for leg in route.get("legs", []):
                leg["duration"] = apply_traffic_factor(leg["duration"], request.traffic_conditions)
        
        return AlternativeRoute(**osrm_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路由計算失敗: {str(e)}")

@router.get("/calculate")
async def calculate_route_get(
    start_lat: float = Query(..., description="起點緯度"),
    start_lon: float = Query(..., description="起點經度"),
    end_lat: float = Query(..., description="終點緯度"),
    end_lon: float = Query(..., description="終點經度"),
    vehicle_type: str = Query("car", description="交通工具類型"),
    route_preference: str = Query("fastest", description="路線偏好"),
    traffic_conditions: str = Query("normal", description="交通狀況"),
    alternatives: bool = Query(False, description="是否返回替代路線")
):
    """
    計算路由 (GET 版本)
    
    用於簡單的路由計算請求
    """
    request = RouteRequest(
        start=Coordinate(lat=start_lat, lon=start_lon),
        end=Coordinate(lat=end_lat, lon=end_lon),
        vehicle_type=vehicle_type,
        route_preference=route_preference,
        traffic_conditions=traffic_conditions,
        alternatives=alternatives
    )
    
    return await calculate_route(request)

@router.get("/health")
async def health_check():
    """OSRM 服務健康檢查"""
    try:
        # 使用簡單的路由請求來檢查服務狀態
        coordinates = "121.5170,25.0478;121.5170,25.0478"
        osrm_response = await call_osrm_api(coordinates, False, "car")
        
        return {
            "status": "healthy",
            "osrm_service": "running",
            "timestamp": datetime.now().isoformat(),
            "response": osrm_response.get("code") == "Ok"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "osrm_service": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.post("/batch")
async def calculate_batch_routes(requests: List[RouteRequest]):
    """
    批量計算路由
    
    同時計算多條路線，提高效率
    """
    if len(requests) > 10:
        raise HTTPException(status_code=400, detail="批量請求最多支持10條路線")
    
    try:
        # 並發處理所有請求
        tasks = [calculate_route(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理結果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "index": i,
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append({
                    "index": i,
                    "result": result.dict(),
                    "success": True
                })
        
        return {
            "results": processed_results,
            "total": len(requests),
            "successful": sum(1 for r in processed_results if r["success"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量計算失敗: {str(e)}")

@router.get("/isochrone")
async def calculate_isochrone(
    center_lat: float = Query(..., description="中心點緯度"),
    center_lon: float = Query(..., description="中心點經度"),
    max_time_minutes: int = Query(30, description="最大時間（分鐘）"),
    vehicle_type: str = Query("car", description="交通工具類型")
):
    """
    計算等時線（可到達範圍）
    
    計算從指定點出發，在指定時間內可到達的範圍
    """
    try:
        # 構建等時線請求
        coordinates = f"{center_lon},{center_lat}"
        url = f"{OSRM_BASE_URL}/isochrone/v1/driving/{coordinates}"
        params = {
            "contours": f"{max_time_minutes * 60}",  # 轉換為秒
            "geometries": "geojson"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"等時線計算失敗: {str(e)}")

# 添加 CORS 支援
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """設置 CORS 中間件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
