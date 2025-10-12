"""
統一的資料處理管道
在資料匯入時就完成所有處理：地址解析、語境增強、embedding 生成
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProcessedData:
    """處理後的資料結構"""
    # 基本資訊
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    
    # 分類和類型
    categories: Optional[List[str]] = None
    type: Optional[str] = None
    
    # 地理位置
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    parsed_address: Optional[Dict[str, Any]] = None
    
    # 評分和價格
    rating: Optional[float] = None
    price_range: Optional[int] = None
    
    # 時間相關
    stay_minutes: Optional[int] = None
    
    # 設施和服務
    amenities: Optional[List[str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    
    # 語境資訊
    context_metadata: Optional[Dict[str, Any]] = None
    
    # 向量嵌入
    embedding: Optional[List[float]] = None
    
    # 原始資料
    raw_data: Optional[Dict[str, Any]] = None
    
    # 品質標記
    premium_markers: Optional[Dict[str, Any]] = None

class DataProcessor(ABC):
    """資料處理器基類"""
    
    @abstractmethod
    def process(self, raw_data: Dict[str, Any]) -> ProcessedData:
        """處理原始資料"""
        pass

class AddressParser:
    """地址解析器"""
    
    def __init__(self):
        # 台灣各縣市的詳細座標資料
        self.taiwan_districts = {
            "宜蘭縣": {
                "宜蘭市": (24.7580, 121.7530),
                "羅東鎮": (24.6770, 121.7730),
                "蘇澳鎮": (24.5960, 121.8420),
                "頭城鎮": (24.8570, 121.8230),
                "礁溪鄉": (24.8270, 121.7730),
                "壯圍鄉": (24.7470, 121.7930),
                "員山鄉": (24.7470, 121.7230),
                "冬山鄉": (24.6370, 121.7930),
                "五結鄉": (24.6870, 121.8030),
                "三星鄉": (24.6670, 121.6630),
                "大同鄉": (24.5270, 121.6030),
                "南澳鄉": (24.4670, 121.8030)
            },
            "台北市": {
                "中正區": (25.0320, 121.5180),
                "大同區": (25.0650, 121.5130),
                "中山區": (25.0630, 121.5260),
                "松山區": (25.0480, 121.5770),
                "大安區": (25.0270, 121.5440),
                "萬華區": (25.0360, 121.4990),
                "信義區": (25.0360, 121.5710),
                "士林區": (25.0880, 121.5240),
                "北投區": (25.1320, 121.4980),
                "內湖區": (25.0690, 121.5940),
                "南港區": (25.0550, 121.6070),
                "文山區": (25.0040, 121.5700)
            },
            "新北市": {
                "板橋區": (25.0060, 121.4620),
                "三重區": (25.0620, 121.4850),
                "中和區": (24.9940, 121.5080),
                "永和區": (25.0070, 121.5150),
                "新莊區": (25.0360, 121.4500),
                "新店區": (24.9580, 121.5410),
                "樹林區": (24.9900, 121.4250),
                "鶯歌區": (24.9550, 121.3550),
                "三峽區": (24.9350, 121.3690),
                "淡水區": (25.1670, 121.4450),
                "汐止區": (25.0690, 121.6560),
                "瑞芳區": (25.1080, 121.8050),
                "土城區": (24.9720, 121.4440),
                "蘆洲區": (25.0850, 121.4640),
                "五股區": (25.0830, 121.4390),
                "泰山區": (25.0610, 121.4300),
                "林口區": (25.0770, 121.3890),
                "深坑區": (25.0020, 121.6180),
                "石碇區": (24.9900, 121.6630),
                "坪林區": (24.9370, 121.7110),
                "三芝區": (25.2580, 121.5000),
                "石門區": (25.2920, 121.5670),
                "八里區": (25.1460, 121.3980),
                "平溪區": (25.0250, 121.7840),
                "雙溪區": (25.0380, 121.8650),
                "貢寮區": (25.0210, 121.9210),
                "金山區": (25.2210, 121.6340),
                "萬里區": (25.1790, 121.6890),
                "烏來區": (24.8630, 121.5510)
            }
            # 可以繼續添加其他縣市
        }
    
    def parse_address(self, address: str) -> Dict[str, Any]:
        """解析地址，提取結構化資訊"""
        if not address:
            return {}
        
        import re
        
        clean_address = address.strip()
        
        # 提取郵遞區號
        postal_code = re.search(r'(\d{3})', clean_address)
        postal_code = postal_code.group(1) if postal_code else None
        
        # 提取縣市和鄉鎮區
        county = None
        district = None
        
        for county_name, districts in self.taiwan_districts.items():
            if county_name in clean_address:
                county = county_name
                for district_name in districts.keys():
                    if district_name in clean_address:
                        district = district_name
                        break
                break
        
        # 提取路名
        road_patterns = [
            r'([^縣市鄉鎮區路街巷弄號]+路)',
            r'([^縣市鄉鎮區路街巷弄號]+街)',
            r'([^縣市鄉鎮區路街巷弄號]+巷)',
            r'([^縣市鄉鎮區路街巷弄號]+弄)'
        ]
        
        road_info = {}
        for pattern in road_patterns:
            match = re.search(pattern, clean_address)
            if match:
                road_type = pattern.replace(r'[^縣市鄉鎮區路街巷弄號]+', '').replace('(', '').replace(')', '')
                road_name = match.group(1).replace(road_type, '')
                road_info[road_type] = road_name
        
        # 提取門牌號碼
        house_number = re.search(r'(\d+[-]?\d*號)', clean_address)
        house_number = house_number.group(1) if house_number else None
        
        return {
            "postal_code": postal_code,
            "county": county,
            "district": district,
            "road_info": road_info,
            "house_number": house_number,
            "full_address": clean_address
        }
    
    def get_coordinates(self, parsed_address: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        """根據解析的地址獲取座標"""
        if not parsed_address:
            return None, None
        
        county = parsed_address.get("county")
        district = parsed_address.get("district")
        
        if not county or not district:
            return None, None
        
        if county in self.taiwan_districts and district in self.taiwan_districts[county]:
            return self.taiwan_districts[county][district]
        
        return None, None

class ContextEnhancer:
    """語境增強器"""
    
    def __init__(self):
        # 分類到語境的映射
        self.category_context_map = {
            # 餐廳相關
            "環保餐廳": {
                "activity_type": "用餐體驗",
                "visit_duration": "中等時間",
                "price_level": "中等",
                "activity_features": ["環保", "有機", "綠色", "健康", "美食"],
                "time_context": ["用餐時間", "全天", "健康飲食"],
                "location_context": ["餐廳", "美食", "環保理念"]
            },
            "甜點冰品": {
                "activity_type": "甜點品嚐",
                "visit_duration": "短時間",
                "price_level": "便宜",
                "activity_features": ["甜點", "冰品", "蛋糕", "冰淇淋", "甜品"],
                "time_context": ["下午茶", "甜點時間", "休閒"],
                "location_context": ["甜點店", "咖啡廳", "休閒"]
            },
            # 景點相關
            "溫泉類": {
                "activity_type": "溫泉體驗",
                "visit_duration": "長時間",
                "price_level": "較貴",
                "activity_features": ["溫泉", "泡湯", "溫泉浴", "SPA", "療癒"],
                "time_context": ["全天", "放鬆", "療癒"],
                "location_context": ["溫泉區", "泡湯", "療癒"]
            },
            "自然風景類": {
                "activity_type": "自然觀賞",
                "visit_duration": "長時間",
                "price_level": "免費",
                "activity_features": ["自然", "風景", "拍照", "戶外", "生態"],
                "time_context": ["白天", "戶外", "自然"],
                "location_context": ["自然景點", "風景區", "戶外"]
            },
            "文化類": {
                "activity_type": "文化學習",
                "visit_duration": "長時間",
                "price_level": "便宜",
                "activity_features": ["文化", "歷史", "教育", "學習", "展覽"],
                "time_context": ["白天", "學習", "文化"],
                "location_context": ["文化景點", "博物館", "歷史"]
            },
            "遊憩類": {
                "activity_type": "娛樂休閒",
                "visit_duration": "中等時間",
                "price_level": "中等",
                "activity_features": ["娛樂", "休閒", "觀光", "遊玩", "活動"],
                "time_context": ["全天", "娛樂", "休閒"],
                "location_context": ["遊樂景點", "休閒", "娛樂"]
            }
        }
        
        # 住宿類型映射
        self.accommodation_type_map = {
            "hotel": {
                "accommodation_type": "飯店",
                "service_level": "專業服務",
                "facilities": ["櫃台服務", "客房服務", "商務設施"],
                "price_level": "中高檔"
            },
            "homestay": {
                "accommodation_type": "民宿",
                "service_level": "親切服務",
                "facilities": ["家庭式", "溫馨", "個人化"],
                "price_level": "中檔"
            }
        }
    
    def enhance_place_context(self, processed_data: ProcessedData) -> Dict[str, Any]:
        """增強地點的語境資訊"""
        context = {}
        
        # 從分類推斷語境
        if processed_data.categories:
            for category in processed_data.categories:
                if category in self.category_context_map:
                    context.update(self.category_context_map[category])
                    break
        
        # 從停留時間推斷活動類型
        if processed_data.stay_minutes:
            if processed_data.stay_minutes <= 30:
                context["visit_duration"] = "短時間"
                context["activity_type"] = "快速參觀"
            elif processed_data.stay_minutes <= 90:
                context["visit_duration"] = "中等時間"
                context["activity_type"] = "一般參觀"
            elif processed_data.stay_minutes <= 180:
                context["visit_duration"] = "長時間"
                context["activity_type"] = "深度體驗"
            else:
                context["visit_duration"] = "全日"
                context["activity_type"] = "全天活動"
        
        # 從價格推斷消費等級
        if processed_data.price_range:
            if processed_data.price_range == 1:
                context["price_level"] = "免費"
                context["budget_friendly"] = "免費景點"
            elif processed_data.price_range == 2:
                context["price_level"] = "便宜"
                context["budget_friendly"] = "經濟實惠"
            elif processed_data.price_range == 3:
                context["price_level"] = "中等"
                context["budget_friendly"] = "中等價格"
            elif processed_data.price_range == 4:
                context["price_level"] = "較貴"
                context["budget_friendly"] = "高檔消費"
            else:
                context["price_level"] = "昂貴"
                context["budget_friendly"] = "奢華體驗"
        
        # 從評分推斷推薦程度
        if processed_data.rating:
            if processed_data.rating >= 4.5:
                context["recommendation"] = "強力推薦"
                context["popularity"] = "熱門景點"
            elif processed_data.rating >= 4.0:
                context["recommendation"] = "推薦"
                context["popularity"] = "受歡迎"
            elif processed_data.rating >= 3.5:
                context["recommendation"] = "一般"
                context["popularity"] = "普通"
            else:
                context["recommendation"] = "較少推薦"
                context["popularity"] = "冷門"
        
        # 從名稱推斷特殊時段
        name = processed_data.name.lower() if processed_data.name else ""
        if "夜市" in name:
            context["time_context"] = ["夜間", "晚上", "夜生活", "宵夜"]
        elif "公園" in name:
            context["time_context"] = ["白天", "戶外", "散步", "運動"]
        elif "博物館" in name or "館" in name:
            context["time_context"] = ["室內", "白天", "學習", "參觀"]
        elif "咖啡" in name:
            context["time_context"] = ["全天", "下午茶", "休閒", "聊天"]
        
        # 從地址推斷地區特色
        if processed_data.parsed_address:
            district = processed_data.parsed_address.get("district")
            if district:
                location_context = []
                if "礁溪" in district:
                    location_context.extend(["溫泉區", "泡湯", "療癒"])
                elif "羅東" in district:
                    location_context.extend(["市區", "美食", "夜市"])
                elif "頭城" in district:
                    location_context.extend(["海邊", "海岸", "海景"])
                elif "蘇澳" in district:
                    location_context.extend(["漁港", "海鮮", "海邊"])
                elif "五結" in district:
                    location_context.extend(["傳藝", "傳統藝術", "文化"])
                elif "三星" in district:
                    location_context.extend(["農業", "蔥", "田園"])
                elif "冬山" in district:
                    location_context.extend(["梅花湖", "自然", "風景"])
                elif "大同" in district:
                    location_context.extend(["太平山", "森林", "高山"])
                elif "南澳" in district:
                    location_context.extend(["東岳湧泉", "自然", "溫泉"])
                
                if location_context:
                    context["location_context"] = location_context
        
        return context
    
    def enhance_accommodation_context(self, processed_data: ProcessedData) -> Dict[str, Any]:
        """增強住宿的語境資訊"""
        context = {}
        
        # 從類型推斷特色
        if processed_data.type and processed_data.type in self.accommodation_type_map:
            context.update(self.accommodation_type_map[processed_data.type])
        
        # 從設施推斷特色
        if processed_data.amenities:
            amenity_features = []
            for amenity in processed_data.amenities:
                if "溫泉" in amenity or "SPA" in amenity:
                    amenity_features.extend(["溫泉", "SPA", "療癒", "放鬆"])
                elif "WiFi" in amenity:
                    amenity_features.extend(["網路", "WiFi", "現代", "便利"])
                elif "停車場" in amenity:
                    amenity_features.extend(["停車", "停車場", "自駕", "便利"])
                elif "早餐" in amenity:
                    amenity_features.extend(["早餐", "餐飲", "服務"])
                elif "廚房" in amenity:
                    amenity_features.extend(["廚房", "自助", "家庭式"])
                elif "洗衣機" in amenity:
                    amenity_features.extend(["洗衣", "洗衣機", "長期住宿", "便利"])
            
            if amenity_features:
                context["amenity_features"] = list(set(amenity_features))
        
        return context

class EmbeddingGenerator:
    """Embedding 生成器"""
    
    def __init__(self):
        from itinerary_planner.infrastructure.clients.embedding_client import EmbeddingClient
        self.embedding_client = EmbeddingClient()
        
        # 詳細分類描述
        self.category_descriptions = {
            "環保餐廳": "環保餐廳 有機料理 綠色餐飲 永續食材 健康飲食 生態友善 環保理念 綠色生活 有機蔬果 天然食材 無添加 環保餐具 環保包裝 綠色廚房 永續餐廳 生態餐廳 環保美食 綠色料理 有機餐廳 環保用餐",
            "溫泉類": "溫泉 泡湯 溫泉浴 溫泉SPA 溫泉療養 溫泉度假 溫泉養生 溫泉休閒 溫泉體驗 溫泉文化 溫泉旅遊 溫泉景點 溫泉區 溫泉村 溫泉館 溫泉會館 溫泉度假村 溫泉旅館 溫泉民宿 溫泉設施",
            "自然風景類": "自然風景 風景區 自然景觀 自然保護區 生態景點 自然步道 自然生態 自然環境 自然美景 自然景觀 自然風光 自然景點 自然旅遊 自然探索 自然體驗 自然觀察 自然攝影 自然教育 自然學習 自然保育",
            "文化類": "文化景點 文化遺產 文化歷史 文化古蹟 文化建築 文化藝術 文化體驗 文化學習 文化教育 文化導覽 文化旅遊 文化探索 文化發現 文化傳承 文化保存 文化復興 文化推廣 文化活動 文化節慶 文化展示",
            "遊憩類": "遊憩景點 休閒娛樂 遊樂設施 休閒活動 娛樂設施 遊憩體驗 休閒旅遊 娛樂活動 遊憩設施 休閒景點 娛樂景點 遊樂園 休閒中心 娛樂中心 遊憩中心 休閒場所 娛樂場所 遊憩場所 休閒設施 娛樂設施",
            "甜點冰品": "甜點 冰品 蛋糕 冰淇淋 甜品 甜食 甜點店 冰品店 蛋糕店 冰淇淋店 甜品店 甜食店 甜點製作 冰品製作 蛋糕製作 冰淇淋製作 甜品製作 甜食製作 甜點體驗 冰品體驗 蛋糕體驗 冰淇淋體驗 甜品體驗 甜食體驗"
        }
    
    def generate_place_embedding(self, processed_data: ProcessedData) -> List[float]:
        """為地點生成 embedding"""
        text_parts = []
        
        # 基本資訊
        if processed_data.name:
            text_parts.append(processed_data.name)
        
        if processed_data.description:
            text_parts.append(processed_data.description)
        
        # 分類描述
        if processed_data.categories:
            for category in processed_data.categories:
                if category in self.category_descriptions:
                    text_parts.append(self.category_descriptions[category])
        
        # 語境資訊
        if processed_data.context_metadata:
            for key, value in processed_data.context_metadata.items():
                if isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
                else:
                    text_parts.append(str(value))
        
        # 地址資訊
        if processed_data.parsed_address:
            parsed = processed_data.parsed_address
            if parsed.get("district"):
                text_parts.append(f"地區: {parsed['district']}")
            if parsed.get("county"):
                text_parts.append(f"縣市: {parsed['county']}")
        
        embedding_text = " ".join(text_parts)
        return self.embedding_client.get_embedding(embedding_text)
    
    def generate_accommodation_embedding(self, processed_data: ProcessedData) -> List[float]:
        """為住宿生成 embedding"""
        text_parts = []
        
        # 基本資訊
        if processed_data.name:
            text_parts.append(processed_data.name)
        
        # 類型描述
        if processed_data.type == "hotel":
            text_parts.append("飯店 酒店 旅館 住宿 專業服務 櫃台服務 客房服務 商務設施")
        elif processed_data.type == "homestay":
            text_parts.append("民宿 家庭式住宿 親切服務 溫馨住宿 個人化服務 家庭式")
        
        # 語境資訊
        if processed_data.context_metadata:
            for key, value in processed_data.context_metadata.items():
                if isinstance(value, list):
                    text_parts.extend([str(v) for v in value])
                else:
                    text_parts.append(str(value))
        
        # 設施特色
        if processed_data.amenities:
            for amenity in processed_data.amenities:
                if "溫泉" in amenity or "SPA" in amenity:
                    text_parts.extend(["溫泉", "SPA", "療癒", "放鬆"])
                elif "WiFi" in amenity:
                    text_parts.extend(["網路", "WiFi", "現代", "便利"])
                elif "停車場" in amenity:
                    text_parts.extend(["停車", "停車場", "自駕", "便利"])
        
        embedding_text = " ".join(text_parts)
        return self.embedding_client.get_embedding(embedding_text)

class DataProcessingPipeline:
    """統一的資料處理管道"""
    
    def __init__(self, enable_embeddings: bool = False):
        self.address_parser = AddressParser()
        self.context_enhancer = ContextEnhancer()
        # 暫時停用 embedding 功能
        self.enable_embeddings = enable_embeddings
        if enable_embeddings:
            self.embedding_generator = EmbeddingGenerator()
        else:
            self.embedding_generator = None
    
    def process_raw_data(self, raw_data: Dict[str, Any], data_type: str = "place", source_type: str = "default") -> ProcessedData:
        """處理原始資料"""
        try:
            # 1. 基本資料提取 - 支援多種資料格式
            if data_type == "place":
                # 地點資料的欄位映射
                name = (raw_data.get("name") or 
                       raw_data.get("中文名稱") or 
                       raw_data.get("名稱") or 
                       raw_data.get("org_name", ""))
                description = (raw_data.get("description") or 
                             raw_data.get("描述") or
                             raw_data.get("簡介"))
                address = (raw_data.get("address") or 
                         raw_data.get("地址") or 
                         raw_data.get("營業地址"))
                categories = raw_data.get("categories") or raw_data.get("分類")
                rating = raw_data.get("rating") or raw_data.get("評分")
                price_range = raw_data.get("price_range") or raw_data.get("價格區間")
                stay_minutes = raw_data.get("stay_minutes") or raw_data.get("建議停留時間")
                amenities = raw_data.get("amenities") or raw_data.get("設施")
                operating_hours = raw_data.get("operating_hours") or raw_data.get("營業時間")
                
                # 根據來源類型設定品質標記
                premium_markers = {}
                if source_type == "eco_hotel":
                    premium_markers["eco_certified"] = True
                    premium_markers["certification_type"] = "環保標章"
                elif source_type == "eco_restaurant":
                    premium_markers["eco_certified"] = True
                    premium_markers["certification_type"] = "環保餐廳"
                elif source_type == "education_facility":
                    premium_markers["education_certified"] = True
                    premium_markers["certification_type"] = "環境教育設施"
                    
            else:  # accommodation
                # 住宿資料的欄位映射
                name = (raw_data.get("name") or 
                       raw_data.get("中文名稱") or 
                       raw_data.get("名稱", ""))
                description = (raw_data.get("description") or 
                             raw_data.get("描述"))
                address = (raw_data.get("address") or 
                         raw_data.get("地址") or 
                         raw_data.get("營業地址"))
                type_value = raw_data.get("type") or raw_data.get("類型")
                rating = raw_data.get("rating") or raw_data.get("評分")
                price_range = raw_data.get("price_range") or raw_data.get("價格區間")
                amenities = raw_data.get("amenities") or raw_data.get("設施")
                
                # 根據資料來源推斷類型
                if not type_value:
                    if "旅館" in raw_data.get("旅館登記證核准編號", ""):
                        type_value = "hotel"
                    elif "民宿" in raw_data.get("民宿登記證核准編號", ""):
                        type_value = "homestay"
                    else:
                        type_value = "hotel"  # 預設為飯店
                
                # 根據來源類型設定品質標記
                premium_markers = {}
                if source_type == "eco_hotel":
                    premium_markers["eco_certified"] = True
                    premium_markers["certification_type"] = "環保標章"
            
            processed = ProcessedData(
                name=name,
                description=description,
                address=address,
                categories=raw_data.get("categories") if data_type == "place" else None,
                type=type_value if data_type == "accommodation" else None,
                rating=rating,
                price_range=price_range,
                stay_minutes=stay_minutes if data_type == "place" else None,
                amenities=amenities,
                operating_hours=operating_hours if data_type == "place" else None,
                raw_data=raw_data,
                premium_markers=premium_markers
            )
            
            # 2. 地址解析與座標處理
            # 優先使用原始資料中的座標
            if raw_data.get("latitude") and raw_data.get("longitude"):
                processed.latitude = float(raw_data.get("latitude"))
                processed.longitude = float(raw_data.get("longitude"))
            
            # 進行地址解析
            if processed.address:
                parsed_address = self.address_parser.parse_address(processed.address)
                processed.parsed_address = parsed_address
                
                # 如果沒有座標，嘗試從地址解析中獲取
                if not processed.latitude or not processed.longitude:
                    lat, lon = self.address_parser.get_coordinates(parsed_address)
                    processed.latitude = lat
                    processed.longitude = lon
            
            # 3. 語境增強
            if data_type == "place":
                context = self.context_enhancer.enhance_place_context(processed)
            else:  # accommodation
                context = self.context_enhancer.enhance_accommodation_context(processed)
            
            # 合併品質標記到語境 metadata
            if processed.premium_markers:
                if not context:
                    context = {}
                context.update(processed.premium_markers)
            
            processed.context_metadata = context
            
            # 4. 生成 embedding (暫時停用)
            if self.enable_embeddings and self.embedding_generator:
                if data_type == "place":
                    embedding = self.embedding_generator.generate_place_embedding(processed)
                else:  # accommodation
                    embedding = self.embedding_generator.generate_accommodation_embedding(processed)
                processed.embedding = embedding
            else:
                processed.embedding = None
            
            logger.info(f"成功處理 {data_type}: {processed.name}")
            return processed
            
        except Exception as e:
            logger.error(f"處理資料失敗: {e}")
            raise
    
    def batch_process(self, raw_data_list: List[Dict[str, Any]], data_type: str = "place", source_type: str = "default") -> List[ProcessedData]:
        """批次處理資料"""
        processed_list = []
        
        for i, raw_data in enumerate(raw_data_list):
            try:
                processed = self.process_raw_data(raw_data, data_type, source_type)
                processed_list.append(processed)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"已處理 {i + 1}/{len(raw_data_list)} 筆資料")
                    
            except Exception as e:
                logger.error(f"處理第 {i + 1} 筆資料失敗: {e}")
                continue
        
        logger.info(f"批次處理完成: {len(processed_list)}/{len(raw_data_list)} 筆成功")
        return processed_list
