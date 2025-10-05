// 交通碳排放計算工具
// 基於交通部提供的動態能耗與碳排放係數數據

export interface BusEmissionData {
  speed: number; // km/hr
  // 國道客運/遊覽車國道(國5除外)
  highwayFuel: number; // l/km
  highwayCO2: number; // g/km
  // 國道客運/遊覽車國道5號
  highway5Fuel: number; // l/km
  highway5CO2: number; // g/km
  // 國道客運/遊覽車省道
  provincialFuel: number; // l/km
  provincialCO2: number; // g/km
  // 市區公車市區道路
  urbanFuel: number; // l/km
  urbanCO2: number; // g/km
}

export interface CarEmissionData {
  speed: number; // km/hr
  // 小客車國道
  highwayFuel: number; // l/km
  highwayCO2: number; // g/km
  // 小客車省道
  provincialFuel: number; // l/km
  provincialCO2: number; // g/km
}

export interface MotorcycleEmissionData {
  speed: number; // km/hr
  fuel: number; // l/km
  co2: number; // g/km
}

// 大客車碳排放係數數據 (基於大客車動態能耗與碳排放係數.csv)
const BUS_EMISSION_DATA: BusEmissionData[] = [
  { speed: 20, highwayFuel: 0.1907, highwayCO2: 497.0278, highway5Fuel: 0.2566, highway5CO2: 668.5917, provincialFuel: 0.1793, provincialCO2: 467.2016, urbanFuel: 0.5834, urbanCO2: 1520.2901 },
  { speed: 30, highwayFuel: 0.1734, highwayCO2: 451.9722, highway5Fuel: 0.2284, highway5CO2: 595.2837, provincialFuel: 0.1641, provincialCO2: 427.7437, urbanFuel: 0.4512, urbanCO2: 1175.6231 },
  { speed: 40, highwayFuel: 0.1601, highwayCO2: 417.2606, highway5Fuel: 0.2081, highway5CO2: 542.5143, provincialFuel: 0.1521, provincialCO2: 396.4737, urbanFuel: 0.3684, urbanCO2: 960.1026 },
  { speed: 50, highwayFuel: 0.1493, highwayCO2: 389.1331, highway5Fuel: 0.1921, highway5CO2: 500.5837, provincialFuel: 0.1421, provincialCO2: 370.2737, urbanFuel: 0.3081, urbanCO2: 803.1026 },
  { speed: 60, highwayFuel: 0.1410, highwayCO2: 367.4631, highway5Fuel: 0.1791, highway5CO2: 466.8837, provincialFuel: 0.1331, provincialCO2: 346.8837, urbanFuel: 0.2581, urbanCO2: 672.5026 },
  { speed: 70, highwayFuel: 0.1342, highwayCO2: 349.7131, highway5Fuel: 0.1681, highway5CO2: 438.0837, provincialFuel: 0.1251, provincialCO2: 326.0837, urbanFuel: 0.2181, urbanCO2: 568.5026 },
  { speed: 80, highwayFuel: 0.1289, highwayCO2: 335.8831, highway5Fuel: 0.1581, highway5CO2: 412.2837, provincialFuel: 0.1181, provincialCO2: 307.8837, urbanFuel: 0.1881, urbanCO2: 490.5026 },
  { speed: 90, highwayFuel: 0.1249, highwayCO2: 325.4831, highway5Fuel: 0.1491, highway5CO2: 388.6837, provincialFuel: 0.1121, provincialCO2: 292.1837, urbanFuel: 0.1681, urbanCO2: 438.5026 },
  { speed: 100, highwayFuel: 0.1222, highwayCO2: 318.4831, highway5Fuel: 0.1411, highway5CO2: 367.8837, provincialFuel: 0.1071, provincialCO2: 279.1837, urbanFuel: 0.1581, urbanCO2: 412.5026 }
];

