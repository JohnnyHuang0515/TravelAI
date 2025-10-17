"""
交通工具偏好模型
定義不同交通工具的偏好設定和規劃策略
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import time, timedelta

class TransportMode(Enum):
    """交通工具模式"""
    DRIVING = "driving"           # 開車
    PUBLIC_TRANSPORT = "public_transport"  # 大眾運輸
    MIXED = "mixed"              # 混合模式
    WALKING = "walking"          # 步行
    CYCLING = "cycling"          # 騎自行車

class TransportType(Enum):
    """交通工具類型"""
    CAR = "car"                  # 汽車
    MOTORCYCLE = "motorcycle"    # 機車
    BUS = "bus"                  # 公車
    TRAIN = "train"              # 火車
    TAXI = "taxi"                # 計程車
    WALKING = "walking"          # 步行
    BICYCLE = "bicycle"          # 自行車

class RouteOptimization(Enum):
    """路線優化策略"""
    FASTEST = "fastest"          # 最快路線
    SHORTEST = "shortest"        # 最短距離
    SCENIC = "scenic"            # 風景路線
    ECONOMIC = "economic"        # 經濟路線
    ACCESSIBLE = "accessible"    # 無障礙路線

@dataclass
class TransportConstraints:
    """交通工具約束條件"""
    max_walking_distance: float = 500.0      # 最大步行距離 (公尺)
    max_walking_time: int = 10               # 最大步行時間 (分鐘)
    prefer_low_floor_bus: bool = True        # 偏好低地板公車
    avoid_transfers: bool = False            # 避免轉乘
    max_transfers: int = 2                   # 最大轉乘次數
    walking_speed: float = 80.0              # 步行速度 (公尺/分鐘)
    max_daily_driving_time: int = 480        # 最大每日開車時間 (分鐘)
    rest_stop_interval: int = 120            # 休息站間隔 (分鐘)

@dataclass
class TransportPreference:
    """交通工具偏好設定"""
    primary_mode: TransportMode              # 主要交通模式
    primary_type: TransportType              # 主要交通工具類型
    secondary_modes: List[TransportMode]     # 次要交通模式
    optimization: RouteOptimization          # 路線優化策略
    constraints: TransportConstraints        # 約束條件
    accessibility_needs: List[str] = None    # 無障礙需求
    budget_preference: str = "medium"        # 預算偏好 (low/medium/high)
    eco_friendly: bool = False               # 環保偏好
    
    def __post_init__(self):
        if self.accessibility_needs is None:
            self.accessibility_needs = []

@dataclass
class TransportSegment:
    """交通路段"""
    mode: TransportMode                      # 交通模式
    type: TransportType                      # 交通工具類型
    start_coords: Tuple[float, float]        # 起點座標 (lon, lat)
    end_coords: Tuple[float, float]          # 終點座標 (lon, lat)
    distance: float                          # 距離 (公尺)
    duration: int                            # 時間 (秒)
    cost: float = 0.0                        # 費用 (台幣)
    instructions: List[str] = None           # 導航指示
    departure_time: Optional[time] = None    # 出發時間
    arrival_time: Optional[time] = None      # 到達時間
    
    def __post_init__(self):
        if self.instructions is None:
            self.instructions = []

@dataclass
class TransportPlan:
    """交通規劃結果"""
    segments: List[TransportSegment]         # 交通路段列表
    total_distance: float                    # 總距離 (公尺)
    total_duration: int                      # 總時間 (秒)
    total_cost: float                        # 總費用 (台幣)
    total_walking_time: int = 0              # 總步行時間 (秒)
    total_driving_time: int = 0              # 總開車時間 (秒)
    transfer_count: int = 0                  # 轉乘次數
    carbon_emission: float = 0.0             # 碳排放量 (kg CO2)
    
    @property
    def summary(self) -> str:
        """取得路線摘要"""
        duration_min = self.total_duration / 60
        distance_km = self.total_distance / 1000
        
        if duration_min < 60:
            duration_text = f"{duration_min:.0f}分鐘"
        else:
            hours = int(duration_min // 60)
            minutes = int(duration_min % 60)
            duration_text = f"{hours}小時{minutes}分鐘"
        
        segments_summary = []
        for segment in self.segments:
            if segment.mode == TransportMode.DRIVING:
                segments_summary.append(f"開車 {segment.duration//60}分鐘")
            elif segment.mode == TransportMode.PUBLIC_TRANSPORT:
                if segment.type == TransportType.BUS:
                    segments_summary.append(f"搭公車 {segment.duration//60}分鐘")
                elif segment.type == TransportType.TRAIN:
                    segments_summary.append(f"搭火車 {segment.duration//60}分鐘")
            elif segment.mode == TransportMode.WALKING:
                segments_summary.append(f"步行 {segment.duration//60}分鐘")
        
        return f"距離 {distance_km:.1f}公里，時間 {duration_text}，包含 {', '.join(segments_summary)}"

# 預設交通工具偏好配置
DEFAULT_PREFERENCES = {
    "driving": TransportPreference(
        primary_mode=TransportMode.DRIVING,
        primary_type=TransportType.CAR,
        secondary_modes=[TransportMode.WALKING],
        optimization=RouteOptimization.FASTEST,
        constraints=TransportConstraints(
            max_walking_distance=200.0,
            max_walking_time=5,
            max_daily_driving_time=480,
            rest_stop_interval=120
        )
    ),
    
    "public_transport": TransportPreference(
        primary_mode=TransportMode.PUBLIC_TRANSPORT,
        primary_type=TransportType.BUS,
        secondary_modes=[TransportMode.WALKING, TransportMode.TRAIN],
        optimization=RouteOptimization.ECONOMIC,
        constraints=TransportConstraints(
            max_walking_distance=800.0,
            max_walking_time=15,
            prefer_low_floor_bus=True,
            max_transfers=3,
            walking_speed=70.0
        )
    ),
    
    "mixed": TransportPreference(
        primary_mode=TransportMode.MIXED,
        primary_type=TransportType.BUS,
        secondary_modes=[TransportMode.DRIVING, TransportMode.WALKING, TransportMode.TRAIN],
        optimization=RouteOptimization.BALANCED,
        constraints=TransportConstraints(
            max_walking_distance=600.0,
            max_walking_time=10,
            max_transfers=2,
            prefer_low_floor_bus=True
        )
    ),
    
    "eco_friendly": TransportPreference(
        primary_mode=TransportMode.PUBLIC_TRANSPORT,
        primary_type=TransportType.BUS,
        secondary_modes=[TransportMode.WALKING, TransportMode.CYCLING],
        optimization=RouteOptimization.ECONOMIC,
        constraints=TransportConstraints(
            max_walking_distance=1000.0,
            max_walking_time=20,
            prefer_low_floor_bus=True,
            max_transfers=3
        ),
        eco_friendly=True
    )
}

def get_preference_by_name(name: str) -> Optional[TransportPreference]:
    """根據名稱取得預設偏好設定"""
    return DEFAULT_PREFERENCES.get(name)

def create_custom_preference(
    primary_mode: TransportMode,
    primary_type: TransportType,
    **kwargs
) -> TransportPreference:
    """建立自訂偏好設定"""
    
    # 取得預設約束條件
    base_prefs = DEFAULT_PREFERENCES.get(primary_mode.value, DEFAULT_PREFERENCES["mixed"])
    constraints = base_prefs.constraints
    
    # 允許覆蓋約束條件
    if "constraints" in kwargs:
        constraints = kwargs.pop("constraints")
    
    return TransportPreference(
        primary_mode=primary_mode,
        primary_type=primary_type,
        secondary_modes=kwargs.get("secondary_modes", base_prefs.secondary_modes),
        optimization=kwargs.get("optimization", base_prefs.optimization),
        constraints=constraints,
        accessibility_needs=kwargs.get("accessibility_needs", []),
        budget_preference=kwargs.get("budget_preference", "medium"),
        eco_friendly=kwargs.get("eco_friendly", False)
    )
