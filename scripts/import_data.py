import json
import re
import uuid
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import sessionmaker
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

# 修正 sys.path 以便能從專案根目錄導入模組
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.itinerary_planner.infrastructure.persistence.database import engine, Base
from src.itinerary_planner.infrastructure.persistence.orm_models import Place, Hour

# --- CONFIGURATION ---
# 讓腳本能找到 JSON 資料源
DATA_DIR = project_root / "docs"
RESTAURANT_FILE = DATA_DIR / "tdx_restaurant_yilan_raw.json"
SCENIC_SPOT_FILE = DATA_DIR / "tdx_scenic_yilan_raw.json"
HOTEL_FILE = DATA_DIR / "宜蘭縣旅館名冊.json"
HOMESTAY_FILE = DATA_DIR / "宜蘭縣民宿名冊.json"
ECO_RESTAURANT_FILE = DATA_DIR / "環保餐廳環境即時通地圖資料.json"
ECO_HOTEL_FILE = DATA_DIR / "環保標章旅館環境即時通地圖資料.json"
EDUCATION_FACILITY_FILE = DATA_DIR / "環境教育設施場所認證資料.json"

# --- DATA TRANSFORMATION LOGIC ---

def time_str_to_minutes(time_str: str) -> int:
    """將 'HH:MM' 格式的時間字串轉換為從午夜起算的分鐘數。"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except ValueError:
        return 0 # 處理格式不符的情況

def parse_open_time(open_time_str: str) -> List[Dict[str, Any]]:
    """
    解析複雜的營業時間字串。
    範例: "週一至週五 09:00-17:00; 週六 10:00-15:00"
    返回: [{'weekday': 1, 'open_min': 540, 'close_min': 1020}, ...]
    """
    if not open_time_str or "公休" in open_time_str or "休息" in open_time_str:
        return []

    week_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 0}
    parsed_hours = []

    # 移除多餘的文字
    clean_str = open_time_str.replace("、", " ").replace(";", " ").replace("，", " ")
    
    # 尋找所有時間範圍，例如 11:00-21:00
    time_ranges = re.findall(r'(\d{2}:\d{2})-(\d{2}:\d{2})', clean_str)
    if not time_ranges:
        return []

    # 尋找星期幾的描述
    day_descs = re.findall(r'週([一二三四五六日])至週([一二三四五六日])|週([一二三四五六日])', clean_str)
    
    active_days = set()
    for range_start, range_end, single_day in day_descs:
        if range_start and range_end: # 處理 "週一至週五"
            start_day = week_map[range_start]
            end_day = week_map[range_end]
            for i in range(start_day, end_day + 1):
                active_days.add(i)
        elif single_day: # 處理 "週二"
            active_days.add(week_map[single_day])

    # 如果沒有找到明確的星期描述，但有時間，則假設每天都營業
    if not active_days and time_ranges:
        active_days = set(range(7))

    for day in active_days:
        for start_str, end_str in time_ranges:
            open_min = time_str_to_minutes(start_str)
            close_min = time_str_to_minutes(end_str)
            if open_min < close_min: # 確保是有效的時間範圍
                parsed_hours.append({
                    "weekday": day,
                    "open_min": open_min,
                    "close_min": close_min
                })
    return parsed_hours


def process_tdx_data(data: List[Dict], type: str) -> List[Dict]:
    """處理 TDX 格式的資料（餐廳和景點）。"""
    processed = []
    for item in data:
        place_id = uuid.uuid4()
        
        # 處理位置
        lon = item.get("Position", {}).get("PositionLon")
        lat = item.get("Position", {}).get("PositionLat")
        if not lon or not lat:
            continue # 沒有座標的資料直接跳過
        
        point = Point(lon, lat)

        # 處理類別
        categories = []
        if item.get("Class"):
            categories.append(item["Class"])
        if item.get("Class1"):
            categories.append(item["Class1"])
        if item.get("Class2"):
            categories.append(item["Class2"])
        
        # 處理營業時間
        hours_data = parse_open_time(item.get("OpenTime", ""))

        place_data = {
            "id": place_id,
            "name": item.get("RestaurantName") or item.get("ScenicSpotName", "N/A"),
            "geom": from_shape(point, srid=4326),
            "categories": list(filter(None, categories)),
            "stay_minutes": 90 if type == "restaurant" else 120,
            "hours": [{"place_id": place_id, **h} for h in hours_data]
        }
        processed.append(place_data)
    return processed

def process_hotel_data(data: List[Dict], type: str) -> List[Dict]:
    """處理旅館/民宿資料"""
    processed = []
    for item in data:
        place_id = uuid.uuid4()
        
        # 檢查是否有座標資訊
        lat = item.get("latitude") or item.get("緯度")
        lon = item.get("longitude") or item.get("經度")
        
        if lat and lon:
            try:
                lat_float = float(lat)
                lon_float = float(lon)
                
                # 檢查是否在宜蘭地區 (大致範圍)
                if 24.4 <= lat_float <= 25.0 and 121.4 <= lon_float <= 122.0:
                    point = Point(lon_float, lat_float)
                    place_data = {
                        "id": place_id,
                        "name": item.get("name") or item.get("中文名稱", "N/A"),
                        "geom": from_shape(point, srid=4326),
                        "categories": [type],
                        "stay_minutes": 480,  # 住宿8小時
                        "hours": [],
                        "address": item.get("address") or item.get("營業地址", ""),
                        "phone": item.get("phone") or item.get("電話", ""),
                        "rating": 3.5,  # 預設評分
                        "price_range": 3  # 預設價格區間
                    }
                    processed.append(place_data)
            except (ValueError, TypeError):
                # 座標格式錯誤，跳過
                continue
        else:
            # 沒有座標，跳過
            continue
    
    return processed

def process_eco_restaurant_data(data: List[Dict]) -> List[Dict]:
    """處理環保餐廳資料（只保留宜蘭地區）。"""
    processed = []
    for item in data:
        # 只處理宜蘭地區的資料
        city = item.get("city", "")
        if "宜蘭" not in city:
            continue
            
        place_id = uuid.uuid4()
        
        # 處理位置
        try:
            lon = float(item.get("longitude", 0))
            lat = float(item.get("latitude", 0))
            if lon == 0 or lat == 0:
                continue
        except (ValueError, TypeError):
            continue
        
        point = Point(lon, lat)

        place_data = {
            "id": place_id,
            "name": item.get("name", "N/A"),
            "geom": from_shape(point, srid=4326),
            "categories": ["環保餐廳"],
            "stay_minutes": 90,
            "hours": []
        }
        processed.append(place_data)
    return processed

def process_eco_hotel_data(data: List[Dict]) -> List[Dict]:
    """處理環保標章旅館資料（只保留宜蘭地區）。"""
    processed = []
    for item in data:
        # 只處理宜蘭地區的資料
        county = item.get("county", "")
        if "宜蘭" not in county:
            continue
            
        place_id = uuid.uuid4()
        
        # 處理位置
        try:
            lon = float(item.get("longitude", 0))
            lat = float(item.get("latitude", 0))
            if lon == 0 or lat == 0:
                continue
        except (ValueError, TypeError):
            continue
        
        point = Point(lon, lat)

        place_data = {
            "id": place_id,
            "name": item.get("name", "N/A"),
            "geom": from_shape(point, srid=4326),
            "categories": ["環保旅館", item.get("note", "")],
            "stay_minutes": 480,  # 住宿8小時
            "hours": []
        }
        processed.append(place_data)
    return processed

def process_education_facility_data(data: List[Dict]) -> List[Dict]:
    """處理環境教育設施資料（沒有座標）。"""
    processed = []
    for item in data:
        place_id = uuid.uuid4()
        
        # 環境教育設施沒有座標，暫時跳過
        continue  # 暫時跳過沒有座標的資料
        
    return processed

# --- DATABASE INTERACTION ---

def main():
    """主執行函式"""
    print("Connecting to the database...")
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Recreating database tables...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    all_places_data = []

    # 處理 TDX 餐廳資料
    print(f"Reading TDX restaurant data from {RESTAURANT_FILE}...")
    with open(RESTAURANT_FILE, 'r', encoding='utf-8') as f:
        restaurant_raw = json.load(f)
    restaurants = process_tdx_data(restaurant_raw, "restaurant")
    print(f"Processed {len(restaurants)} TDX restaurant records.")
    all_places_data.extend(restaurants)

    # 處理 TDX 景點資料
    print(f"Reading TDX scenic spot data from {SCENIC_SPOT_FILE}...")
    with open(SCENIC_SPOT_FILE, 'r', encoding='utf-8') as f:
        scenic_raw = json.load(f)
    scenic_spots = process_tdx_data(scenic_raw, "scenic_spot")
    print(f"Processed {len(scenic_spots)} TDX scenic spot records.")
    all_places_data.extend(scenic_spots)

    # 處理環保餐廳資料
    print(f"Reading eco restaurant data from {ECO_RESTAURANT_FILE}...")
    with open(ECO_RESTAURANT_FILE, 'r', encoding='utf-8') as f:
        eco_restaurant_raw = json.load(f)
    eco_restaurants = process_eco_restaurant_data(eco_restaurant_raw)
    print(f"Processed {len(eco_restaurants)} eco restaurant records.")
    all_places_data.extend(eco_restaurants)

    # 處理環保標章旅館資料
    print(f"Reading eco hotel data from {ECO_HOTEL_FILE}...")
    with open(ECO_HOTEL_FILE, 'r', encoding='utf-8') as f:
        eco_hotel_raw = json.load(f)
    eco_hotels = process_eco_hotel_data(eco_hotel_raw)
    print(f"Processed {len(eco_hotels)} eco hotel records.")
    all_places_data.extend(eco_hotels)

    # 處理旅館資料（暫時跳過，因為沒有座標）
    print(f"Reading hotel data from {HOTEL_FILE}...")
    with open(HOTEL_FILE, 'r', encoding='utf-8') as f:
        hotel_raw = json.load(f)
    hotels = process_hotel_data(hotel_raw, "hotel")
    print(f"Processed {len(hotels)} hotel records (skipped due to no coordinates).")
    all_places_data.extend(hotels)

    # 處理民宿資料（暫時跳過，因為沒有座標）
    print(f"Reading homestay data from {HOMESTAY_FILE}...")
    with open(HOMESTAY_FILE, 'r', encoding='utf-8') as f:
        homestay_raw = json.load(f)
    homestays = process_hotel_data(homestay_raw, "homestay")
    print(f"Processed {len(homestays)} homestay records (skipped due to no coordinates).")
    all_places_data.extend(homestays)

    # 處理環境教育設施資料（暫時跳過，因為沒有座標）
    print(f"Reading education facility data from {EDUCATION_FACILITY_FILE}...")
    with open(EDUCATION_FACILITY_FILE, 'r', encoding='utf-8') as f:
        education_raw = json.load(f)
    education_facilities = process_education_facility_data(education_raw)
    print(f"Processed {len(education_facilities)} education facility records (skipped due to no coordinates).")
    all_places_data.extend(education_facilities)
    
    print(f"Importing {len(all_places_data)} total records into the database...")
    
    # 先插入所有 Place
    for place_data in all_places_data:
        hours = place_data.pop("hours")
        place = Place(**place_data)
        session.add(place)
    
    # 提交 Place 資料
    session.commit()
    print("Places imported successfully!")
    
    # 再插入所有 Hour
    for place_data in all_places_data:
        hours = place_data.get("hours", [])
        for h_data in hours:
            hour = Hour(**h_data)
            session.add(hour)

    try:
        session.commit()
        print("Data import successful!")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()
        print("Database session closed.")

if __name__ == "__main__":
    main()
