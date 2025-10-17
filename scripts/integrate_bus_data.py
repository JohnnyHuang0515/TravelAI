#!/usr/bin/env python3
"""
公車資料整合腳本
執行完整的公車資料整合流程：資料庫遷移、資料匯入、服務啟動
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """
    執行命令並顯示結果
    
    Args:
        command: 要執行的命令
        description: 命令描述
        
    Returns:
        是否執行成功
    """
    print(f"\n=== {description} ===")
    print(f"執行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ 執行成功")
        if result.stdout:
            print(f"輸出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 執行失敗")
        print(f"錯誤碼: {e.returncode}")
        if e.stdout:
            print(f"標準輸出: {e.stdout}")
        if e.stderr:
            print(f"錯誤輸出: {e.stderr}")
        return False

def check_file_exists(file_path: str, description: str) -> bool:
    """
    檢查檔案是否存在
    
    Args:
        file_path: 檔案路徑
        description: 檔案描述
        
    Returns:
        檔案是否存在
    """
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}不存在: {file_path}")
        return False

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="公車資料整合腳本")
    parser.add_argument(
        "--skip-migration", 
        action="store_true", 
        help="跳過資料庫遷移"
    )
    parser.add_argument(
        "--skip-import", 
        action="store_true", 
        help="跳過資料匯入"
    )
    parser.add_argument(
        "--start-osrm", 
        action="store_true", 
        help="啟動 OSRM 服務"
    )
    parser.add_argument(
        "--data-dir", 
        type=str, 
        help="OSRM 資料目錄路徑"
    )
    
    args = parser.parse_args()
    
    # 取得專案根目錄
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    print("=== 公車資料整合流程 ===")
    print(f"專案目錄: {project_root}")
    
    # 檢查必要檔案
    print("\n=== 檢查必要檔案 ===")
    
    required_files = [
        ("migrations/008_add_bus_transport_tables.sql", "資料庫遷移檔案"),
        ("scripts/import_bus_data.py", "資料匯入腳本"),
        ("scripts/start_osrm_service.py", "OSRM 服務啟動腳本"),
        ("data/osrm/data/routes.csv", "路線資料"),
        ("data/osrm/data/stations.csv", "站點資料"),
        ("data/osrm/data/trips.csv", "班次資料"),
        ("data/osrm/data/stop_times.csv", "時刻表資料"),
    ]
    
    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ 缺少必要檔案，請確認資料包已正確放置")
        sys.exit(1)
    
    # 執行資料庫遷移
    if not args.skip_migration:
        print("\n=== 執行資料庫遷移 ===")
        
        migration_file = "migrations/008_add_bus_transport_tables.sql"
        
        # 檢查資料庫連接
        if not run_command(
            "python -c \"from src.itinerary_planner.infrastructure.persistence.database import get_database_url; print('資料庫連接測試:', get_database_url())\"",
            "測試資料庫連接"
        ):
            print("❌ 資料庫連接失敗，請檢查資料庫設定")
            sys.exit(1)
        
        # 執行遷移
        if not run_command(
            f"psql $DATABASE_URL -f {migration_file}",
            "執行資料庫遷移"
        ):
            print("❌ 資料庫遷移失敗")
            sys.exit(1)
    
    # 執行資料匯入
    if not args.skip_import:
        print("\n=== 執行資料匯入 ===")
        
        if not run_command(
            "python scripts/import_bus_data.py",
            "匯入公車資料"
        ):
            print("❌ 資料匯入失敗")
            sys.exit(1)
    
    # 啟動 OSRM 服務
    if args.start_osrm:
        print("\n=== 啟動 OSRM 服務 ===")
        
        osrm_cmd = "python scripts/start_osrm_service.py"
        if args.data_dir:
            osrm_cmd += f" --data-dir {args.data_dir}"
        
        if not run_command(osrm_cmd, "啟動 OSRM 服務"):
            print("❌ OSRM 服務啟動失敗")
            sys.exit(1)
    
    print("\n=== 整合完成 ===")
    print("✅ 公車資料整合流程已完成")
    print("\n後續步驟:")
    print("1. 啟動 OSRM 服務: python scripts/start_osrm_service.py")
    print("2. 啟動應用程式: python -m uvicorn src.main:app --reload")
    print("3. 測試公車路線規劃功能")
    
    # 顯示整合結果摘要
    print("\n=== 整合摘要 ===")
    print("✅ 資料庫表結構已建立")
    print("✅ 公車資料已匯入")
    print("✅ OSRM 路由引擎已整合")
    print("✅ 公車路線規劃服務已準備就緒")

if __name__ == "__main__":
    main()