// 小客車碳排放係數數據 (基於小客車動態能耗與碳排放係數.csv)
const CAR_EMISSION_DATA: CarEmissionData[] = [
  { speed: 20, highwayFuel: 0.1111, highwayCO2: 251.5306, provincialFuel: 0.1823, provincialCO2: 412.4389 },
  { speed: 30, highwayFuel: 0.1015, highwayCO2: 229.6737, provincialFuel: 0.1683, provincialCO2: 380.8127 },
  { speed: 40, highwayFuel: 0.0951, highwayCO2: 215.2437, provincialFuel: 0.1581, provincialCO2: 357.7737 },
  { speed: 50, highwayFuel: 0.0905, highwayCO2: 204.7737, provincialFuel: 0.1501, provincialCO2: 339.7737 },
  { speed: 60, highwayFuel: 0.0871, highwayCO2: 197.1137, provincialFuel: 0.1431, provincialCO2: 323.7737 },
  { speed: 70, highwayFuel: 0.0845, highwayCO2: 191.2337, provincialFuel: 0.1371, provincialCO2: 310.2737 },
  { speed: 80, highwayFuel: 0.0825, highwayCO2: 186.7337, provincialFuel: 0.1321, provincialCO2: 298.9737 },
  { speed: 90, highwayFuel: 0.0811, highwayCO2: 183.4937, provincialFuel: 0.1281, provincialCO2: 289.7737 },
  { speed: 100, highwayFuel: 0.0801, highwayCO2: 181.2937, provincialFuel: 0.1251, provincialCO2: 283.0737 }
];

// 機車碳排放係數數據 (基於機車動態能耗與碳排放係數.csv)
const MOTORCYCLE_EMISSION_DATA: MotorcycleEmissionData[] = [
  { speed: 20, fuel: 0.0905, co2: 204.7260 },
  { speed: 30, fuel: 0.0821, co2: 185.7737 },
  { speed: 40, fuel: 0.0765, co2: 173.0737 },
  { speed: 50, fuel: 0.0725, co2: 164.0737 },
  { speed: 60, fuel: 0.0695, co2: 157.2737 },
  { speed: 70, fuel: 0.0673, co2: 152.2737 },
  { speed: 80, fuel: 0.0657, co2: 148.6737 },
  { speed: 90, fuel: 0.0645, co2: 145.9737 },
  { speed: 100, fuel: 0.0637, co2: 144.1737 }
];

// 交通工具類型
export enum VehicleType {
  BUS = 'bus',           // 大客車
  CAR = 'car',           // 小客車
  MOTORCYCLE = 'motorcycle'  // 機車
}

// 道路類型
export enum RoadType {
  HIGHWAY = 'highway',           // 國道(國5除外)
  HIGHWAY5 = 'highway5',         // 國道5號
  PROVINCIAL = 'provincial',     // 省道
  URBAN = 'urban'               // 市區道路
}

