#!/usr/bin/env python3
"""
公車資料匯入腳本
將 CSV 格式的公車資料匯入到 PostgreSQL 資料庫中
"""

import os
import sys
import pandas as pd
from datetime import datetime, time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import WKTElement
import uuid

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.infrastructure.persistence.database import get_database_url
from src.itinerary_planner.infrastructure.persistence.orm_models import (
    BusRoute, BusStation, BusTrip, BusStopTime, Base
)

def create_database_engine():
    """建立資料庫連接引擎"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    return engine

def create_tables(engine):
    """建立公車相關的資料表"""
    print("建立公車相關資料表...")
    Base.metadata.create_all(engine)
    print("資料表建立完成")

def parse_operating_days(days_str):
    """解析營運日字串"""
    if pd.isna(days_str) or days_str == '':
        return []
    
    # 移除引號並分割
    days_str = str(days_str).strip('"')
    days = [day.strip() for day in days_str.split(',')]
    return days

def parse_time(time_str):
    """解析時間字串"""
    if pd.isna(time_str) or time_str == '':
        return None
    
    try:
        # 處理 HH:MM 格式
        if ':' in str(time_str):
            hour, minute = str(time_str).split(':')
            return time(int(hour), int(minute))
    except (ValueError, AttributeError):
        pass
    
    return None

def import_routes(engine, csv_file):
    """匯入路線資料"""
    print(f"匯入路線資料: {csv_file}")
    
    df = pd.read_csv(csv_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        for _, row in df.iterrows():
            route = BusRoute(
                route_id=str(row['路線ID']),
                route_name=row['路線編號'],
                departure_stop=row['起站'],
                destination_stop=row['迄站'],
                route_type=row['路線類型'] if pd.notna(row['路線類型']) else None,
                status=row['營運狀態'] if pd.notna(row['營運狀態']) else None
            )
            session.add(route)
        
        session.commit()
        print(f"成功匯入 {len(df)} 條路線")
        
    except Exception as e:
        session.rollback()
        print(f"匯入路線資料時發生錯誤: {e}")
        raise
    finally:
        session.close()

def import_stations(engine, csv_file):
    """匯入站點資料"""
    print(f"匯入站點資料: {csv_file}")
    
    df = pd.read_csv(csv_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 先取得路線對應表
        route_mapping = {}
        routes = session.query(BusRoute).all()
        for route in routes:
            route_mapping[route.route_name] = route.id
        
        for _, row in df.iterrows():
            route_name = row['路線編號']
            if route_name not in route_mapping:
                print(f"警告: 找不到路線 {route_name}")
                continue
            
            # 解析方向 (去程=0, 回程=1)
            direction = 0 if row['方向'] == '去程' else 1
            
            # 建立地理座標
            lat = float(row['緯度'])
            lon = float(row['經度'])
            geom = WKTElement(f'POINT({lon} {lat})', srid=4326)
            
            station = BusStation(
                route_id=route_mapping[route_name],
                station_id=str(row['站牌ID']),
                station_name=row['站名'],
                sequence=int(row['站序']),
                direction=direction,
                geom=geom
            )
            session.add(station)
        
        session.commit()
        print(f"成功匯入 {len(df)} 個站點")
        
    except Exception as e:
        session.rollback()
        print(f"匯入站點資料時發生錯誤: {e}")
        raise
    finally:
        session.close()

def import_trips(engine, csv_file):
    """匯入班次資料"""
    print(f"匯入班次資料: {csv_file}")
    
    df = pd.read_csv(csv_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 先取得路線對應表
        route_mapping = {}
        routes = session.query(BusRoute).all()
        for route in routes:
            route_mapping[route.route_name] = route.id
        
        for _, row in df.iterrows():
            route_name = row['路線編號']
            if route_name not in route_mapping:
                print(f"警告: 找不到路線 {route_name}")
                continue
            
            # 解析方向 (去程=0, 回程=1)
            direction = 0 if row['方向'] == '去程' else 1
            
            # 解析發車時間
            departure_time = parse_time(row['發車時間'])
            if not departure_time:
                print(f"警告: 無法解析發車時間 {row['發車時間']}")
                continue
            
            # 解析營運日
            operating_days = parse_operating_days(row['營運日'])
            
            # 解析低地板公車
            is_low_floor = row['低地板公車'] == '是' if pd.notna(row['低地板公車']) else False
            
            trip = BusTrip(
                route_id=route_mapping[route_name],
                trip_id=str(row['班次ID']),
                direction=direction,
                departure_time=departure_time,
                departure_station=row['發車站名'],
                operating_days=operating_days,
                is_low_floor=is_low_floor
            )
            session.add(trip)
        
        session.commit()
        print(f"成功匯入 {len(df)} 個班次")
        
    except Exception as e:
        session.rollback()
        print(f"匯入班次資料時發生錯誤: {e}")
        raise
    finally:
        session.close()

def import_stop_times(engine, csv_file):
    """匯入時刻表資料"""
    print(f"匯入時刻表資料: {csv_file}")
    
    df = pd.read_csv(csv_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 先取得班次和站點對應表
        trip_mapping = {}
        trips = session.query(BusTrip).all()
        for trip in trips:
            # 使用路線名稱 + 班次ID + 方向作為鍵
            route = session.query(BusRoute).filter(BusRoute.id == trip.route_id).first()
            key = f"{route.route_name}_{trip.trip_id}_{trip.direction}"
            trip_mapping[key] = trip.id
        
        station_mapping = {}
        stations = session.query(BusStation).all()
        for station in stations:
            # 使用路線名稱 + 站牌ID + 方向作為鍵
            route = session.query(BusRoute).filter(BusRoute.id == station.route_id).first()
            key = f"{route.route_name}_{station.station_id}_{station.direction}"
            station_mapping[key] = station.id
        
        imported_count = 0
        for _, row in df.iterrows():
            route_name = row['路線編號']
            trip_id = str(row['班次ID'])
            station_id = str(row['站牌ID'])
            direction = 0 if row['方向'] == '去程' else 1
            
            # 建立查詢鍵
            trip_key = f"{route_name}_{trip_id}_{direction}"
            station_key = f"{route_name}_{station_id}_{direction}"
            
            if trip_key not in trip_mapping:
                continue  # 跳過沒有對應班次的記錄
            if station_key not in station_mapping:
                continue  # 跳過沒有對應站點的記錄
            
            # 解析時間
            arrival_time = parse_time(row['抵達時間'])
            departure_time = parse_time(row['離站時間'])
            
            if not arrival_time or not departure_time:
                continue  # 跳過時間格式錯誤的記錄
            
            stop_time = BusStopTime(
                trip_id=trip_mapping[trip_key],
                station_id=station_mapping[station_key],
                sequence=int(row['站序']),
                arrival_time=arrival_time,
                departure_time=departure_time
            )
            session.add(stop_time)
            imported_count += 1
        
        session.commit()
        print(f"成功匯入 {imported_count} 筆時刻記錄")
        
    except Exception as e:
        session.rollback()
        print(f"匯入時刻表資料時發生錯誤: {e}")
        raise
    finally:
        session.close()

def verify_import(engine):
    """驗證匯入結果"""
    print("\n=== 匯入結果驗證 ===")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 統計各表的記錄數
        routes_count = session.query(BusRoute).count()
        stations_count = session.query(BusStation).count()
        trips_count = session.query(BusTrip).count()
        stop_times_count = session.query(BusStopTime).count()
        
        print(f"路線數量: {routes_count}")
        print(f"站點數量: {stations_count}")
        print(f"班次數量: {trips_count}")
        print(f"時刻記錄數量: {stop_times_count}")
        
        # 顯示一些範例資料
        print("\n=== 範例路線 ===")
        sample_routes = session.query(BusRoute).limit(5).all()
        for route in sample_routes:
            print(f"- {route.route_name}: {route.departure_stop} → {route.destination_stop}")
        
        print("\n=== 範例班次 ===")
        sample_trips = session.query(BusTrip).join(BusRoute).limit(5).all()
        for trip in sample_trips:
            route = session.query(BusRoute).filter(BusRoute.id == trip.route_id).first()
            direction_name = "去程" if trip.direction == 0 else "回程"
            print(f"- {route.route_name} {direction_name}: {trip.departure_time} 從 {trip.departure_station}")
        
    finally:
        session.close()

def main():
    """主程式"""
    print("=== 公車資料匯入程式 ===\n")
    
    # 資料檔案路徑
    data_dir = os.path.join(project_root, "data", "osrm", "data")
    routes_file = os.path.join(data_dir, "routes.csv")
    stations_file = os.path.join(data_dir, "stations.csv")
    trips_file = os.path.join(data_dir, "trips.csv")
    
    # 優先使用增強版的時刻表資料
    enhanced_stop_times_file = os.path.join(data_dir, "stop_times_enhanced.csv")
    stop_times_file = os.path.join(data_dir, "stop_times.csv")
    
    if os.path.exists(enhanced_stop_times_file):
        stop_times_file = enhanced_stop_times_file
        print(f"使用增強版時刻表資料: {enhanced_stop_times_file}")
    else:
        print(f"使用標準時刻表資料: {stop_times_file}")
    
    # 檢查檔案是否存在
    required_files = [routes_file, stations_file, trips_file, stop_times_file]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"錯誤: 找不到檔案 {file_path}")
            sys.exit(1)
    
    # 建立資料庫連接
    try:
        engine = create_database_engine()
        print("資料庫連接成功")
    except Exception as e:
        print(f"資料庫連接失敗: {e}")
        sys.exit(1)
    
    try:
        # 建立資料表
        create_tables(engine)
        
        # 依序匯入資料
        import_routes(engine, routes_file)
        import_stations(engine, stations_file)
        import_trips(engine, trips_file)
        import_stop_times(engine, stop_times_file)
        
        # 驗證匯入結果
        verify_import(engine)
        
        print("\n=== 匯入完成 ===")
        print("所有公車資料已成功匯入資料庫！")
        
    except Exception as e:
        print(f"匯入過程中發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

