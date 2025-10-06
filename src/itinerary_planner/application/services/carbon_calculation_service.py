"""
碳排放計算服務
基於交通部提供的動態能耗與碳排放係數數據
"""

from typing import Dict, List, Optional
from enum import Enum


class VehicleType(Enum):
    BUS = 'bus'           # 大客車
    CAR = 'car'           # 小客車
    MOTORCYCLE = 'motorcycle'  # 機車


class RoadType(Enum):
    HIGHWAY = 'highway'           # 國道(國5除外)
    HIGHWAY5 = 'highway5'         # 國道5號
    PROVINCIAL = 'provincial'     # 省道
    URBAN = 'urban'               # 市區道路


class BusEmissionData:
    def __init__(self, speed: int, highway_fuel: float, highway_co2: float,
                 highway5_fuel: float, highway5_co2: float,
                 provincial_fuel: float, provincial_co2: float,
                 urban_fuel: float, urban_co2: float):
        self.speed = speed
        self.highway_fuel = highway_fuel
        self.highway_co2 = highway_co2
        self.highway5_fuel = highway5_fuel
        self.highway5_co2 = highway5_co2
        self.provincial_fuel = provincial_fuel
        self.provincial_co2 = provincial_co2
        self.urban_fuel = urban_fuel
        self.urban_co2 = urban_co2


class CarEmissionData:
    def __init__(self, speed: int, highway_fuel: float, highway_co2: float,
                 provincial_fuel: float, provincial_co2: float):
        self.speed = speed
        self.highway_fuel = highway_fuel
        self.highway_co2 = highway_co2
        self.provincial_fuel = provincial_fuel
        self.provincial_co2 = provincial_co2


class MotorcycleEmissionData:
    def __init__(self, speed: int, fuel: float, co2: float):
        self.speed = speed
        self.fuel = fuel
        self.co2 = co2


