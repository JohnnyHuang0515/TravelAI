"""
去重管理器
處理資料匯入時的重複問題
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)

class DeduplicationManager:
    """去重管理器"""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        初始化去重管理器
        
        Args:
            similarity_threshold: 相似度閾值，超過此值視為重複
        """
        self.similarity_threshold = similarity_threshold
        self.duplicate_groups: Dict[str, List[Dict]] = {}
    
    def normalize_name(self, name: str) -> str:
        """正規化名稱用於比較"""
        if not name:
            return ""
        
        # 移除特殊字符和空格
        normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', name.lower())
        
        # 移除常見的後綴
        suffixes = ['飯店', '酒店', '旅館', '民宿', '餐廳', '咖啡廳', '館', '店']
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        
        return normalized
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """計算兩個名稱的相似度"""
        if not name1 or not name2:
            return 0.0
        
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # 使用 SequenceMatcher 計算相似度
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # 如果其中一個名稱包含另一個，提高相似度
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.9)
        
        return similarity
    
    def is_same_location(self, address1: str, address2: str) -> bool:
        """判斷兩個地址是否在同一位置"""
        if not address1 or not address2:
            return False
        
        # 縣市列表
        cities = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', 
                 '宜蘭縣', '花蓮縣', '台東縣', '南投縣', '雲林縣', '嘉義縣', 
                 '彰化縣', '苗栗縣', '基隆市', '新竹縣', '新竹市', '金門縣', 
                 '澎湖縣', '連江縣']
        
        # 提取縣市資訊
        def extract_city(address):
            for city in cities:
                if city in address:
                    return city
            return None
        
        city1 = extract_city(address1)
        city2 = extract_city(address2)
        
        # 如果縣市不同，肯定不是同一位置
        if city1 != city2:
            return False
        
        # 提取街道資訊進行更詳細比較
        def extract_street(address):
            # 移除縣市部分
            for city in cities:
                address = address.replace(city, '')
            
            # 提取路名
            street_match = re.search(r'([^0-9]+路|[^0-9]+街|[^0-9]+巷)', address)
            if street_match:
                return street_match.group(1)
            return None
        
        street1 = extract_street(address1)
        street2 = extract_street(address2)
        
        # 如果街道相同，視為同一位置
        if street1 and street2 and street1 == street2:
            return True
        
        return False
    
    def find_duplicates(self, items: List[Dict], item_type: str = "place") -> Dict[str, List[Dict]]:
        """
        找出重複項目
        
        Args:
            items: 要檢查的項目列表
            item_type: 項目類型 ("place" 或 "accommodation")
        
        Returns:
            重複組的字典，key 為組 ID，value 為重複項目列表
        """
        duplicate_groups = {}
        processed_indices = set()
        
        for i, item1 in enumerate(items):
            if i in processed_indices:
                continue
            
            name1 = item1.get('name', '') or item1.get('中文名稱', '')
            address1 = item1.get('address', '') or item1.get('地址', '')
            
            if not name1:
                continue
            
            duplicates = [item1]
            group_key = f"{item_type}_{i}"
            
            for j, item2 in enumerate(items[i+1:], i+1):
                if j in processed_indices:
                    continue
                
                name2 = item2.get('name', '') or item2.get('中文名稱', '')
                address2 = item2.get('address', '') or item2.get('地址', '')
                
                if not name2:
                    continue
                
                # 檢查名稱相似度
                name_similarity = self.calculate_similarity(name1, name2)
                
                # 檢查地址是否相同
                same_location = self.is_same_location(address1, address2)
                
                # 判斷是否為重複
                is_duplicate = (name_similarity >= self.similarity_threshold and same_location)
                
                if is_duplicate:
                    duplicates.append(item2)
                    processed_indices.add(j)
            
            # 如果找到重複項目，記錄到組中
            if len(duplicates) > 1:
                duplicate_groups[group_key] = duplicates
                processed_indices.add(i)
        
        return duplicate_groups
    
    def resolve_duplicates(self, duplicate_groups: Dict[str, List[Dict]], 
                          priority_source: str = "eco_certified") -> List[Dict]:
        """
        解決重複問題，選擇最佳版本
        
        Args:
            duplicate_groups: 重複組字典
            priority_source: 優先來源類型
        
        Returns:
            去重後的項目列表
        """
        resolved_items = []
        
        for group_key, duplicates in duplicate_groups.items():
            # 選擇最佳版本
            best_item = self._select_best_version(duplicates, priority_source)
            resolved_items.append(best_item)
            
            logger.info(f"重複組 {group_key}: 選擇 {best_item.get('name', best_item.get('中文名稱', 'Unknown'))}")
        
        return resolved_items
    
    def _select_best_version(self, duplicates: List[Dict], priority_source: str) -> Dict:
        """選擇最佳版本的重複項目"""
        if len(duplicates) == 1:
            return duplicates[0]
        
        # 優先級規則
        priority_rules = {
            "eco_certified": [
                lambda item: "環保標章" in str(item.get('certification_type', '')),
                lambda item: "環保" in str(item.get('certification_type', '')),
                lambda item: len(str(item.get('description', ''))) > 50,  # 描述較詳細
                lambda item: item.get('rating') is not None,  # 有評分
            ],
            "most_complete": [
                lambda item: len(str(item.get('description', ''))) > 50,
                lambda item: item.get('rating') is not None,
                lambda item: item.get('amenities') is not None,
                lambda item: item.get('phone') is not None,
            ]
        }
        
        rules = priority_rules.get(priority_source, priority_rules["most_complete"])
        
        # 根據規則評分
        best_item = duplicates[0]
        best_score = 0
        
        for item in duplicates:
            score = 0
            for rule in rules:
                try:
                    if rule(item):
                        score += 1
                except:
                    continue
            
            if score > best_score:
                best_score = score
                best_item = item
        
        return best_item
    
    def get_duplicate_report(self, duplicate_groups: Dict[str, List[Dict]]) -> str:
        """生成重複報告"""
        report = []
        report.append("=== 重複項目報告 ===")
        report.append(f"發現 {len(duplicate_groups)} 個重複組")
        report.append("")
        
        for group_key, duplicates in duplicate_groups.items():
            report.append(f"重複組: {group_key}")
            for i, item in enumerate(duplicates):
                name = item.get('name', '') or item.get('中文名稱', '')
                address = item.get('address', '') or item.get('地址', '')
                source = item.get('source', 'Unknown')
                report.append(f"  {i+1}. {name} ({address}) - 來源: {source}")
            report.append("")
        
        return "\n".join(report)
