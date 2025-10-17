#!/usr/bin/env python3
"""
OSRM 服務啟動腳本
用於啟動和管理 OSRM 路由服務
"""

import os
import sys
import time
import signal
import argparse
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.itinerary_planner.infrastructure.routing.osrm_service import OSRMManager, get_osrm_manager

class OSRMServiceManager:
    """OSRM 服務管理器"""
    
    def __init__(self):
        self.manager = get_osrm_manager()
        self.running = False
    
    def start_service(self, data_dir: str = None) -> bool:
        """啟動 OSRM 服務"""
        print("=== OSRM 服務管理器 ===")
        
        if data_dir:
            self.manager.data_dir = data_dir
        
        print(f"資料目錄: {self.manager.data_dir}")
        
        # 檢查資料檔案
        osrm_file = os.path.join(self.manager.data_dir, "taiwan-250923.osrm")
        if not os.path.exists(osrm_file):
            print(f"錯誤: 找不到 OSRM 資料檔案 {osrm_file}")
            print("請確認資料檔案路徑正確")
            return False
        
        print("正在啟動 OSRM 服務...")
        
        if self.manager.ensure_service_running():
            self.running = True
            print("✅ OSRM 服務啟動成功")
            print(f"服務地址: http://localhost:5000")
            print("按 Ctrl+C 停止服務")
            return True
        else:
            print("❌ OSRM 服務啟動失敗")
            return False
    
    def stop_service(self):
        """停止 OSRM 服務"""
        if self.running:
            print("\n正在停止 OSRM 服務...")
            self.manager.cleanup()
            self.running = False
            print("✅ OSRM 服務已停止")
    
    def run_interactive(self):
        """執行互動式服務"""
        def signal_handler(signum, frame):
            print(f"\n收到信號 {signum}，正在停止服務...")
            self.stop_service()
            sys.exit(0)
        
        # 註冊信號處理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # 保持服務運行
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_service()

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description="OSRM 服務管理器")
    parser.add_argument(
        "--data-dir", 
        type=str, 
        help="OSRM 資料目錄路徑"
    )
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="檢查 OSRM 服務狀態"
    )
    parser.add_argument(
        "--stop", 
        action="store_true", 
        help="停止 OSRM 服務"
    )
    
    args = parser.parse_args()
    
    # 預設資料目錄
    if not args.data_dir:
        args.data_dir = os.path.join(project_root, "data", "osrm")
    
    manager = OSRMServiceManager()
    
    if args.check:
        # 檢查服務狀態
        service = manager.manager.get_service()
        if service.is_service_running():
            print("✅ OSRM 服務正在運行")
        else:
            print("❌ OSRM 服務未運行")
        return
    
    if args.stop:
        # 停止服務
        manager.stop_service()
        return
    
    # 啟動服務
    if manager.start_service(args.data_dir):
        manager.run_interactive()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

