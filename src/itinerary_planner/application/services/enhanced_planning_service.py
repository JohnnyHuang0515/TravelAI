"""
增強版行程規劃服務
整合交通工具偏好和智能交通規劃
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, time, date, timedelta

from ...domain.models.itinerary import Itinerary, Day, Visit, Accommodation
from ...domain.models.story import Story
from ...domain.models.transport_preference import (
    TransportPreference, TransportMode, TransportType, 
    PlanningContext, TransportPreferenceManager
)
from ...infrastructure.persistence.orm_models import Place
from .smart_transport_planner import SmartTransportPlanner, PlanningContext as TransportPlanningContext
from .bus_routing_service import BusRoutingService
from ..routing.osrm_service import get_osrm_manager

logger = logging.getLogger(__name__)

class EnhancedPlanningService:
    """增強版行程規劃服務"""
    
    def __init__(self, bus_service: BusRoutingService = None):
        """
        初始化增強版行程規劃服務
        
        Args:
            bus_service: 公車路線規劃服務
        """
        self.bus_service = bus_service
        self.transport_planner = SmartTransportPlanner(bus_service, get_osrm_manager().get_service())
        self.preference_manager = TransportPreferenceManager()
    
    def plan_itinerary_with_transport(
        self,
        story: Story,
        candidates: List[Place],
        transport_preference: Optional[TransportPreference] = None,
        user_transport_choice: str = "mixed"
    ) -> Itinerary:
        """
        根據交通工具偏好規劃行程
        
        Args:
            story: 用戶故事
            candidates: 候選景點
            transport_preference: 交通工具偏好
            user_transport_choice: 用戶選擇的交通方式
            
        Returns:
            包含交通規劃的行程
        """
        try:
            # 如果沒有提供偏好，根據用戶選擇建立
            if not transport_preference:
                transport_preference = self.preference_manager.create_preference_from_user_input(
                    user_transport_choice
                )
            
            logger.info(f"使用交通偏好: {transport_preference.primary_mode.value}")
            
            # 執行基礎行程規劃
            itinerary = self._plan_basic_itinerary(story, candidates)
            
            # 為每一天規劃詳細的交通
            for day in itinerary.days:
                self._enhance_day_with_transport(day, transport_preference, story)
            
            return itinerary
            
        except Exception as e:
            logger.error(f"規劃行程時發生錯誤: {e}")
            # 回退到基礎規劃
            return self._plan_basic_itinerary(story, candidates)
    
    def _plan_basic_itinerary(self, story: Story, candidates: List[Place]) -> Itinerary:
        """執行基礎行程規劃（不包含詳細交通）"""
        from .planning_service import GreedyPlanner
        
        # 使用現有的貪婪規劃器
        planner = GreedyPlanner()
        
        # 建立簡化的交通時間矩陣（使用直線距離估算）
        travel_matrix = self._create_simple_travel_matrix(candidates)
        
        return planner.plan(story, candidates, travel_matrix)
    
    def _enhance_day_with_transport(
        self, 
        day: Day, 
        transport_preference: TransportPreference, 
        story: Story
    ):
        """為行程天數增強交通規劃"""
        try:
            if len(day.visits) < 2:
                return  # 只有一個景點，不需要交通規劃
            
            # 建立規劃上下文
            context = TransportPlanningContext(
                start_time=self._parse_time_to_time(story.daily_window.start) if story.daily_window else time(9, 0),
                end_time=self._parse_time_to_time(story.daily_window.end) if story.daily_window else time(18, 0),
                date=story.date_range[0] if story.date_range else date.today(),
                weather_condition="normal",
                traffic_condition="normal"
            )
            
            # 規劃交通
            transport_plans = self.transport_planner.plan_day_transport(
                day.visits, transport_preference, context
            )
            
            # 將交通資訊整合到行程中
            self._integrate_transport_into_day(day, transport_plans, transport_preference)
            
        except Exception as e:
            logger.error(f"為第 {day.day_number} 天規劃交通時發生錯誤: {e}")
    
    def _integrate_transport_into_day(
        self, 
        day: Day, 
        transport_plans: List, 
        transport_preference: TransportPreference
    ):
        """將交通規劃整合到行程天數中"""
        
        # 為每個 Visit 添加交通資訊
        for i, visit in enumerate(day.visits):
            if i == 0:
                # 第一個景點，設定出發時間
                visit.arrival_time = self._parse_time_to_time(day.start_time)
                visit.departure_time = self._add_minutes_to_time(
                    visit.arrival_time, 
                    visit.stay_minutes or 60
                )
            else:
                # 後續景點，根據交通規劃設定時間
                if i - 1 < len(transport_plans):
                    transport_plan = transport_plans[i - 1]
                    
                    # 設定到達時間
                    if transport_plan.segments:
                        last_segment = transport_plan.segments[-1]
                        if last_segment.arrival_time:
                            visit.arrival_time = last_segment.arrival_time
                        else:
                            # 如果沒有具體時間，使用估算
                            prev_departure = day.visits[i-1].departure_time
                            travel_minutes = transport_plan.total_duration // 60
                            visit.arrival_time = self._add_minutes_to_time(prev_departure, travel_minutes)
                    
                    # 設定離開時間
                    visit.departure_time = self._add_minutes_to_time(
                        visit.arrival_time, 
                        visit.stay_minutes or 60
                    )
                    
                    # 添加交通摘要到景點描述
                    self._add_transport_summary_to_visit(visit, transport_plan)
    
    def _add_transport_summary_to_visit(self, visit: Visit, transport_plan):
        """為景點添加交通摘要"""
        if not transport_plan:
            return
        
        # 建立交通摘要
        transport_summary = self._create_transport_summary(transport_plan)
        
        # 添加到景點描述
        if visit.place.description:
            visit.place.description += f"\n\n交通資訊: {transport_summary}"
        else:
            visit.place.description = f"交通資訊: {transport_summary}"
    
    def _create_transport_summary(self, transport_plan) -> str:
        """建立交通摘要文字"""
        if not transport_plan.segments:
            return "無交通資訊"
        
        summary_parts = []
        
        for segment in transport_plan.segments:
            duration_min = segment.duration // 60
            distance_km = segment.distance / 1000
            
            if segment.mode.value == "driving":
                summary_parts.append(f"開車 {duration_min}分鐘 ({distance_km:.1f}公里)")
            elif segment.mode.value == "public_transport":
                if segment.type == TransportType.BUS:
                    summary_parts.append(f"搭公車 {duration_min}分鐘")
                elif segment.type == TransportType.TRAIN:
                    summary_parts.append(f"搭火車 {duration_min}分鐘")
            elif segment.mode.value == "walking":
                summary_parts.append(f"步行 {duration_min}分鐘 ({distance_km:.1f}公里)")
        
        # 添加總體資訊
        total_duration = transport_plan.total_duration // 60
        total_cost = transport_plan.total_cost
        
        summary = f"{' → '.join(summary_parts)} (總時間: {total_duration}分鐘"
        if total_cost > 0:
            summary += f", 費用: ${total_cost:.0f}"
        summary += ")"
        
        return summary
    
    def _create_simple_travel_matrix(self, candidates: List[Place]) -> List[List[float]]:
        """建立簡化的交通時間矩陣"""
        matrix = []
        
        for i, place1 in enumerate(candidates):
            row = []
            for j, place2 in enumerate(candidates):
                if i == j:
                    row.append(0.0)
                else:
                    # 計算直線距離並轉換為時間估算
                    distance = self._calculate_straight_distance(
                        (place1.geom.ST_X(), place1.geom.ST_Y()),
                        (place2.geom.ST_X(), place2.geom.ST_Y())
                    )
                    # 假設平均時速 30km/h (500m/分鐘)
                    time_minutes = distance / 500.0
                    row.append(time_minutes)
            matrix.append(row)
        
        return matrix
    
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
    
    def _parse_time_to_time(self, time_str: str) -> time:
        """解析時間字串為 time 物件"""
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except:
            return time(9, 0)  # 預設時間
    
    def _add_minutes_to_time(self, base_time: time, minutes: int) -> time:
        """將分鐘加到時間上"""
        base_datetime = datetime.combine(datetime.today(), base_time)
        new_datetime = base_datetime + timedelta(minutes=minutes)
        return new_datetime.time()
    
    def get_transport_options_for_story(self, story: Story) -> List[Dict[str, Any]]:
        """根據故事內容推薦交通工具選項"""
        options = []
        
        # 分析故事內容
        destination = story.destination.lower() if story.destination else ""
        interests = story.interests or []
        
        # 根據目的地和興趣推薦
        if "山" in destination or "登山" in interests:
            options.append({
                "name": "開車",
                "value": "driving",
                "description": "適合山區景點，彈性高，可攜帶裝備",
                "icon": "🚗"
            })
        
        if "市區" in destination or "文化" in interests or "歷史" in interests:
            options.append({
                "name": "大眾運輸",
                "value": "public_transport",
                "description": "適合市區景點，環保經濟，體驗當地生活",
                "icon": "🚌"
            })
        
        if "生態" in interests or "環保" in interests:
            options.append({
                "name": "環保出行",
                "value": "eco_friendly",
                "description": "優先使用大眾運輸和步行，減少碳排放",
                "icon": "🌱"
            })
        
        # 預設選項
        if not options:
            options = [
                {
                    "name": "開車",
                    "value": "driving",
                    "description": "彈性高，適合遠距離景點",
                    "icon": "🚗"
                },
                {
                    "name": "大眾運輸",
                    "value": "public_transport",
                    "description": "經濟環保，體驗當地交通",
                    "icon": "🚌"
                },
                {
                    "name": "混合模式",
                    "value": "mixed",
                    "description": "智能選擇最佳交通方式",
                    "icon": "🔄"
                }
            ]
        
        return options
    
    def estimate_transport_impact(
        self, 
        itinerary: Itinerary, 
        transport_preference: TransportPreference
    ) -> Dict[str, Any]:
        """估算交通對行程的影響"""
        total_cost = 0.0
        total_carbon = 0.0
        total_driving_time = 0
        total_walking_time = 0
        
        for day in itinerary.days:
            for i in range(len(day.visits) - 1):
                start_place = day.visits[i].place
                end_place = day.visits[i + 1].place
                
                # 簡化估算
                distance = self._calculate_straight_distance(
                    (start_place.geom.ST_X(), start_place.geom.ST_Y()),
                    (end_place.geom.ST_X(), end_place.geom.ST_Y())
                )
                
                if transport_preference.primary_mode == TransportMode.DRIVING:
                    total_cost += distance / 1000 * 3.0  # 油錢
                    total_carbon += distance / 1000 * 0.12  # 碳排放
                    total_driving_time += int(distance / 500)  # 開車時間
                elif transport_preference.primary_mode == TransportMode.PUBLIC_TRANSPORT:
                    total_cost += 15.0  # 公車票價
                    total_carbon += distance / 1000 * 0.08  # 碳排放
                    total_walking_time += 10  # 步行時間
                else:
                    total_cost += distance / 1000 * 1.5  # 混合成本
                    total_carbon += distance / 1000 * 0.1  # 碳排放
        
        return {
            "total_cost": round(total_cost, 2),
            "total_carbon_emission": round(total_carbon, 2),
            "total_driving_time_minutes": total_driving_time,
            "total_walking_time_minutes": total_walking_time,
            "transport_efficiency": "high" if total_carbon < 5 else "medium" if total_carbon < 10 else "low"
        }
