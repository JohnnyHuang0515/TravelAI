#!/usr/bin/env python3
"""
公車資料品質檢查腳本
檢查公車時刻表資料的品質和邏輯性
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
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

def check_data_quality(file_path):
    """
    檢查公車時刻表資料品質
    
    Args:
        file_path: 資料檔案路徑
        
    Returns:
        dict: 檢查結果
    """
    print(f"檢查資料檔案: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"資料筆數: {len(df)}")
    except Exception as e:
        print(f"❌ 讀取檔案失敗: {e}")
        return None
    
    results = {
        'file_path': file_path,
        'total_records': len(df),
        'issues': [],
        'statistics': {},
        'route_analysis': {}
    }
    
    # 基本統計
    results['statistics'] = {
        'total_routes': df['路線編號'].nunique(),
        'total_trips': df.groupby(['路線編號', '班次ID']).ngroups,
        'total_stops': df['站牌ID'].nunique(),
        'date_range': {
            'earliest_time': df['抵達時間'].min(),
            'latest_time': df['抵達時間'].max()
        }
    }
    
    print(f"路線數: {results['statistics']['total_routes']}")
    print(f"班次數: {results['statistics']['total_trips']}")
    print(f"站點數: {results['statistics']['total_stops']}")
    
    # 檢查時間邏輯
    print("\n=== 檢查時間邏輯 ===")
    time_logic_issues = 0
    
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
                    time_logic_issues += 1
                    if time_logic_issues <= 5:  # 只記錄前5個
                        results['issues'].append({
                            'type': 'arrival_after_departure',
                            'route': route_name,
                            'trip_id': trip_id,
                            'stop_sequence': current_stop['站序'],
                            'stop_name': current_stop['站名'],
                            'arrival': current_arrival,
                            'departure': current_departure
                        })
                
                # 檢查離站時間 <= 下一站抵達時間
                if time_to_minutes(current_departure) > time_to_minutes(next_arrival):
                    time_logic_issues += 1
                    if time_logic_issues <= 5:  # 只記錄前5個
                        results['issues'].append({
                            'type': 'departure_after_next_arrival',
                            'route': route_name,
                            'trip_id': trip_id,
                            'stop_sequence': current_stop['站序'],
                            'stop_name': current_stop['站名'],
                            'departure': current_departure,
                            'next_arrival': next_arrival
                        })
    
    results['statistics']['time_logic_issues'] = time_logic_issues
    
    if time_logic_issues > 0:
        print(f"❌ 發現 {time_logic_issues} 個時間邏輯問題")
        for issue in results['issues'][:3]:
            print(f"  - {issue['route']} {issue['trip_id']} 站序{issue['stop_sequence']}: {issue['type']}")
    else:
        print("✅ 時間邏輯檢查通過")
    
    # 檢查路線完整性
    print("\n=== 檢查路線完整性 ===")
    route_issues = 0
    
    for (route_name, direction, trip_id), group in grouped:
        # 檢查站序是否連續
        sequences = sorted(group['站序'].tolist())
        expected_sequences = list(range(1, len(sequences) + 1))
        
        if sequences != expected_sequences:
            route_issues += 1
            if route_issues <= 3:
                results['issues'].append({
                    'type': 'incomplete_sequence',
                    'route': route_name,
                    'trip_id': trip_id,
                    'expected': len(expected_sequences),
                    'actual': len(sequences),
                    'missing': set(expected_sequences) - set(sequences)
                })
    
    results['statistics']['route_issues'] = route_issues
    
    if route_issues > 0:
        print(f"❌ 發現 {route_issues} 個路線完整性问题")
    else:
        print("✅ 路線完整性檢查通過")
    
    # 分析路線特徵
    print("\n=== 路線特徵分析 ===")
    
    for route_name in df['路線編號'].unique()[:5]:  # 只分析前5條路線
        route_data = df[df['路線編號'] == route_name]
        
        route_stats = {
            'total_trips': route_data.groupby('班次ID').ngroups,
            'total_stops': route_data['站牌ID'].nunique(),
            'avg_trip_duration': 0,
            'time_range': {
                'earliest': route_data['抵達時間'].min(),
                'latest': route_data['抵達時間'].max()
            }
        }
        
        # 計算平均行程時間
        trip_durations = []
        for trip_id in route_data['班次ID'].unique():
            trip_data = route_data[route_data['班次ID'] == trip_id].sort_values('站序')
            if len(trip_data) > 1:
                first_time = parse_time(trip_data.iloc[0]['抵達時間'])
                last_time = parse_time(trip_data.iloc[-1]['抵達時間'])
                if first_time and last_time:
                    duration = time_to_minutes(last_time) - time_to_minutes(first_time)
                    if duration > 0:
                        trip_durations.append(duration)
        
        if trip_durations:
            route_stats['avg_trip_duration'] = np.mean(trip_durations)
        
        results['route_analysis'][route_name] = route_stats
        
        print(f"{route_name}: {route_stats['total_trips']}班次, {route_stats['total_stops']}站點, "
              f"平均{route_stats['avg_trip_duration']:.1f}分鐘")
    
    # 時間分佈分析
    print("\n=== 時間分佈分析 ===")
    
    df['抵達時間'] = pd.to_datetime(df['抵達時間'], format='%H:%M', errors='coerce').dt.time
    df['小時'] = df['抵達時間'].apply(lambda x: x.hour if pd.notna(x) else -1)
    
    hour_distribution = df['小時'].value_counts().sort_index()
    
    print("班次時間分佈:")
    for hour, count in hour_distribution.items():
        if hour >= 0:
            print(f"  {hour:02d}:00 - {count:4d} 班次")
    
    results['statistics']['hour_distribution'] = hour_distribution.to_dict()
    
    # 總結
    print(f"\n=== 資料品質總結 ===")
    print(f"總記錄數: {results['total_records']}")
    print(f"路線數: {results['statistics']['total_routes']}")
    print(f"班次數: {results['statistics']['total_trips']}")
    print(f"站點數: {results['statistics']['total_stops']}")
    print(f"時間邏輯問題: {results['statistics']['time_logic_issues']}")
    print(f"路線完整性问题: {results['statistics']['route_issues']}")
    
    if results['statistics']['time_logic_issues'] == 0 and results['statistics']['route_issues'] == 0:
        print("✅ 資料品質良好")
    else:
        print("⚠️  資料品質需要改善")
    
    return results

def compare_data_files(file1_path, file2_path):
    """
    比較兩個資料檔案的差異
    
    Args:
        file1_path: 第一個檔案路徑
        file2_path: 第二個檔案路徑
    """
    print(f"\n=== 比較資料檔案 ===")
    print(f"檔案1: {file1_path}")
    print(f"檔案2: {file2_path}")
    
    try:
        df1 = pd.read_csv(file1_path)
        df2 = pd.read_csv(file2_path)
        
        print(f"檔案1記錄數: {len(df1)}")
        print(f"檔案2記錄數: {len(df2)}")
        
        # 檢查時間差異
        if '抵達時間' in df1.columns and '抵達時間' in df2.columns:
            # 隨機選擇一些記錄比較
            sample_size = min(100, len(df1), len(df2))
            sample1 = df1.sample(n=sample_size, random_state=42)
            sample2 = df2.sample(n=sample_size, random_state=42)
            
            time_changes = 0
            for i in range(sample_size):
                if i < len(sample2):
                    time1 = sample1.iloc[i]['抵達時間']
                    time2 = sample2.iloc[i]['抵達時間']
                    if time1 != time2:
                        time_changes += 1
            
            print(f"時間變化記錄數: {time_changes}/{sample_size}")
            
    except Exception as e:
        print(f"❌ 比較檔案失敗: {e}")

def main():
    """主程式"""
    print("=== 公車資料品質檢查程式 ===")
    
    # 檔案路徑
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data", "osrm", "data")
    
    files_to_check = [
        os.path.join(data_dir, "stop_times.csv"),
        os.path.join(data_dir, "stop_times_enhanced.csv"),
        os.path.join(data_dir, "stop_times_backup.csv")
    ]
    
    results = {}
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n{'='*60}")
            result = check_data_quality(file_path)
            if result:
                results[file_path] = result
        else:
            print(f"檔案不存在: {file_path}")
    
    # 比較檔案
    if len(results) >= 2:
        file_paths = list(results.keys())
        compare_data_files(file_paths[0], file_paths[1])
    
    print(f"\n{'='*60}")
    print("=== 檢查完成 ===")

if __name__ == "__main__":
    main()
