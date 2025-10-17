-- 新增公車運輸相關資料表
-- 遷移版本: 008
-- 描述: 新增公車路線、站點、班次和時刻表相關的資料表

-- 確保 PostGIS 擴展已啟用
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- 公車路線表
-- ============================================================================
CREATE TABLE IF NOT EXISTS bus_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id VARCHAR(50) UNIQUE NOT NULL,
    route_name VARCHAR(50) NOT NULL,
    departure_stop VARCHAR(255) NOT NULL,
    destination_stop VARCHAR(255) NOT NULL,
    route_type VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_bus_routes_route_id ON bus_routes(route_id);
CREATE INDEX IF NOT EXISTS idx_bus_routes_route_name ON bus_routes(route_name);

-- 建立唯一約束
ALTER TABLE bus_routes ADD CONSTRAINT IF NOT EXISTS uq_bus_route_id UNIQUE (route_id);
ALTER TABLE bus_routes ADD CONSTRAINT IF NOT EXISTS uq_bus_route_name UNIQUE (route_name);

-- ============================================================================
-- 公車站點表
-- ============================================================================
CREATE TABLE IF NOT EXISTS bus_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES bus_routes(id) ON DELETE CASCADE,
    station_id VARCHAR(50) NOT NULL,
    station_name VARCHAR(255) NOT NULL,
    sequence INTEGER NOT NULL,
    direction INTEGER NOT NULL, -- 0: 去程, 1: 回程
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_bus_stations_route_id ON bus_stations(route_id);
CREATE INDEX IF NOT EXISTS idx_bus_stations_station_id ON bus_stations(station_id);
CREATE INDEX IF NOT EXISTS idx_bus_stations_geom ON bus_stations USING GIST(geom);

-- 建立唯一約束
ALTER TABLE bus_stations ADD CONSTRAINT IF NOT EXISTS uq_bus_station_sequence 
    UNIQUE (route_id, station_id, direction, sequence);

-- ============================================================================
-- 公車班次表
-- ============================================================================
CREATE TABLE IF NOT EXISTS bus_trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES bus_routes(id) ON DELETE CASCADE,
    trip_id VARCHAR(50) NOT NULL,
    direction INTEGER NOT NULL, -- 0: 去程, 1: 回程
    departure_time TIME NOT NULL,
    departure_station VARCHAR(255) NOT NULL,
    operating_days TEXT[], -- 營運日陣列
    is_low_floor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_bus_trips_route_id ON bus_trips(route_id);
CREATE INDEX IF NOT EXISTS idx_bus_trips_trip_id ON bus_trips(trip_id);

-- 建立唯一約束
ALTER TABLE bus_trips ADD CONSTRAINT IF NOT EXISTS uq_bus_trip 
    UNIQUE (route_id, trip_id, direction);

-- ============================================================================
-- 公車時刻表
-- ============================================================================
CREATE TABLE IF NOT EXISTS bus_stop_times (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES bus_trips(id) ON DELETE CASCADE,
    station_id UUID NOT NULL REFERENCES bus_stations(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    arrival_time TIME NOT NULL,
    departure_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_bus_stop_times_trip_id ON bus_stop_times(trip_id);
CREATE INDEX IF NOT EXISTS idx_bus_stop_times_station_id ON bus_stop_times(station_id);

-- 建立唯一約束
ALTER TABLE bus_stop_times ADD CONSTRAINT IF NOT EXISTS uq_bus_stop_time_sequence 
    UNIQUE (trip_id, sequence);

-- ============================================================================
-- 運輸連接點表
-- ============================================================================
CREATE TABLE IF NOT EXISTS transport_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    station_id UUID REFERENCES bus_stations(id) ON DELETE CASCADE,
    connection_type VARCHAR(50) NOT NULL, -- 'bus_station', 'transfer_point'
    distance_meters INTEGER,
    walking_time_minutes INTEGER,
    is_accessible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_transport_connections_place_id ON transport_connections(place_id);
CREATE INDEX IF NOT EXISTS idx_transport_connections_station_id ON transport_connections(station_id);

-- 建立約束：place_id 和 station_id 必須有一個不為 NULL
ALTER TABLE transport_connections ADD CONSTRAINT IF NOT EXISTS check_connection_reference 
    CHECK (
        (place_id IS NOT NULL AND station_id IS NULL) OR 
        (place_id IS NULL AND station_id IS NOT NULL)
    );

-- ============================================================================
-- 更新時間戳記的觸發器函數
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 為 bus_routes 表建立更新觸發器
DROP TRIGGER IF EXISTS update_bus_routes_updated_at ON bus_routes;
CREATE TRIGGER update_bus_routes_updated_at
    BEFORE UPDATE ON bus_routes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 新增註解
-- ============================================================================
COMMENT ON TABLE bus_routes IS '公車路線基本資訊';
COMMENT ON TABLE bus_stations IS '公車站點資訊，包含座標和路線順序';
COMMENT ON TABLE bus_trips IS '公車班次資訊，包含發車時間和營運日';
COMMENT ON TABLE bus_stop_times IS '公車時刻表，記錄每個班次在各站點的抵達和離站時間';
COMMENT ON TABLE transport_connections IS '運輸連接點，用於連接景點和公車站點';

COMMENT ON COLUMN bus_stations.direction IS '方向：0=去程，1=回程';
COMMENT ON COLUMN bus_trips.direction IS '方向：0=去程，1=回程';
COMMENT ON COLUMN bus_trips.operating_days IS '營運日陣列，如：["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]';
COMMENT ON COLUMN transport_connections.connection_type IS '連接類型：bus_station=公車站點，transfer_point=轉乘點';

-- ============================================================================
-- 資料驗證
-- ============================================================================
-- 檢查是否成功建立所有資料表
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('bus_routes', 'bus_stations', 'bus_trips', 'bus_stop_times', 'transport_connections');
    
    IF table_count = 5 THEN
        RAISE NOTICE '所有公車運輸相關資料表已成功建立';
    ELSE
        RAISE EXCEPTION '資料表建立不完整，期望 5 個資料表，實際建立 % 個', table_count;
    END IF;
END $$;

