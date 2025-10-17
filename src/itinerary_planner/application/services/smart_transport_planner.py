"""
智能交通規劃服務
根據交通工具偏好智能規劃行程中的交通方式
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, time, timedelta
from dataclasses import dataclass

from ...domain.models.transport_preference import (
    TransportMode, TransportType, TransportPreference, 
    TransportSegment, TransportPlan, DEFAULT_PREFERENCES
)
from ...domain.models.itinerary import Day, Visit
from ..routing.osrm_service import OSRMService, get_osrm_manager
from ..routing.bus_routing_service import BusRoutingService
from ...infrastructure.persistence.orm_models import Place

logger = logging.getLogger(__name__)

@dataclass
class PlanningContext:
    """規劃上下文"""
    start_time: time                    # 出發時間
    end_time: time                      # 結束時間
    date: datetime                      # 日期
    weather_condition: str = "normal"   # 天氣狀況
    traffic_condition: str = "normal"   # 交通狀況

class SmartTransportPlanner:
    """智能交通規劃器"""
    
    def __init__(self, bus_service: BusRoutingService = None, osrm_service: OSRMService = None):
        """
        初始化智能交通規劃器
        
        Args:
            bus_service: 公車路線規劃服務
            osrm_service: OSRM 路由服務
        """
        self.bus_service = bus_service
        self.osrm_service = osrm_service or get_osrm_manager().get_service()
    
    def plan_transport_between_places(
        self,
        start_place: Place,
        end_place: Place,
        preference: TransportPreference,
        context: PlanningContext
    ) -> Optional[TransportPlan]:
        """
        規劃兩個景點間的交通
        
        Args:
            start_place: 起點景點
            end_place: 終點景點
            preference: 交通工具偏好
            context: 規劃上下文
            
        Returns:
            交通規劃結果
        """
        try:
            # 提取座標
            start_coords = (start_place.geom.ST_X(), start_place.geom.ST_Y())
            end_coords = (end_place.geom.ST_X(), end_place.geom.ST_Y())
            
            # 計算直線距離
            distance = self._calculate_straight_distance(start_coords, end_coords)
            
            # 根據偏好選擇規劃策略
            if preference.primary_mode == TransportMode.DRIVING:
                return self._plan_driving_route(start_coords, end_coords, preference, context)
            elif preference.primary_mode == TransportMode.PUBLIC_TRANSPORT:
                return self._plan_public_transport_route(
                    start_coords, end_coords, preference, context
                )
            elif preference.primary_mode == TransportMode.MIXED:
                return self._plan_mixed_route(start_coords, end_coords, preference, context)
            else:
                return self._plan_walking_route(start_coords, end_coords, preference, context)
                
        except Exception as e:
            logger.error(f"規劃交通時發生錯誤: {e}")
            return None
    
    def _plan_driving_route(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        preference: TransportPreference,
        context: PlanningContext
    ) -> Optional[TransportPlan]:
        """規劃開車路線"""
        try:
            # 使用 OSRM 計算開車路線
            route_result = self.osrm_service.route_between_points(
                start_coords[0], start_coords[1],
                end_coords[0], end_coords[1],
                profile="driving"
            )
            
            if not route_result:
                # 如果 OSRM 不可用，使用簡化計算
                distance = self._calculate_straight_distance(start_coords, end_coords)
                duration = int(distance / 1000 * 60)  # 假設平均時速 60km/h
            else:
                distance = route_result.distance
                duration = int(route_result.duration)
            
            # 考慮交通狀況調整時間
            if context.traffic_condition == "heavy":
                duration = int(duration * 1.5)
            elif context.traffic_condition == "light":
                duration = int(duration * 0.9)
            
            # 建立開車路段
            segment = TransportSegment(
                mode=TransportMode.DRIVING,
                type=TransportType.CAR,
                start_coords=start_coords,
                end_coords=end_coords,
                distance=distance,
                duration=duration,
                cost=self._calculate_driving_cost(distance),
                departure_time=context.start_time,
                arrival_time=self._add_minutes_to_time(context.start_time, duration // 60)
            )
            
            return TransportPlan(
                segments=[segment],
                total_distance=distance,
                total_duration=duration,
                total_cost=segment.cost,
                total_driving_time=duration,
                carbon_emission=self._calculate_carbon_emission(distance, "car")
            )
            
        except Exception as e:
            logger.error(f"規劃開車路線時發生錯誤: {e}")
            return None
    
    def _plan_public_transport_route(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        preference: TransportPreference,
        context: PlanningContext
    ) -> Optional[TransportPlan]:
        """規劃大眾運輸路線"""
        try:
            if not self.bus_service:
                logger.warning("公車服務不可用，回退到步行路線")
                return self._plan_walking_route(start_coords, end_coords, preference, context)
            
            # 使用公車路線規劃服務
            route_plan = self.bus_service.plan_route(
                start_coords[0], start_coords[1],
                end_coords[0], end_coords[1],
                context.start_time,
                preference.constraints.max_walking_distance
            )
            
            if not route_plan:
                # 如果沒有公車路線，嘗試步行
                return self._plan_walking_route(start_coords, end_coords, preference, context)
            
            # 轉換為 TransportPlan
            segments = []
            total_cost = 0.0
            
            # 步行到公車站
            if route_plan.total_distance > 0:
                walking_segment = TransportSegment(
                    mode=TransportMode.WALKING,
                    type=TransportType.WALKING,
                    start_coords=start_coords,
                    end_coords=start_coords,  # 簡化處理
                    distance=route_plan.total_distance,
                    duration=route_plan.walking_duration_minutes * 60,
                    departure_time=context.start_time
                )
                segments.append(walking_segment)
            
            # 公車路段
            for bus_option in route_plan.bus_options:
                # 計算公車路段距離 (簡化)
                bus_distance = 1000  # 假設平均 1 公里
                
                bus_segment = TransportSegment(
                    mode=TransportMode.PUBLIC_TRANSPORT,
                    type=TransportType.BUS,
                    start_coords=start_coords,  # 簡化
                    end_coords=end_coords,      # 簡化
                    distance=bus_distance,
                    duration=bus_option.duration_minutes * 60,
                    cost=15.0,  # 公車票價
                    departure_time=bus_option.departure_time,
                    arrival_time=bus_option.arrival_time
                )
                segments.append(bus_segment)
                total_cost += bus_segment.cost
            
            return TransportPlan(
                segments=segments,
                total_distance=route_plan.total_distance + sum(s.distance for s in segments[1:]),
                total_duration=route_plan.total_duration_minutes * 60,
                total_cost=total_cost,
                total_walking_time=route_plan.walking_duration_minutes * 60,
                transfer_count=len(route_plan.bus_options) - 1,
                carbon_emission=self._calculate_carbon_emission(
                    sum(s.distance for s in segments[1:]), "bus"
                )
            )
            
        except Exception as e:
            logger.error(f"規劃大眾運輸路線時發生錯誤: {e}")
            return None
    
    def _plan_mixed_route(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        preference: TransportPreference,
        context: PlanningContext
    ) -> Optional[TransportPlan]:
        """規劃混合路線"""
        try:
            # 計算距離
            distance = self._calculate_straight_distance(start_coords, end_coords)
            
            # 根據距離決定主要交通方式
            if distance > 5000:  # 超過 5 公里，優先考慮開車
                driving_plan = self._plan_driving_route(start_coords, end_coords, preference, context)
                if driving_plan:
                    return driving_plan
            
            # 嘗試大眾運輸
            public_plan = self._plan_public_transport_route(start_coords, end_coords, preference, context)
            if public_plan and public_plan.total_duration < driving_plan.total_duration * 1.5:
                return public_plan
            
            # 回退到開車
            return driving_plan or self._plan_driving_route(start_coords, end_coords, preference, context)
            
        except Exception as e:
            logger.error(f"規劃混合路線時發生錯誤: {e}")
            return None
    
    def _plan_walking_route(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        preference: TransportPreference,
        context: PlanningContext
    ) -> Optional[TransportPlan]:
        """規劃步行路線"""
        try:
            distance = self._calculate_straight_distance(start_coords, end_coords)
            
            # 檢查是否超過步行限制
            if distance > preference.constraints.max_walking_distance:
                logger.warning(f"步行距離 {distance}m 超過限制 {preference.constraints.max_walking_distance}m")
                return None
            
            # 計算步行時間
            duration = int(distance / preference.constraints.walking_speed * 60)
            
            segment = TransportSegment(
                mode=TransportMode.WALKING,
                type=TransportType.WALKING,
                start_coords=start_coords,
                end_coords=end_coords,
                distance=distance,
                duration=duration,
                departure_time=context.start_time,
                arrival_time=self._add_minutes_to_time(context.start_time, duration // 60)
            )
            
            return TransportPlan(
                segments=[segment],
                total_distance=distance,
                total_duration=duration,
                total_cost=0.0,
                total_walking_time=duration
            )
            
        except Exception as e:
            logger.error(f"規劃步行路線時發生錯誤: {e}")
            return None
    
    def plan_day_transport(
        self,
        day_visits: List[Visit],
        preference: TransportPreference,
        context: PlanningContext
    ) -> List[TransportPlan]:
        """
        規劃一天的交通
        
        Args:
            day_visits: 當天的景點訪問列表
            preference: 交通工具偏好
            context: 規劃上下文
            
        Returns:
            交通規劃列表
        """
        transport_plans = []
        current_time = context.start_time
        
        for i in range(len(day_visits) - 1):
            start_visit = day_visits[i]
            end_visit = day_visits[i + 1]
            
            # 建立當前時間上下文
            current_context = PlanningContext(
                start_time=current_time,
                end_time=context.end_time,
                date=context.date,
                weather_condition=context.weather_condition,
                traffic_condition=context.traffic_condition
            )
            
            # 規劃交通
            transport_plan = self.plan_transport_between_places(
                start_visit.place, end_visit.place, preference, current_context
            )
            
            if transport_plan:
                transport_plans.append(transport_plan)
                
                # 更新當前時間 (考慮景點停留時間)
                arrival_time = transport_plan.segments[-1].arrival_time
                if arrival_time:
                    # 加上景點停留時間
                    stay_time = end_visit.stay_minutes or 60
                    current_time = self._add_minutes_to_time(arrival_time, stay_time)
            else:
                logger.warning(f"無法規劃從 {start_visit.place.name} 到 {end_visit.place.name} 的交通")
        
        return transport_plans
    
    def _calculate_straight_distance(
        self, 
        start_coords: Tuple[float, float], 
        end_coords: Tuple[float, float]
    ) -> float:
        """計算直線距離"""
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # 地球半徑 (公里)
            return c * r * 1000  # 轉換為公尺
        
        return haversine(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
    
    def _calculate_driving_cost(self, distance: float) -> float:
        """計算開車成本"""
        # 簡化的成本計算：油錢 + 過路費
        fuel_cost = distance / 1000 * 3.0  # 每公里 3 元油錢
        toll_cost = max(0, (distance - 10000) / 1000 * 5.0)  # 超過 10 公里每公里 5 元過路費
        return fuel_cost + toll_cost
    
    def _calculate_carbon_emission(self, distance: float, transport_type: str) -> float:
        """計算碳排放量"""
        # 簡化的碳排放計算 (kg CO2)
        emission_factors = {
            "car": 0.12,      # 每公里 0.12 kg CO2
            "bus": 0.08,      # 每公里 0.08 kg CO2
            "train": 0.05,    # 每公里 0.05 kg CO2
            "walking": 0.0,   # 步行無排放
            "cycling": 0.0    # 騎車無排放
        }
        
        factor = emission_factors.get(transport_type, 0.1)
        return distance / 1000 * factor
    
    def _add_minutes_to_time(self, base_time: time, minutes: int) -> time:
        """將分鐘加到時間上"""
        base_datetime = datetime.combine(datetime.today(), base_time)
        new_datetime = base_datetime + timedelta(minutes=minutes)
        return new_datetime.time()

class TransportPreferenceManager:
    """交通工具偏好管理器"""
    
    def __init__(self):
        self.preferences = DEFAULT_PREFERENCES.copy()
    
    def get_preference(self, name: str) -> Optional[TransportPreference]:
        """取得偏好設定"""
        return self.preferences.get(name)
    
    def create_preference_from_user_input(
        self,
        primary_mode: str,
        accessibility_needs: List[str] = None,
        budget: str = "medium",
        eco_friendly: bool = False
    ) -> TransportPreference:
        """根據用戶輸入建立偏好設定"""
        
        # 解析主要交通模式
        mode_mapping = {
            "開車": TransportMode.DRIVING,
            "大眾運輸": TransportMode.PUBLIC_TRANSPORT,
            "混合": TransportMode.MIXED,
            "環保": TransportMode.PUBLIC_TRANSPORT
        }
        
        primary_transport_mode = mode_mapping.get(primary_mode, TransportMode.MIXED)
        
        # 取得基礎偏好
        base_preference = self.preferences.get(primary_transport_mode.value, self.preferences["mixed"])
        
        # 建立自訂偏好
        custom_preference = TransportPreference(
            primary_mode=primary_transport_mode,
            primary_type=base_preference.primary_type,
            secondary_modes=base_preference.secondary_modes,
            optimization=base_preference.optimization,
            constraints=base_preference.constraints,
            accessibility_needs=accessibility_needs or [],
            budget_preference=budget,
            eco_friendly=eco_friendly or primary_mode == "環保"
        )
        
        # 根據特殊需求調整約束條件
        if accessibility_needs and "輪椅" in accessibility_needs:
            custom_preference.constraints.prefer_low_floor_bus = True
            custom_preference.constraints.max_walking_distance = 300.0
        
        if budget == "low":
            custom_preference.optimization = RouteOptimization.ECONOMIC
        elif budget == "high":
            custom_preference.constraints.avoid_transfers = True
        
        return custom_preference
