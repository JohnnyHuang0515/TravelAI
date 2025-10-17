#!/usr/bin/env python3
"""
公車時刻表修正腳本
根據首末站時間和站點數來合理計算每個站點的到站時間
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
    # 確保分鐘數在合理範圍內
    minutes = minutes % (24 * 60)  # 限制在一天內
    hours = minutes // 60
    mins = minutes % 60
    return time(hours, mins)

def calculate_interpolated_times(start_time, end_time, num_stations):
    """
    根據首末站時間和站點數計算每個站點的時間
    
    Args:
        start_time: 起始時間 (time object)
        end_time: 結束時間 (time object)
        num_stations: 站點總數
        
    Returns:
        List[time]: 每個站點的時間列表
    """
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)
    
    # 計算總行程時間
    total_minutes = end_minutes - start_minutes
    if total_minutes <= 0:
        total_minutes += 24 * 60  # 跨日處理
    
    # 計算每個站點間的平均時間間隔
    if num_stations <= 1:
        return [start_time]
    
    # 站點間隔時間 (分鐘)
    interval_minutes = total_minutes / (num_stations - 1)
    
    times = []
    for i in range(num_stations):
        station_minutes = start_minutes + (interval_minutes * i)
        # 處理跨日情況
        station_minutes = station_minutes % (24 * 60)
        times.append(minutes_to_time(int(station_minutes)))
    
    return times

def add_realistic_variation(times, variation_range=1):
    """
    為時間添加合理的變化，模擬實際公車運行
    
    Args:
        times: 時間列表
        variation_range: 變化範圍 (分鐘)
        
    Returns:
        List[time]: 添加變化後的時間列表
    """
    if len(times) <= 2:
        return times
    
    # 為中間站點添加隨機變化
    result = [times[0]]  # 首站保持不變
    
    for i in range(1, len(times) - 1):
        base_time = times[i]
        variation = np.random.randint(-variation_range, variation_range + 1)
        
        base_minutes = time_to_minutes(base_time)
        new_minutes = base_minutes + variation
        
        # 確保時間不早於前一個站點
        prev_minutes = time_to_minutes(result[-1])
        new_minutes = max(new_minutes, prev_minutes + 1)
        
        # 處理跨日
        new_minutes = new_minutes % (24 * 60)
        result.append(minutes_to_time(new_minutes))
    
    # 末站保持不變
    result.append(times[-1])
    
    return result

def fix_stop_times_data(input_file, output_file):
    """
    修正公車時刻表資料
    
    Args:
        input_file: 輸入檔案路徑
        output_file: 輸出檔案路徑
    """
    print(f"讀取資料: {input_file}")
    df = pd.read_csv(input_file)
    
    print(f"原始資料筆數: {len(df)}")
    
    # 修正後的資料
    fixed_data = []
    
    # 按路線、方向、班次分組處理
    grouped = df.groupby(['路線編號', '方向', '班次ID'])
    
    total_groups = len(grouped)
    processed = 0
    
    for (route_name, direction, trip_id), group in grouped:
        processed += 1
        if processed % 100 == 0:
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
            # 如果時間解析失敗，使用原始資料
            fixed_data.extend(group.to_dict('records'))
            continue
        
        # 計算合理的站點時間
        num_stations = len(group)
        interpolated_times = calculate_interpolated_times(start_time, end_time, num_stations)
        
        # 添加合理變化
        realistic_times = add_realistic_variation(interpolated_times, variation_range=1)
        
        # 更新每個站點的時間
        for i, (_, stop) in enumerate(group.iterrows()):
            new_arrival_time = realistic_times[i]
            
            # 離站時間通常是抵達時間 + 1分鐘（模擬停靠時間）
            arrival_minutes = time_to_minutes(new_arrival_time)
            departure_minutes = arrival_minutes + 1
            new_departure_time = minutes_to_time(departure_minutes)
            
            # 建立修正後的記錄
            fixed_record = stop.to_dict()
            fixed_record['抵達時間'] = new_arrival_time.strftime('%H:%M')
            fixed_record['離站時間'] = new_departure_time.strftime('%H:%M')
            
            fixed_data.append(fixed_record)
    
    # 轉換為 DataFrame 並保存
    fixed_df = pd.DataFrame(fixed_data)
    
    # 確保欄位順序
    column_order = ['路線編號', '方向', '班次ID', '站序', '站名', '站牌ID', 
                   '緯度', '經度', '抵達時間', '離站時間', '營運日']
    fixed_df = fixed_df[column_order]
    
    print(f"修正後資料筆數: {len(fixed_df)}")
    
    # 保存修正後的資料
    fixed_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"修正後的資料已保存至: {output_file}")
    
    # 顯示一些範例
    print("\n=== 修正範例 ===")
    sample_route = fixed_df[fixed_df['路線編號'] == '紅1'].head(10)
    for _, row in sample_route.iterrows():
        print(f"{row['站序']:2d}. {row['站名']:12s} 抵達: {row['抵達時間']} 離站: {row['離站時間']}")
    
    return fixed_df

def validate_fixed_data(df):
    """驗證修正後的資料"""
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
        for issue in issues[:10]:  # 只顯示前10個
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... 還有 {len(issues) - 10} 個問題")
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
    print("=== 公車時刻表修正程式 ===")
    
    # 檔案路徑
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(project_root, "data", "osrm", "data", "stop_times.csv")
    output_file = os.path.join(project_root, "data", "osrm", "data", "stop_times_fixed.csv")
    backup_file = os.path.join(project_root, "data", "osrm", "data", "stop_times_backup.csv")
    
    # 檢查輸入檔案
    if not os.path.exists(input_file):
        print(f"❌ 找不到輸入檔案: {input_file}")
        sys.exit(1)
    
    # 備份原始檔案
    if os.path.exists(input_file) and not os.path.exists(backup_file):
        print(f"備份原始檔案到: {backup_file}")
        import shutil
        shutil.copy2(input_file, backup_file)
    
    try:
        # 修正資料
        fixed_df = fix_stop_times_data(input_file, output_file)
        
        # 驗證修正後的資料
        validate_fixed_data(fixed_df)
        
        print(f"\n=== 修正完成 ===")
        print(f"原始檔案: {input_file}")
        print(f"修正檔案: {output_file}")
        print(f"備份檔案: {backup_file}")
        
        # 詢問是否替換原始檔案
        replace = input("\n是否要替換原始檔案？(y/N): ").strip().lower()
        if replace == 'y':
            import shutil
            shutil.copy2(output_file, input_file)
            print("✅ 已替換原始檔案")
        else:
            print("ℹ️  保留原始檔案，修正後的資料在 stop_times_fixed.csv")
        
    except Exception as e:
        print(f"❌ 修正過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
