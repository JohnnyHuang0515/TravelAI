#!/usr/bin/env python3
"""
統一的資料匯入管道
使用新的資料處理管道，在匯入時就完成所有處理
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Place, Accommodation
from itinerary_planner.infrastructure.data_processing.data_pipeline import DataProcessingPipeline, ProcessedData
from geoalchemy2 import WKTElement
from scripts.deduplication_manager import DeduplicationManager

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedDataImporter:
    """統一的資料匯入器"""
    
    def __init__(self):
        self.pipeline = DataProcessingPipeline()
        self.db = SessionLocal()
        self.deduplicator = DeduplicationManager()
    
    def _get_source_type(self, file_path: str) -> str:
        """根據檔案名稱判斷資料來源類型"""
        filename = Path(file_path).name
        
        if "環保標章旅館" in filename:
            return "eco_hotel"
        elif "環保餐廳" in filename:
            return "eco_restaurant"
        elif "環境教育設施" in filename:
            return "education_facility"
        elif "旅館名冊" in filename:
            return "yilan_hotel"
        elif "民宿名冊" in filename:
            return "yilan_bnb"
        else:
            return "default"
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def clear_existing_data(self):
        """清除現有資料"""
        logger.info("清除現有資料...")
        
        try:
            # 清除地點
            self.db.query(Place).delete()
            logger.info("已清除地點資料")
            
            # 清除住宿
            self.db.query(Accommodation).delete()
            logger.info("已清除住宿資料")
            
            self.db.commit()
            logger.info("資料清除完成")
            
        except Exception as e:
            logger.error(f"清除資料失敗: {e}")
            self.db.rollback()
            raise
    
    def load_json_data(self, file_path: str) -> List[Dict[str, Any]]:
        """載入 JSON 資料"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功載入 {file_path}: {len(data)} 筆資料")
            return data
            
        except Exception as e:
            logger.error(f"載入 {file_path} 失敗: {e}")
            raise
    
    def convert_processed_data_to_place(self, processed: ProcessedData) -> Place:
        """將處理後的資料轉換為 Place 物件"""
        place = Place(
            name=processed.name,
            description=processed.description,
            address=processed.address,
            categories=processed.categories,
            rating=processed.rating,
            price_range=processed.price_range,
            stay_minutes=processed.stay_minutes,
            place_metadata=processed.context_metadata
            # embedding=processed.embedding  # 暫時移除
        )
        
        # 設定地理位置
        if processed.latitude and processed.longitude:
            place.geom = WKTElement(f"POINT({processed.longitude} {processed.latitude})", srid=4326)
        
        return place
    
    def convert_processed_data_to_accommodation(self, processed: ProcessedData) -> Accommodation:
        """將處理後的資料轉換為 Accommodation 物件"""
        accommodation = Accommodation(
            name=processed.name,
            address=processed.address,
            type=processed.type,
            rating=processed.rating,
            price_range=processed.price_range,
            amenities=processed.amenities
            # embedding=processed.embedding  # 暫時移除
        )
        
        # 設定地理位置
        if processed.latitude and processed.longitude:
            accommodation.geom = WKTElement(f"POINT({processed.longitude} {processed.latitude})", srid=4326)
        
        return accommodation
    
    def import_places_from_file(self, file_path: str) -> int:
        """從檔案匯入地點資料"""
        logger.info(f"開始匯入地點資料: {file_path}")
        
        try:
            # 載入原始資料
            raw_data_list = self.load_json_data(file_path)
            
            # 去重處理
            source_type = self._get_source_type(file_path)
            if source_type in ["eco_hotel", "eco_restaurant", "education_facility"]:
                # 對新資料進行去重
                duplicate_groups = self.deduplicator.find_duplicates(raw_data_list, "place")
                if duplicate_groups:
                    logger.info(f"發現 {len(duplicate_groups)} 個重複組")
                    # 選擇最佳版本
                    resolved_items = self.deduplicator.resolve_duplicates(duplicate_groups, "eco_certified")
                    # 移除重複項目
                    for group in duplicate_groups.values():
                        for item in group[1:]:  # 保留第一個，移除其他
                            if item in raw_data_list:
                                raw_data_list.remove(item)
            
            # 批次處理資料
            processed_list = self.pipeline.batch_process(raw_data_list, "place", source_type)
            
            # 轉換為 ORM 物件並儲存
            imported_count = 0
            for i, processed in enumerate(processed_list):
                try:
                    place = self.convert_processed_data_to_place(processed)
                    self.db.add(place)
                    imported_count += 1
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"已處理 {i + 1}/{len(processed_list)} 個地點")
                        
                except Exception as e:
                    logger.error(f"處理地點 {processed.name} 失敗: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"地點匯入完成: {imported_count}/{len(raw_data_list)} 筆成功")
            return imported_count
            
        except Exception as e:
            logger.error(f"匯入地點失敗: {e}")
            self.db.rollback()
            raise
    
    def import_accommodations_from_file(self, file_path: str) -> int:
        """從檔案匯入住宿資料"""
        logger.info(f"開始匯入住宿資料: {file_path}")
        
        try:
            # 載入原始資料
            raw_data_list = self.load_json_data(file_path)
            
            # 去重處理
            source_type = self._get_source_type(file_path)
            if source_type == "eco_hotel":
                # 對環保標章旅館進行去重
                duplicate_groups = self.deduplicator.find_duplicates(raw_data_list, "accommodation")
                if duplicate_groups:
                    logger.info(f"發現 {len(duplicate_groups)} 個重複組")
                    # 選擇最佳版本
                    resolved_items = self.deduplicator.resolve_duplicates(duplicate_groups, "eco_certified")
                    # 移除重複項目
                    for group in duplicate_groups.values():
                        for item in group[1:]:  # 保留第一個，移除其他
                            if item in raw_data_list:
                                raw_data_list.remove(item)
            
            # 批次處理資料
            processed_list = self.pipeline.batch_process(raw_data_list, "accommodation", source_type)
            
            # 轉換為 ORM 物件並儲存
            imported_count = 0
            for i, processed in enumerate(processed_list):
                try:
                    accommodation = self.convert_processed_data_to_accommodation(processed)
                    self.db.add(accommodation)
                    imported_count += 1
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"已處理 {i + 1}/{len(processed_list)} 個住宿")
                        
                except Exception as e:
                    logger.error(f"處理住宿 {processed.name} 失敗: {e}")
                    continue
            
            self.db.commit()
            logger.info(f"住宿匯入完成: {imported_count}/{len(raw_data_list)} 筆成功")
            return imported_count
            
        except Exception as e:
            logger.error(f"匯入住宿失敗: {e}")
            self.db.rollback()
            raise
    
    def import_from_directory(self, data_dir: str, clear_existing: bool = True):
        """從目錄匯入所有資料"""
        logger.info(f"開始從目錄匯入資料: {data_dir}")
        
        if clear_existing:
            self.clear_existing_data()
        
        data_path = Path(data_dir)
        
        # 統計資訊
        total_places = 0
        total_accommodations = 0
        
        try:
            # 匯入地點資料
            place_files = [
                "宜蘭縣環保餐廳.json",
                "宜蘭縣遊憩類景點.json",
                "宜蘭縣自然風景類景點.json",
                "宜蘭縣文化類景點.json",
                "宜蘭縣溫泉類景點.json",
                "宜蘭縣甜點冰品.json",
                # 全台灣資料
                "環保餐廳環境即時通地圖資料.json",
                "環境教育設施場所認證資料.json"
            ]
            
            for file_name in place_files:
                file_path = data_path / file_name
                if file_path.exists():
                    count = self.import_places_from_file(str(file_path))
                    total_places += count
                else:
                    logger.warning(f"檔案不存在: {file_path}")
            
            # 匯入住宿資料
            accommodation_files = [
                "宜蘭縣旅館名冊.json",
                "宜蘭縣民宿名冊.json",
                # 全台灣資料
                "環保標章旅館環境即時通地圖資料.json"
            ]
            
            for file_name in accommodation_files:
                file_path = data_path / file_name
                if file_path.exists():
                    count = self.import_accommodations_from_file(str(file_path))
                    total_accommodations += count
                else:
                    logger.warning(f"檔案不存在: {file_path}")
            
            logger.info(f"資料匯入完成!")
            logger.info(f"總計匯入:")
            logger.info(f"  📍 地點: {total_places} 筆")
            logger.info(f"  🏨 住宿: {total_accommodations} 筆")
            logger.info(f"  📊 總計: {total_places + total_accommodations} 筆")
            
        except Exception as e:
            logger.error(f"資料匯入失敗: {e}")
            raise
    
    def get_import_statistics(self):
        """取得匯入統計資訊"""
        try:
            places_count = self.db.query(Place.id).count()
            accommodations_count = self.db.query(Accommodation.id).count()
            
            # 暫時移除 embedding 統計
            places_with_embedding = 0  # self.db.query(Place.id).filter(Place.embedding.isnot(None)).count()
            accommodations_with_embedding = 0  # self.db.query(Accommodation.id).filter(Accommodation.embedding.isnot(None)).count()
            
            places_with_metadata = self.db.query(Place.id).filter(Place.place_metadata.isnot(None)).count()
            
            places_with_coordinates = self.db.query(Place.id).filter(Place.geom.isnot(None)).count()
            accommodations_with_coordinates = self.db.query(Accommodation.id).filter(Accommodation.geom.isnot(None)).count()
            
            logger.info("📊 **資料庫統計資訊**")
            logger.info(f"📍 地點總數: {places_count}")
            logger.info(f"  - 有 embedding: {places_with_embedding}")
            logger.info(f"  - 有 metadata: {places_with_metadata}")
            logger.info(f"  - 有座標: {places_with_coordinates}")
            
            logger.info(f"🏨 住宿總數: {accommodations_count}")
            logger.info(f"  - 有 embedding: {accommodations_with_embedding}")
            logger.info(f"  - 有座標: {accommodations_with_coordinates}")
            
        except Exception as e:
            logger.error(f"取得統計資訊失敗: {e}")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='統一資料匯入器')
    parser.add_argument('--data-dir', default='docs', help='資料目錄路徑')
    parser.add_argument('--clear', action='store_true', help='清除現有資料')
    parser.add_argument('--stats-only', action='store_true', help='只顯示統計資訊')
    
    args = parser.parse_args()
    
    with UnifiedDataImporter() as importer:
        if args.stats_only:
            importer.get_import_statistics()
        else:
            importer.import_from_directory(args.data_dir, args.clear)
            importer.get_import_statistics()

if __name__ == "__main__":
    main()
