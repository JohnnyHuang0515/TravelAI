"""
公車路線規劃服務
整合公車資料和 OSRM 路由引擎，提供公車路線規劃功能
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, time, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement
from geoalchemy2.functions import ST_DWithin, ST_Distance

from ..persistence.orm_models import BusRoute, BusStation, BusTrip, BusStopTime
from .osrm_service import OSRMService, RouteResult, get_osrm_manager

logger = logging.getLogger(__name__)

@dataclass
class BusRouteOption:
    """公車路線選項"""
    route_name: str
    departure_station: str
    destination_station: str
    departure_time: time
    arrival_time: time
    duration_minutes: int
    transfers: List[str]  # 轉乘路線
    walking_distance_meters: int
    is_low_floor: bool
    operating_days: List[str]

@dataclass
class RoutePlan:
    """路線規劃結果"""
    total_duration_minutes: int
    total_distance_meters: int
    walking_duration_minutes: int
    bus_options: List[BusRouteOption]
    route_geometry: List[Tuple[float, float]]
    summary: str

class BusRoutingService:
    """公車路線規劃服務"""
    
    def __init__(self, session: Session, osrm_service: Optional[OSRMService] = None):
        """
        初始化公車路線規劃服務
        
        Args:
            session: 資料庫會話
            osrm_service: OSRM 服務實例
        """
        self.session = session
        self.osrm_service = osrm_service or get_osrm_manager().get_service()
    
    def find_nearby_stations(self, 
                           lon: float, 
                           lat: float, 
                           radius_meters: float = 500) -> List[BusStation]:
        """
        尋找附近的公車站點
        
        Args:
            lon: 經度
            lat: 緯度
            radius_meters: 搜尋半徑 (公尺)
            
        Returns:
            附近的公車站點列表
        """
        try:
            # 使用 PostGIS 進行空間查詢
            point = WKTElement(f'POINT({lon} {lat})', srid=4326)
            
            stations = self.session.query(BusStation).filter(
                ST_DWithin(BusStation.geom, point, radius_meters)
            ).order_by(
                ST_Distance(BusStation.geom, point)
            ).limit(10).all()
            
            return stations
            
        except Exception as e:
            logger.error(f"搜尋附近站點時發生錯誤: {e}")
            return []
    
    def get_station_by_name(self, station_name: str) -> Optional[BusStation]:
        """
        根據站名取得站點資訊
        
        Args:
            station_name: 站點名稱
            
        Returns:
            站點資訊
        """
        try:
            station = self.session.query(BusStation).filter(
                BusStation.station_name.ilike(f"%{station_name}%")
            ).first()
            return station
        except Exception as e:
            logger.error(f"搜尋站點時發生錯誤: {e}")
            return None
    
    def find_direct_routes(self, 
                          start_station: BusStation, 
                          end_station: BusStation,
                          departure_time: time = None) -> List[BusRouteOption]:
        """
        尋找直達路線
        
        Args:
            start_station: 起點站
            end_station: 終點站
            departure_time: 出發時間
            
        Returns:
            直達路線選項列表
        """
        try:
            # 檢查是否在同一路線
            if start_station.route_id != end_station.route_id:
                return []
            
            # 檢查方向是否一致
            if start_station.direction != end_station.direction:
                return []
            
            # 檢查站序順序
            if start_station.sequence >= end_station.sequence:
                return []
            
            route = self.session.query(BusRoute).filter(
                BusRoute.id == start_station.route_id
            ).first()
            
            if not route:
                return []
            
            # 尋找符合條件的班次
            trips = self.session.query(BusTrip).filter(
                BusTrip.route_id == start_station.route_id,
                BusTrip.direction == start_station.direction
            )
            
            if departure_time:
                trips = trips.filter(BusTrip.departure_time >= departure_time)
            
            trips = trips.order_by(BusTrip.departure_time).limit(10).all()
            
            options = []
            for trip in trips:
                # 取得起點和終點的時刻
                start_time = self.session.query(BusStopTime).filter(
                    BusStopTime.trip_id == trip.id,
                    BusStopTime.station_id == start_station.id
                ).first()
                
                end_time = self.session.query(BusStopTime).filter(
                    BusStopTime.trip_id == trip.id,
                    BusStopTime.station_id == end_station.id
                ).first()
                
                if start_time and end_time:
                    # 計算行車時間
                    start_datetime = datetime.combine(datetime.today(), start_time.departure_time)
                    end_datetime = datetime.combine(datetime.today(), end_time.arrival_time)
                    duration = (end_datetime - start_datetime).total_seconds() / 60
                    
                    option = BusRouteOption(
                        route_name=route.route_name,
                        departure_station=start_station.station_name,
                        destination_station=end_station.station_name,
                        departure_time=start_time.departure_time,
                        arrival_time=end_time.arrival_time,
                        duration_minutes=int(duration),
                        transfers=[],
                        walking_distance_meters=0,
                        is_low_floor=trip.is_low_floor,
                        operating_days=trip.operating_days or []
                    )
                    options.append(option)
            
            return options
            
        except Exception as e:
            logger.error(f"尋找直達路線時發生錯誤: {e}")
            return []
    
    def find_transfer_routes(self, 
                           start_station: BusStation, 
                           end_station: BusStation,
                           departure_time: time = None) -> List[BusRouteOption]:
        """
        尋找轉乘路線（簡化版本，實際實現會更複雜）
        
        Args:
            start_station: 起點站
            end_station: 終點站
            departure_time: 出發時間
            
        Returns:
            轉乘路線選項列表
        """
        # 這裡實現簡化的轉乘邏輯
        # 實際應用中需要更複雜的演算法
        logger.info("轉乘路線搜尋功能尚未完全實現")
        return []
    
    def plan_route(self, 
                  start_lon: float, 
                  start_lat: float, 
                  end_lon: float, 
                  end_lat: float,
                  departure_time: time = None,
                  max_walking_distance: int = 500) -> Optional[RoutePlan]:
        """
        規劃從起點到終點的完整路線
        
        Args:
            start_lon: 起點經度
            start_lat: 起點緯度
            end_lon: 終點經度
            end_lat: 終點緯度
            departure_time: 出發時間
            max_walking_distance: 最大步行距離
            
        Returns:
            路線規劃結果
        """
        try:
            # 尋找附近的公車站點
            start_stations = self.find_nearby_stations(start_lon, start_lat, max_walking_distance)
            end_stations = self.find_nearby_stations(end_lon, end_lat, max_walking_distance)
            
            if not start_stations or not end_stations:
                logger.warning("找不到合適的公車站點")
                return None
            
            # 嘗試尋找直達路線
            all_options = []
            for start_station in start_stations[:3]:  # 限制搜尋範圍
                for end_station in end_stations[:3]:
                    direct_routes = self.find_direct_routes(start_station, end_station, departure_time)
                    all_options.extend(direct_routes)
            
            if not all_options:
                # 如果沒有直達路線，嘗試轉乘路線
                for start_station in start_stations[:2]:
                    for end_station in end_stations[:2]:
                        transfer_routes = self.find_transfer_routes(start_station, end_station, departure_time)
                        all_options.extend(transfer_routes)
            
            if not all_options:
                logger.warning("找不到合適的公車路線")
                return None
            
            # 選擇最佳路線（這裡簡化為選擇第一個）
            best_option = all_options[0]
            
            # 計算步行距離和時間
            start_walking_distance = self._calculate_walking_distance(
                start_lon, start_lat, 
                start_stations[0].geom.ST_X(), start_stations[0].geom.ST_Y()
            )
            end_walking_distance = self._calculate_walking_distance(
                end_stations[0].geom.ST_X(), end_stations[0].geom.ST_Y(),
                end_lon, end_lat
            )
            
            total_walking_distance = start_walking_distance + end_walking_distance
            walking_duration = total_walking_distance / 80  # 假設步行速度 80m/min
            
            # 計算總時間
            total_duration = walking_duration + best_option.duration_minutes
            
            # 構建路線摘要
            summary = f"步行 {start_walking_distance:.0f}m 到 {best_option.departure_station}，"
            summary += f"搭乘 {best_option.route_name} 約 {best_option.duration_minutes} 分鐘，"
            summary += f"在 {best_option.destination_station} 下車，"
            summary += f"步行 {end_walking_distance:.0f}m 到目的地"
            
            return RoutePlan(
                total_duration_minutes=int(total_duration),
                total_distance_meters=int(total_walking_distance),
                walking_duration_minutes=int(walking_duration),
                bus_options=[best_option],
                route_geometry=[],  # 這裡可以整合 OSRM 取得詳細路線
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"規劃路線時發生錯誤: {e}")
            return None
    
    def _calculate_walking_distance(self, 
                                  start_lon: float, 
                                  start_lat: float,
                                  end_lon: float, 
                                  end_lat: float) -> float:
        """
        計算兩點間的步行距離
        
        Args:
            start_lon: 起點經度
            start_lat: 起點緯度
            end_lon: 終點經度
            end_lat: 終點緯度
            
        Returns:
            步行距離 (公尺)
        """
        try:
            # 使用 OSRM 計算步行距離
            if self.osrm_service and self.osrm_service.is_service_running():
                route_result = self.osrm_service.route_between_points(
                    start_lon, start_lat, end_lon, end_lat, profile="walking"
                )
                if route_result:
                    return route_result.distance
            
            # 如果 OSRM 不可用，使用簡化的直線距離計算
            # 這裡使用 Haversine 公式的簡化版本
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lon1, lat1, lon2, lat2):
                # 將十進制度數轉化為弧度
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                
                # Haversine 公式
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                r = 6371  # 地球平均半徑，單位為公里
                return c * r * 1000  # 轉換為公尺
            
            return haversine(start_lon, start_lat, end_lon, end_lat)
            
        except Exception as e:
            logger.error(f"計算步行距離時發生錯誤: {e}")
            return 0
    
    def get_route_schedule(self, 
                          route_name: str, 
                          direction: int = 0,
                          date: datetime = None) -> List[Dict]:
        """
        取得路線時刻表
        
        Args:
            route_name: 路線名稱
            direction: 方向 (0: 去程, 1: 回程)
            date: 查詢日期
            
        Returns:
            時刻表資料列表
        """
        try:
            route = self.session.query(BusRoute).filter(
                BusRoute.route_name == route_name
            ).first()
            
            if not route:
                return []
            
            trips = self.session.query(BusTrip).filter(
                BusTrip.route_id == route.id,
                BusTrip.direction == direction
            ).order_by(BusTrip.departure_time).all()
            
            schedule = []
            for trip in trips:
                # 檢查營運日
                if date and trip.operating_days:
                    weekday = date.strftime('%A')
                    if weekday not in trip.operating_days:
                        continue
                
                schedule.append({
                    'trip_id': trip.trip_id,
                    'departure_time': trip.departure_time.strftime('%H:%M'),
                    'departure_station': trip.departure_station,
                    'is_low_floor': trip.is_low_floor,
                    'operating_days': trip.operating_days
                })
            
            return schedule
            
        except Exception as e:
            logger.error(f"取得時刻表時發生錯誤: {e}")
            return []