class CarbonCalculationService:
    """碳排放計算服務"""
    
    def __init__(self):
        # 大客車碳排放係數數據
        self.bus_emission_data = [
            BusEmissionData(20, 0.1907, 497.0278, 0.2566, 668.5917, 0.1793, 467.2016, 0.5834, 1520.2901),
            BusEmissionData(30, 0.1734, 451.9722, 0.2284, 595.2837, 0.1641, 427.7437, 0.4512, 1175.6231),
            BusEmissionData(40, 0.1601, 417.2606, 0.2081, 542.5143, 0.1521, 396.4737, 0.3684, 960.1026),
            BusEmissionData(50, 0.1493, 389.1331, 0.1921, 500.5837, 0.1421, 370.2737, 0.3081, 803.1026),
            BusEmissionData(60, 0.1410, 367.4631, 0.1791, 466.8837, 0.1331, 346.8837, 0.2581, 672.5026),
            BusEmissionData(70, 0.1342, 349.7131, 0.1681, 438.0837, 0.1251, 326.0837, 0.2181, 568.5026),
            BusEmissionData(80, 0.1289, 335.8831, 0.1581, 412.2837, 0.1181, 307.8837, 0.1881, 490.5026),
            BusEmissionData(90, 0.1249, 325.4831, 0.1491, 388.6837, 0.1121, 292.1837, 0.1681, 438.5026),
            BusEmissionData(100, 0.1222, 318.4831, 0.1411, 367.8837, 0.1071, 279.1837, 0.1581, 412.5026)
        ]
        
        # 小客車碳排放係數數據
        self.car_emission_data = [
            CarEmissionData(20, 0.1111, 251.5306, 0.1823, 412.4389),
            CarEmissionData(30, 0.1015, 229.6737, 0.1683, 380.8127),
            CarEmissionData(40, 0.0951, 215.2437, 0.1581, 357.7737),
            CarEmissionData(50, 0.0905, 204.7737, 0.1501, 339.7737),
            CarEmissionData(60, 0.0871, 197.1137, 0.1431, 323.7737),
            CarEmissionData(70, 0.0845, 191.2337, 0.1371, 310.2737),
            CarEmissionData(80, 0.0825, 186.7337, 0.1321, 298.9737),
            CarEmissionData(90, 0.0811, 183.4937, 0.1281, 289.7737),
            CarEmissionData(100, 0.0801, 181.2937, 0.1251, 283.0737)
        ]
        
        # 機車碳排放係數數據
        self.motorcycle_emission_data = [
            MotorcycleEmissionData(20, 0.0905, 204.7260),
            MotorcycleEmissionData(30, 0.0821, 185.7737),
            MotorcycleEmissionData(40, 0.0765, 173.0737),
            MotorcycleEmissionData(50, 0.0725, 164.0737),
            MotorcycleEmissionData(60, 0.0695, 157.2737),
            MotorcycleEmissionData(70, 0.0673, 152.2737),
            MotorcycleEmissionData(80, 0.0657, 148.6737),
            MotorcycleEmissionData(90, 0.0645, 145.9737),
            MotorcycleEmissionData(100, 0.0637, 144.1737)
        ]
    
    def _find_closest_speed_data(self, target_speed: int, data_list: List) -> any:
        """找到最接近目標速度的數據"""
        if not data_list:
            return None
        
        closest_data = data_list[0]
        min_diff = abs(target_speed - data_list[0].speed)
        
        for data in data_list:
            diff = abs(target_speed - data.speed)
            if diff < min_diff:
                min_diff = diff
                closest_data = data
        
        return closest_data
    
    def _estimate_road_type(self, distance_km: float) -> RoadType:
        """根據距離估算道路類型"""
        if distance_km > 20:
            return RoadType.HIGHWAY
        elif distance_km > 5:
            return RoadType.PROVINCIAL
        else:
            return RoadType.URBAN
    
    def _estimate_average_speed(self, distance_km: float, road_type: RoadType) -> int:
        """根據距離和道路類型估算平均速度"""
        if road_type == RoadType.HIGHWAY:
            return 90  # 國道平均 90 km/h
        elif road_type == RoadType.HIGHWAY5:
            return 80  # 國5平均 80 km/h
        elif road_type == RoadType.PROVINCIAL:
            return 60  # 省道平均 60 km/h
        else:  # URBAN
            return 40  # 市區道路平均 40 km/h
    
    def get_carbon_emission_coefficient(self, speed: int, road_type: RoadType, vehicle_type: VehicleType) -> float:
        """根據速度、道路類型和交通工具類型獲取碳排放係數"""
        
        if vehicle_type == VehicleType.MOTORCYCLE:
            # 機車：找到最接近的速度數據
            data = self._find_closest_speed_data(speed, self.motorcycle_emission_data)
            return data.co2 if data else 150.0
        
        elif vehicle_type == VehicleType.CAR:
            # 小客車：找到最接近的速度數據
            data = self._find_closest_speed_data(speed, self.car_emission_data)
            if not data:
                return 200.0
            
            # 根據道路類型返回相應的碳排放係數
            if road_type in [RoadType.HIGHWAY, RoadType.HIGHWAY5]:
                return data.highway_co2
            else:  # PROVINCIAL, URBAN
                return data.provincial_co2
        
        elif vehicle_type == VehicleType.BUS:
            # 大客車：找到最接近的速度數據
            data = self._find_closest_speed_data(speed, self.bus_emission_data)
            if not data:
                return 400.0
            
            # 根據道路類型返回相應的碳排放係數
            if road_type == RoadType.HIGHWAY:
                return data.highway_co2
            elif road_type == RoadType.HIGHWAY5:
                return data.highway5_co2
            elif road_type == RoadType.PROVINCIAL:
                return data.provincial_co2
            else:  # URBAN
                return data.urban_co2
        
        # 預設返回小客車的排放係數
        return self.get_carbon_emission_coefficient(speed, road_type, VehicleType.CAR)
    
    def calculate_carbon_emission(
        self, 
        distance: float, 
        vehicle_type: str = "car",
        traffic_conditions: str = "normal",
        road_type: Optional[RoadType] = None,
        speed: Optional[int] = None
    ) -> float:
        """
        計算碳排放
        
        Args:
            distance: 距離（公尺）
            vehicle_type: 交通工具類型 (car, motorcycle, bus)
            traffic_conditions: 交通狀況 (normal, heavy, light)
            road_type: 道路類型（可選，會自動估算）
            speed: 速度（可選，會自動估算）
        
        Returns:
            碳排放量（克）
        """
        try:
            # 轉換距離單位
            distance_km = distance / 1000.0
            
            # 驗證交通工具類型
            try:
                vehicle_enum = VehicleType(vehicle_type)
            except ValueError:
                vehicle_enum = VehicleType.CAR
            
            # 估算道路類型
            if road_type is None:
                road_type = self._estimate_road_type(distance_km)
            
            # 估算速度
            if speed is None:
                speed = self._estimate_average_speed(distance_km, road_type)
            
            # 根據交通狀況調整速度
            if traffic_conditions == "heavy":
                speed = max(20, speed - 20)  # 塞車時速度降低
            elif traffic_conditions == "light":
                speed = min(100, speed + 10)  # 順暢時速度提升
            
            # 獲取碳排放係數
            co2_per_km = self.get_carbon_emission_coefficient(speed, road_type, vehicle_enum)
            
            # 計算總碳排放
            total_co2 = distance_km * co2_per_km
            
            return total_co2
            
        except Exception as e:
            # 如果計算失敗，返回預設值
            print(f"碳排放計算錯誤: {e}")
            distance_km = distance / 1000.0
            return distance_km * 200.0  # 預設 200g/km
    
    def calculate_multiple_vehicle_emissions(self, distance: float) -> Dict[str, float]:
        """計算多種交通工具的碳排放比較"""
        distance_km = distance / 1000.0
        road_type = self._estimate_road_type(distance_km)
        speed = self._estimate_average_speed(distance_km, road_type)
        
        return {
            "car": self.calculate_carbon_emission(distance, "car", road_type=road_type, speed=speed),
            "bus": self.calculate_carbon_emission(distance, "bus", road_type=road_type, speed=speed),
            "motorcycle": self.calculate_carbon_emission(distance, "motorcycle", road_type=road_type, speed=speed)
        }
