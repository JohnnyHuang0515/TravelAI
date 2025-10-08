"""
碳排放計算服務單元測試
"""
import pytest
from unittest.mock import Mock

from src.itinerary_planner.application.services.carbon_calculation_service import (
    CarbonCalculationService,
    VehicleType,
    RoadType,
    BusEmissionData,
    CarEmissionData,
    MotorcycleEmissionData
)


class TestCarbonCalculationService:
    """碳排放計算服務測試類別"""
    
    @pytest.fixture
    def carbon_service(self):
        """建立碳排放計算服務實例"""
        return CarbonCalculationService()
    
    @pytest.fixture
    def sample_bus_data(self):
        """測試用的大客車排放數據"""
        return BusEmissionData(
            speed=60,
            highway_fuel=0.5,
            highway_co2=1.2,
            highway5_fuel=0.6,
            highway5_co2=1.4,
            provincial_fuel=0.7,
            provincial_co2=1.6,
            urban_fuel=0.8,
            urban_co2=1.8
        )
    
    @pytest.fixture
    def sample_car_data(self):
        """測試用的小客車排放數據"""
        return CarEmissionData(
            speed=60,
            highway_fuel=0.3,
            highway_co2=0.7,
            provincial_fuel=0.4,
            provincial_co2=0.9
        )
    
    @pytest.fixture
    def sample_motorcycle_data(self):
        """測試用的機車排放數據"""
        return MotorcycleEmissionData(
            speed=40,
            fuel=0.2,
            co2=0.5
        )
    
    def test_get_emission_data_bus(self, carbon_service, sample_bus_data):
        """測試取得大客車排放數據"""
        # 執行測試
        result = carbon_service._find_closest_speed_data(60, carbon_service.bus_emission_data)
        
        # 驗證結果
        assert result is not None
        assert isinstance(result, BusEmissionData)
        assert result.speed == 60
    
    def test_get_emission_data_car(self, carbon_service, sample_car_data):
        """測試取得小客車排放數據"""
        # 執行測試
        result = carbon_service._find_closest_speed_data(60, carbon_service.car_emission_data)
        
        # 驗證結果
        assert result is not None
        assert isinstance(result, CarEmissionData)
        assert result.speed == 60
    
    def test_get_emission_data_motorcycle(self, carbon_service, sample_motorcycle_data):
        """測試取得機車排放數據"""
        # 執行測試
        result = carbon_service._find_closest_speed_data(40, carbon_service.motorcycle_emission_data)
        
        # 驗證結果
        assert result is not None
        assert isinstance(result, MotorcycleEmissionData)
        assert result.speed == 40
    
    def test_get_emission_data_invalid_vehicle(self, carbon_service):
        """測試無效的交通工具類型"""
        # 執行測試
        result = carbon_service._find_closest_speed_data(60, [])
        
        # 驗證結果
        assert result is None
    
    def test_get_emission_data_invalid_speed(self, carbon_service):
        """測試無效的速度"""
        # 執行測試
        result = carbon_service._find_closest_speed_data(999, carbon_service.car_emission_data)
        
        # 驗證結果
        assert result is not None  # 應該返回最接近的數據
    
    def test_calculate_emission_bus_highway(self, carbon_service):
        """測試計算大客車在國道的碳排放"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=100000,  # 100公里（公尺）
            vehicle_type="bus",
            traffic_conditions="normal",
            road_type=RoadType.HIGHWAY,
            speed=60
        )
        
        # 驗證結果
        assert result is not None
        assert result > 0  # 碳排放量應該大於0
    
    def test_calculate_emission_car_provincial(self, carbon_service):
        """測試計算小客車在省道的碳排放"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=50000,  # 50公里（公尺）
            vehicle_type="car",
            traffic_conditions="normal",
            road_type=RoadType.PROVINCIAL,
            speed=50
        )
        
        # 驗證結果
        assert result is not None
        assert result > 0  # 碳排放量應該大於0
    
    def test_calculate_emission_motorcycle_urban(self, carbon_service):
        """測試計算機車在市區道路的碳排放"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=20000,  # 20公里（公尺）
            vehicle_type="motorcycle",
            traffic_conditions="normal",
            road_type=RoadType.URBAN,
            speed=40
        )
        
        # 驗證結果
        assert result is not None
        assert result > 0  # 碳排放量應該大於0
    
    def test_calculate_emission_invalid_vehicle(self, carbon_service):
        """測試計算無效交通工具的碳排放"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=100000,
            vehicle_type="invalid",
            traffic_conditions="normal"
        )
        
        # 驗證結果
        assert result is not None  # 應該使用預設值
    
    def test_calculate_emission_zero_distance(self, carbon_service):
        """測試計算零距離的碳排放"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=0,
            vehicle_type="car",
            traffic_conditions="normal"
        )
        
        # 驗證結果
        assert result is not None
        assert result == 0  # 零距離應該返回0
    
    def test_calculate_emission_negative_distance(self, carbon_service):
        """測試計算負距離的碳排放"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=-10000,
            vehicle_type="car",
            traffic_conditions="normal"
        )
        
        # 驗證結果
        assert result is not None  # 應該使用預設值
    
    def test_calculate_emission_different_speeds(self, carbon_service):
        """測試不同速度的碳排放計算"""
        # 測試低速
        result_low = carbon_service.calculate_carbon_emission(
            distance=100000,
            vehicle_type="car",
            traffic_conditions="normal",
            speed=30
        )
        
        # 測試高速
        result_high = carbon_service.calculate_carbon_emission(
            distance=100000,
            vehicle_type="car",
            traffic_conditions="normal",
            speed=90
        )
        
        # 驗證結果
        assert result_low is not None
        assert result_high is not None
        # 不同速度應該有不同的排放量
        assert result_low != result_high
    
    def test_calculate_emission_large_distance(self, carbon_service):
        """測試大距離的碳排放計算"""
        # 執行測試
        result = carbon_service.calculate_carbon_emission(
            distance=500000,  # 500公里（公尺）
            vehicle_type="bus",
            traffic_conditions="normal"
        )
        
        # 驗證結果
        assert result is not None
        assert result > 0  # 碳排放量應該大於0
