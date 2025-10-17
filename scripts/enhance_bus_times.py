#!/usr/bin/env python3
"""
公車時刻表增強腳本
進一步優化公車時刻表的時間計算邏輯
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import os
import sys

def parse_time(time_str):
    """解析時間字串"""
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except:
        return None

def time_to_minutes(time_obj):
    """將時間轉換為分鐘數"""
    if time_obj is None:
        return 0
    return time_obj.hour * 60 + time_obj.minute

def minutes_to_time(minutes):
    """將分鐘數轉換為時間"""
    minutes = minutes % (24 * 60)
    hours = minutes // 60
    mins = minutes % 60
    return time(hours, mins)

def calculate_realistic_times(start_time, end_time, num_stations, distances=None):
    """
    根據首末站時間、站點數和距離計算更真實的時間
    
    Args:
        start_time: 起始時間
        end_time: 結束時間
        num_stations: 站點總數
        distances: 站點間距離列表（可選）
        
    Returns:
        List[time]: 每個站點的時間列表
    """
    if num_stations <= 1:
        return [start_time]
    
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    
    # 計算總行程時間
    total_minutes = end_minutes - start_minutes
    if total_minutes <= 0:
        total_minutes += 24 * 60
    
    times = [start_time]
    
    if distances and len(distances) == num_stations - 1:
        # 根據距離比例分配時間
        total_distance = sum(distances)
        if total_distance > 0:
            current_minutes = start_minutes
            for i, distance in enumerate(distances[:-1]):
                # 根據距離比例計算時間
                segment_time = (distance / total_distance) * total_minutes
                current_minutes += segment_time
                times.append(minutes_to_time(int(current_minutes)))
            times.append(end_time)
        else:
            # 如果沒有距離資料，使用均勻分配
            times = calculate_uniform_times(start_time, end_time, num_stations)
    else:
        # 使用均勻分配
        times = calculate_uniform_times(start_time, end_time, num_stations)
    
    return times

def calculate_uniform_times(start_time, end_time, num_stations):
    """均勻分配時間"""
    if num_stations <= 1:
        return [start_time]
    
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    
    total_minutes = end_minutes - start_minutes
    if total_minutes <= 0:
        total_minutes += 24 * 60
    
    interval = total_minutes / (num_stations - 1)
    
    times = []
    for i in range(num_stations):
        station_minutes = start_minutes + (interval * i)
        times.append(minutes_to_time(int(station_minutes)))
    
    return times

def add_realistic_variations(times, variation_config=None):
    """
    添加更真實的時間變化
    
    Args:
        times: 時間列表
        variation_config: 變化配置
    """
    if len(times) <= 2:
        return times
    
    if variation_config is None:
        variation_config = {
            'base_variation': 1,      # 基礎變化（分鐘）
            'peak_variation': 3,      # 高峰時段變化（分鐘）
            'night_variation': 2,     # 夜間變化（分鐘）
            'distance_factor': 0.5    # 距離因子
        }
    
    result = [times[0]]  # 首站保持不變
    
    for i in range(1, len(times) - 1):
        base_time = times[i]
        base_minutes = time_to_minutes(base_time)
        
        # 根據時間段調整變化範圍
        hour = base_time.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # 高峰時段
            variation_range = variation_config['peak_variation']
        elif 22 <= hour or hour <= 5:  # 夜間時段
            variation_range = variation_config['night_variation']
        else:
            variation_range = variation_config['base_variation']
        
        # 添加隨機變化
        variation = np.random.randint(-variation_range, variation_range + 1)
        new_minutes = base_minutes + variation
        
        # 確保時間不早於前一個站點
        prev_minutes = time_to_minutes(result[-1])
        new_minutes = max(new_minutes, prev_minutes + 1)
        
        # 確保不晚於下一個站點（如果知道的話）
        if i < len(times) - 1:
            next_minutes = time_to_minutes(times[i + 1])
            new_minutes = min(new_minutes, next_minutes - 1)
        
        result.append(minutes_to_time(new_minutes))
    
    # 末站保持不變
    result.append(times[-1])
    
    return result

def calculate_stop_duration(arrival_time, station_type="normal"):
    """
    計算站點停靠時間
    
    Args:
        arrival_time: 抵達時間
        station_type: 站點類型 (normal, transfer, terminal)
        
    Returns:
        int: 停靠時間（分鐘）
    """
    # 根據站點類型決定停靠時間
    if station_type == "terminal":
        return 3  # 終點站停靠3分鐘
    elif station_type == "transfer":
        return 2  # 轉乘站停靠2分鐘
    else:
        return 1  # 一般站點停靠1分鐘

def enhance_stop_times_data(input_file, output_file):
    """
    增強公車時刻表資料
    
    Args:
        input_file: 輸入檔案路徑
        output_file: 輸出檔案路徑
    """
    print(f"讀取資料: {input_file}")
    df = pd.read_csv(input_file)
    
    print(f"原始資料筆數: {len(df)}")
    
    enhanced_data = []
    
    # 按路線、方向、班次分組處理
    grouped = df.groupby(['路線編號', '方向', '班次ID'])
    
    total_groups = len(grouped)
    processed = 0
    
    for (route_name, direction, trip_id), group in grouped:
        processed += 1
        if processed % 50 == 0:
            print(f"處理進度: {processed}/{total_groups}")
        
        # 按站序排序
        group = group.sort_values('站序').reset_index(drop=True)
        
        if len(group) == 0:
            continue
        
        # 取得首末站時間
        first_stop = group.iloc[0]
        last_stop = group.iloc[-1]
        
        start_time = parse_time(first_stop['抵達時間'])
        end_time = parse_time(last_stop['抵達時間'])
        
        if start_time is None or end_time is None:
            enhanced_data.extend(group.to_dict('records'))
            continue
        
        # 計算站點間距離（簡化計算）
        distances = []
        for i in range(len(group) - 1):
            current_stop = group.iloc[i]
            next_stop = group.iloc[i + 1]
            
            # 簡化距離計算（實際應用中可以使用更精確的地理距離）
            lat_diff = abs(float(current_stop['緯度']) - float(next_stop['緯度']))
            lon_diff = abs(float(current_stop['經度']) - float(next_stop['經度']))
            distance = (lat_diff + lon_diff) * 111000  # 簡化為公尺
            distances.append(max(distance, 100))  # 最小100公尺
        
        # 計算更真實的時間
        realistic_times = calculate_realistic_times(
            start_time, end_time, len(group), distances
        )
        
        # 添加變化
        enhanced_times = add_realistic_variations(realistic_times)
        
        # 更新每個站點的時間
        for i, (_, stop) in enumerate(group.iterrows()):
            arrival_time = enhanced_times[i]
            arrival_minutes = time_to_minutes(arrival_time)
            
            # 根據站點類型決定停靠時間
            station_type = "terminal" if i == len(group) - 1 else "normal"
            stop_duration = calculate_stop_duration(arrival_time, station_type)
            
            departure_minutes = arrival_minutes + stop_duration
            departure_time = minutes_to_time(departure_minutes)
            
            # 建立增強後的記錄
            enhanced_record = stop.to_dict()
            enhanced_record['抵達時間'] = arrival_time.strftime('%H:%M')
            enhanced_record['離站時間'] = departure_time.strftime('%H:%M')
            
            enhanced_data.append(enhanced_record)
    
    # 轉換為 DataFrame 並保存
    enhanced_df = pd.DataFrame(enhanced_data)
    
    # 確保欄位順序
    column_order = ['路線編號', '方向', '班次ID', '站序', '站名', '站牌ID', 
                   '緯度', '經度', '抵達時間', '離站時間', '營運日']
    enhanced_df = enhanced_df[column_order]
    
    print(f"增強後資料筆數: {len(enhanced_df)}")
    
    # 保存增強後的資料
    enhanced_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"增強後的資料已保存至: {output_file}")
    
    # 顯示一些範例
    print("\n=== 增強範例 ===")
    sample_route = enhanced_df[enhanced_df['路線編號'] == '紅1'].head(10)
    for _, row in sample_route.iterrows():
        print(f"{row['站序']:2d}. {row['站名']:12s} 抵達: {row['抵達時間']} 離站: {row['離站時間']}")
    
    return enhanced_df

def validate_enhanced_data(df):
    """驗證增強後的資料"""
    print("\n=== 資料驗證 ===")
    
    # 檢查時間邏輯
    issues = []
    
    grouped = df.groupby(['路線編號', '方向', '班次ID'])
    
    for (route_name, direction, trip_id), group in grouped:
        group = group.sort_values('站序')
        
        for i in range(len(group) - 1):
            current_stop = group.iloc[i]
            next_stop = group.iloc[i + 1]
            
            current_arrival = parse_time(current_stop['抵達時間'])
            current_departure = parse_time(current_stop['離站時間'])
            next_arrival = parse_time(next_stop['抵達時間'])
            
            if current_arrival and current_departure and next_arrival:
                # 檢查抵達時間 <= 離站時間
                if time_to_minutes(current_arrival) > time_to_minutes(current_departure):
                    issues.append(f"{route_name} {trip_id} 站序{current_stop['站序']}: 抵達時間晚於離站時間")
                
                # 檢查離站時間 <= 下一站抵達時間
                if time_to_minutes(current_departure) > time_to_minutes(next_arrival):
                    issues.append(f"{route_name} {trip_id} 站序{current_stop['站序']}: 離站時間晚於下一站抵達時間")
    
    if issues:
        print(f"發現 {len(issues)} 個時間邏輯問題:")
        for issue in issues[:5]:  # 只顯示前5個
            print(f"  - {issue}")
        if len(issues) > 5:
            print(f"  ... 還有 {len(issues) - 5} 個問題")
    else:
        print("✅ 時間邏輯驗證通過")
    
    # 統計資訊
    print(f"\n=== 統計資訊 ===")
    print(f"總路線數: {df['路線編號'].nunique()}")
    print(f"總班次數: {df.groupby(['路線編號', '班次ID']).ngroups}")
    print(f"總站點記錄數: {len(df)}")
    
    # 時間分佈統計
    df['抵達時間'] = pd.to_datetime(df['抵達時間'], format='%H:%M').dt.time
    df['小時'] = df['抵達時間'].apply(lambda x: x.hour)
    
    print(f"\n班次時間分佈:")
    time_distribution = df['小時'].value_counts().sort_index()
    for hour, count in time_distribution.items():
        print(f"  {hour:02d}:00 - {count:4d} 班次")

def main():
    """主程式"""
    print("=== 公車時刻表增強程式 ===")
    
    # 檔案路徑
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(project_root, "data", "osrm", "data", "stop_times.csv")
    output_file = os.path.join(project_root, "data", "osrm", "data", "stop_times_enhanced.csv")
    
    # 檢查輸入檔案
    if not os.path.exists(input_file):
        print(f"❌ 找不到輸入檔案: {input_file}")
        sys.exit(1)
    
    try:
        # 增強資料
        enhanced_df = enhance_stop_times_data(input_file, output_file)
        
        # 驗證增強後的資料
        validate_enhanced_data(enhanced_df)
        
        print(f"\n=== 增強完成 ===")
        print(f"原始檔案: {input_file}")
        print(f"增強檔案: {output_file}")
        
        # 詢問是否替換原始檔案
        print("\n是否要替換原始檔案？(y/N): ", end="")
        try:
            replace = input().strip().lower()
            if replace == 'y':
                import shutil
                shutil.copy2(output_file, input_file)
                print("✅ 已替換原始檔案")
            else:
                print("ℹ️  保留原始檔案，增強後的資料在 stop_times_enhanced.csv")
        except EOFError:
            print("ℹ️  保留原始檔案，增強後的資料在 stop_times_enhanced.csv")
        
    except Exception as e:
        print(f"❌ 增強過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