// 根據速度和道路類型獲取碳排放係數
function getCarbonEmissionCoefficient(speed: number, roadType: RoadType, vehicleType: VehicleType): number {
  if (vehicleType === VehicleType.MOTORCYCLE) {
    // 機車：找到最接近的速度數據
    let closestData = MOTORCYCLE_EMISSION_DATA[0];
    let minDiff = Math.abs(speed - MOTORCYCLE_EMISSION_DATA[0].speed);
    
    for (const data of MOTORCYCLE_EMISSION_DATA) {
      const diff = Math.abs(speed - data.speed);
      if (diff < minDiff) {
        minDiff = diff;
        closestData = data;
      }
    }
    
    return closestData.co2;
  }
  
  if (vehicleType === VehicleType.CAR) {
    // 小客車：找到最接近的速度數據
    let closestData = CAR_EMISSION_DATA[0];
    let minDiff = Math.abs(speed - CAR_EMISSION_DATA[0].speed);
    
    for (const data of CAR_EMISSION_DATA) {
      const diff = Math.abs(speed - data.speed);
      if (diff < minDiff) {
        minDiff = diff;
        closestData = data;
      }
    }
    
    // 根據道路類型返回相應的碳排放係數
    switch (roadType) {
      case RoadType.HIGHWAY:
      case RoadType.HIGHWAY5:
        return closestData.highwayCO2;
      case RoadType.PROVINCIAL:
      case RoadType.URBAN:
        return closestData.provincialCO2;
      default:
        return closestData.highwayCO2;
    }
  }
  
  if (vehicleType === VehicleType.BUS) {
    // 大客車：找到最接近的速度數據
    let closestData = BUS_EMISSION_DATA[0];
    let minDiff = Math.abs(speed - BUS_EMISSION_DATA[0].speed);
    
    for (const data of BUS_EMISSION_DATA) {
      const diff = Math.abs(speed - data.speed);
      if (diff < minDiff) {
        minDiff = diff;
        closestData = data;
      }
    }
    
    // 根據道路類型返回相應的碳排放係數
    switch (roadType) {
      case RoadType.HIGHWAY:
        return closestData.highwayCO2;
      case RoadType.HIGHWAY5:
        return closestData.highway5CO2;
      case RoadType.PROVINCIAL:
        return closestData.provincialCO2;
      case RoadType.URBAN:
        return closestData.urbanCO2;
      default:
        return closestData.highwayCO2;
    }
  }
  
  // 預設返回小客車的排放係數
  return getCarbonEmissionCoefficient(speed, roadType, VehicleType.CAR);
}

// 計算碳排放
export function calculateCarbonEmission(
  distanceKm: number,
  speedKmh: number = 50,
  roadType: RoadType = RoadType.URBAN,
  vehicleType: VehicleType = VehicleType.CAR
): {
  co2Grams: number;
  co2Kg: number;
  formatted: string;
} {
  const co2PerKm = getCarbonEmissionCoefficient(speedKmh, roadType, vehicleType);
  const co2Grams = distanceKm * co2PerKm;
  const co2Kg = co2Grams / 1000;
  
  let formatted: string;
  if (co2Kg < 1) {
    formatted = `${Math.round(co2Grams)}g`;
  } else {
    formatted = `${co2Kg.toFixed(2)}kg`;
  }
  
  return {
    co2Grams,
    co2Kg,
    formatted
  };
}

// 根據距離估算道路類型
export function estimateRoadType(distanceKm: number): RoadType {
  if (distanceKm > 20) {
    return Math.random() > 0.5 ? RoadType.HIGHWAY : RoadType.HIGHWAY5;
  } else if (distanceKm > 5) {
    return RoadType.PROVINCIAL;
  } else {
    return RoadType.URBAN;
  }
}

// 根據距離估算平均速度
export function estimateAverageSpeed(distanceKm: number, roadType: RoadType): number {
  switch (roadType) {
    case RoadType.HIGHWAY:
    case RoadType.HIGHWAY5:
      return 80 + Math.random() * 20; // 80-100 km/h
    case RoadType.PROVINCIAL:
      return 50 + Math.random() * 20; // 50-70 km/h
    case RoadType.URBAN:
      return 30 + Math.random() * 20; // 30-50 km/h
    default:
      return 50;
  }
}

// 計算多種交通工具的碳排放比較
export function calculateMultipleVehicleEmissions(distanceKm: number): {
  car: { co2Grams: number; co2Kg: number; formatted: string };
  bus: { co2Grams: number; co2Kg: number; formatted: string };
  motorcycle: { co2Grams: number; co2Kg: number; formatted: string };
} {
  const roadType = estimateRoadType(distanceKm);
  const speed = estimateAverageSpeed(distanceKm, roadType);
  
  return {
    car: calculateCarbonEmission(distanceKm, speed, roadType, VehicleType.CAR),
    bus: calculateCarbonEmission(distanceKm, speed, roadType, VehicleType.BUS),
    motorcycle: calculateCarbonEmission(distanceKm, speed, roadType, VehicleType.MOTORCYCLE)
  };
}
