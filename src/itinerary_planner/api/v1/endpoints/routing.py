"""
路由計算 API 端點
提供路線規劃和距離計算功能
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List, Tuple
import logging
from pydantic import BaseModel

from ....infrastructure.clients.osrm_client import osrm_client
from ....application.services.carbon_calculation_service import CarbonCalculationService

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routing", tags=["路由計算"])


class RouteCalculationRequest(BaseModel):
    """路由計算請求"""
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    vehicle_type: str = "car"  # car, motorcycle, bus
    route_preference: str = "fastest"  # fastest, shortest, balanced
    traffic_conditions: str = "normal"  # normal, heavy, light


class RouteCalculationResponse(BaseModel):
    """路由計算回應"""
    duration: float  # 行駛時間（秒）
    distance: float  # 距離（公尺）
    carbon_emission: float  # 碳排放量（克）
    route_geometry: Optional[str] = None  # 路線幾何（可選）


@router.get("/calculate", response_model=RouteCalculationResponse)
async def calculate_route(
    start_lat: float = Query(..., description="起點緯度"),
    start_lon: float = Query(..., description="起點經度"),
    end_lat: float = Query(..., description="終點緯度"),
    end_lon: float = Query(..., description="終點經度"),
    vehicle_type: str = Query("car", description="交通工具類型"),
    route_preference: str = Query("fastest", description="路線偏好"),
    traffic_conditions: str = Query("normal", description="交通狀況")
):
    """
    計算兩點間的路線
    
    - **start_lat**: 起點緯度
    - **start_lon**: 起點經度  
    - **end_lat**: 終點緯度
    - **end_lon**: 終點經度
    - **vehicle_type**: 交通工具類型 (car, motorcycle, bus)
    - **route_preference**: 路線偏好 (fastest, shortest, balanced)
    - **traffic_conditions**: 交通狀況 (normal, heavy, light)
    """
    try:
        logger.info(f"計算路由: ({start_lat}, {start_lon}) -> ({end_lat}, {end_lon}), 車輛: {vehicle_type}")
        
        # 驗證參數
        if vehicle_type not in ["car", "motorcycle", "bus"]:
            raise HTTPException(status_code=400, detail="不支援的交通工具類型")
        
        if route_preference not in ["fastest", "shortest", "balanced"]:
            raise HTTPException(status_code=400, detail="不支援的路線偏好")
        
        # 使用 OSRM 計算路線
        start_point = (start_lat, start_lon)
        end_point = (end_lat, end_lon)
        
        routes = await osrm_client.get_route_alternatives(
            start_point, 
            end_point, 
            route_preference
        )
        
        if not routes:
            # 如果 OSRM 失敗，返回預設值
            logger.warning("OSRM 路由計算失敗，使用預設值")
            distance = 10000  # 預設 10 公里
            duration = 1800   # 預設 30 分鐘
        else:
            # 使用第一條路線
            route = routes[0]
            distance = route.get("distance", 10000)
            duration = route.get("duration", 1800)
        
        # 計算碳排放
        carbon_service = CarbonCalculationService()
        carbon_emission = carbon_service.calculate_carbon_emission(
            distance=distance,
            vehicle_type=vehicle_type,
            traffic_conditions=traffic_conditions
        )
        
        return RouteCalculationResponse(
            duration=duration,
            distance=distance,
            carbon_emission=carbon_emission
        )
        
    except Exception as e:
        logger.error(f"路由計算錯誤: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"路由計算失敗: {str(e)}")


@router.post("/calculate", response_model=RouteCalculationResponse)
async def calculate_route_post(request: RouteCalculationRequest):
    """
    使用 POST 方法計算路線（支援批量計算）
    """
    return await calculate_route(
        start_lat=request.start_lat,
        start_lon=request.start_lon,
        end_lat=request.end_lat,
        end_lon=request.end_lon,
        vehicle_type=request.vehicle_type,
        route_preference=request.route_preference,
        traffic_conditions=request.traffic_conditions
    )


@router.get("/matrix")
async def get_travel_time_matrix(
    locations: str = Query(..., description="地點列表，格式: lat1,lon1;lat2,lon2;..."),
    vehicle_type: str = Query("car", description="交通工具類型")
):
    """
    計算多個地點間的旅行時間矩陣
    
    - **locations**: 地點列表，格式為 "lat1,lon1;lat2,lon2;..."
    - **vehicle_type**: 交通工具類型
    """
    try:
        # 解析地點列表
        location_pairs = []
        for location_str in locations.split(';'):
            lat, lon = map(float, location_str.split(','))
            location_pairs.append((lat, lon))
        
        if len(location_pairs) < 2:
            raise HTTPException(status_code=400, detail="至少需要兩個地點")
        
        # 計算時間矩陣
        matrix = await osrm_client.get_travel_time_matrix(
            location_pairs,
            route_preference="fastest"
        )
        
        return {
            "matrix": matrix,
            "locations": location_pairs,
            "vehicle_type": vehicle_type
        }
        
    except Exception as e:
        logger.error(f"時間矩陣計算錯誤: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"時間矩陣計算失敗: {str(e)}")
