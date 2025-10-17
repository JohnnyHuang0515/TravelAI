"""
OSRM 路由服務模組
提供基於 OSRM 引擎的路由計算功能
"""

import requests
import json
import subprocess
import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class RouteResult:
    """路由結果資料類別"""
    distance: float  # 距離 (公尺)
    duration: float  # 時間 (秒)
    geometry: List[Tuple[float, float]]  # 路線幾何座標
    instructions: List[Dict]  # 導航指示
    summary: str  # 路線摘要

@dataclass
class RouteRequest:
    """路由請求資料類別"""
    coordinates: List[Tuple[float, float]]  # 座標列表 [(lon, lat), ...]
    profile: str = "driving"  # 路由配置檔 (driving, walking, cycling)
    alternatives: bool = False  # 是否返回替代路線
    steps: bool = True  # 是否包含步驟指示
    geometries: str = "geojson"  # 幾何格式 (geojson, polyline)
    overview: str = "full"  # 路線概覽詳細程度

class OSRMService:
    """OSRM 路由服務類別"""
    
    def __init__(self, 
                 osrm_host: str = "localhost", 
                 osrm_port: int = 5000,
                 data_dir: str = None):
        """
        初始化 OSRM 服務
        
        Args:
            osrm_host: OSRM 服務主機
            osrm_port: OSRM 服務端口
            data_dir: OSRM 資料目錄路徑
        """
        self.host = osrm_host
        self.port = osrm_port
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "../../../../data/osrm")
        self.base_url = f"http://{self.host}:{self.port}"
        self.process = None
        
    def is_service_running(self) -> bool:
        """檢查 OSRM 服務是否正在運行"""
        try:
            response = requests.get(f"{self.base_url}/route/v1/driving/0,0;1,1", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def start_service(self) -> bool:
        """啟動 OSRM 服務"""
        if self.is_service_running():
            logger.info("OSRM 服務已在運行")
            return True
        
        # 檢查資料檔案是否存在
        osrm_file = os.path.join(self.data_dir, "taiwan-250923.osrm")
        if not os.path.exists(osrm_file):
            logger.error(f"找不到 OSRM 資料檔案: {osrm_file}")
            return False
        
        try:
            # 啟動 OSRM 服務
            cmd = [
                "osrm-routed",
                "--algorithm", "mld",
                osrm_file
            ]
            
            logger.info(f"啟動 OSRM 服務: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.data_dir
            )
            
            # 等待服務啟動
            for i in range(30):  # 最多等待 30 秒
                time.sleep(1)
                if self.is_service_running():
                    logger.info("OSRM 服務啟動成功")
                    return True
                logger.info(f"等待 OSRM 服務啟動... ({i+1}/30)")
            
            logger.error("OSRM 服務啟動超時")
            self.stop_service()
            return False
            
        except FileNotFoundError:
            logger.error("找不到 osrm-routed 執行檔，請確認 OSRM 已正確安裝")
            return False
        except Exception as e:
            logger.error(f"啟動 OSRM 服務時發生錯誤: {e}")
            return False
    
    def stop_service(self):
        """停止 OSRM 服務"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                logger.info("OSRM 服務已停止")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.info("OSRM 服務已強制停止")
            except Exception as e:
                logger.error(f"停止 OSRM 服務時發生錯誤: {e}")
            finally:
                self.process = None
    
    def route(self, request: RouteRequest) -> Optional[RouteResult]:
        """
        計算路由
        
        Args:
            request: 路由請求
            
        Returns:
            路由結果，如果計算失敗則返回 None
        """
        if not self.is_service_running():
            logger.error("OSRM 服務未運行")
            return None
        
        try:
            # 構建座標字串
            coordinates_str = ";".join([f"{lon},{lat}" for lon, lat in request.coordinates])
            
            # 構建請求 URL
            url = f"{self.base_url}/route/v1/{request.profile}/{coordinates_str}"
            
            # 請求參數
            params = {
                "alternatives": str(request.alternatives).lower(),
                "steps": str(request.steps).lower(),
                "geometries": request.geometries,
                "overview": request.overview
            }
            
            logger.debug(f"發送路由請求: {url}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                logger.error(f"路由計算失敗: {data.get('message', '未知錯誤')}")
                return None
            
            # 解析第一個路線結果
            route = data["routes"][0]
            legs = route["legs"]
            
            # 計算總距離和時間
            total_distance = sum(leg["distance"] for leg in legs)
            total_duration = sum(leg["duration"] for leg in legs)
            
            # 提取幾何座標
            geometry = []
            if "geometry" in route:
                if request.geometries == "geojson":
                    geometry = route["geometry"]["coordinates"]
                else:  # polyline
                    # 這裡需要解碼 polyline，簡化處理
                    geometry = []
            
            # 提取導航指示
            instructions = []
            if request.steps and "legs" in data:
                for leg in data["legs"]:
                    if "steps" in leg:
                        instructions.extend(leg["steps"])
            
            return RouteResult(
                distance=total_distance,
                duration=total_duration,
                geometry=geometry,
                instructions=instructions,
                summary=route.get("summary", "")
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"路由請求失敗: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"解析路由結果時發生錯誤: {e}")
            return None
        except Exception as e:
            logger.error(f"計算路由時發生未預期錯誤: {e}")
            return None
    
    def route_between_points(self, 
                           start_lon: float, 
                           start_lat: float, 
                           end_lon: float, 
                           end_lat: float,
                           profile: str = "driving") -> Optional[RouteResult]:
        """
        計算兩點間的路由
        
        Args:
            start_lon: 起點經度
            start_lat: 起點緯度
            end_lon: 終點經度
            end_lat: 終點緯度
            profile: 路由配置檔
            
        Returns:
            路由結果
        """
        request = RouteRequest(
            coordinates=[(start_lon, start_lat), (end_lon, end_lat)],
            profile=profile
        )
        return self.route(request)
    
    def route_via_points(self, 
                        coordinates: List[Tuple[float, float]],
                        profile: str = "driving") -> Optional[RouteResult]:
        """
        計算經過多個點的路由
        
        Args:
            coordinates: 座標列表 [(lon, lat), ...]
            profile: 路由配置檔
            
        Returns:
            路由結果
        """
        if len(coordinates) < 2:
            logger.error("至少需要兩個座標點")
            return None
        
        request = RouteRequest(
            coordinates=coordinates,
            profile=profile
        )
        return self.route(request)
    
    def nearest_station(self, 
                       lon: float, 
                       lat: float, 
                       max_distance: float = 1000) -> Optional[Dict]:
        """
        尋找最近的公車站點
        
        Args:
            lon: 經度
            lat: 緯度
            max_distance: 最大搜尋距離 (公尺)
            
        Returns:
            最近站點資訊
        """
        # 這裡需要與資料庫整合，暫時返回 None
        # 實際實現時會查詢 bus_stations 表
        logger.warning("nearest_station 方法尚未實現")
        return None
    
    def get_route_summary(self, route_result: RouteResult) -> str:
        """
        取得路由摘要文字
        
        Args:
            route_result: 路由結果
            
        Returns:
            路由摘要文字
        """
        distance_km = route_result.distance / 1000
        duration_min = route_result.duration / 60
        
        if duration_min < 60:
            duration_text = f"{duration_min:.1f} 分鐘"
        else:
            hours = int(duration_min // 60)
            minutes = int(duration_min % 60)
            duration_text = f"{hours} 小時 {minutes} 分鐘"
        
        return f"距離: {distance_km:.2f} 公里，預估時間: {duration_text}"

class OSRMManager:
    """OSRM 服務管理器"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir
        self.service = None
    
    def get_service(self) -> OSRMService:
        """取得 OSRM 服務實例"""
        if not self.service:
            self.service = OSRMService(data_dir=self.data_dir)
        return self.service
    
    def ensure_service_running(self) -> bool:
        """確保 OSRM 服務正在運行"""
        service = self.get_service()
        if not service.is_service_running():
            return service.start_service()
        return True
    
    def cleanup(self):
        """清理資源"""
        if self.service:
            self.service.stop_service()
            self.service = None

# 全域 OSRM 管理器實例
_osrm_manager = None

def get_osrm_manager() -> OSRMManager:
    """取得全域 OSRM 管理器實例"""
    global _osrm_manager
    if not _osrm_manager:
        _osrm_manager = OSRMManager()
    return _osrm_manager

