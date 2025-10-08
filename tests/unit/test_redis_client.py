"""
測試 redis_client.py
"""

import pytest
from unittest.mock import Mock, patch
import json
import os
import redis

from src.itinerary_planner.infrastructure.clients.redis_client import RedisClient, redis_client


class TestRedisClient:
    """測試 Redis 客戶端"""

    def test_redis_client_initialization_success(self):
        """測試 Redis 客戶端成功初始化"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient("redis://localhost:6379")
            
            # 驗證初始化
            assert client.client == mock_client
            mock_redis.from_url.assert_called_once_with("redis://localhost:6379", decode_responses=True)
            mock_client.ping.assert_called_once()

    def test_redis_client_initialization_connection_error(self):
        """測試 Redis 客戶端連接錯誤"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 拋出連接錯誤
            mock_redis.from_url.side_effect = Exception("Connection refused")
            
            # 創建客戶端實例
            client = RedisClient("redis://invalid:6379")
            
            # 驗證初始化失敗
            assert client.client is None

    def test_redis_client_initialization_default_url(self):
        """測試 Redis 客戶端使用預設 URL"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例（不指定 URL）
            client = RedisClient()
            
            # 驗證使用預設 URL
            mock_redis.from_url.assert_called_once_with("redis://localhost:6379", decode_responses=True)

    def test_get_success(self):
        """測試成功獲取值"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = '{"key": "value"}'
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            result = client.get("test_key")
            
            # 驗證結果
            assert result == {"key": "value"}
            mock_client.get.assert_called_once_with("test_key")

    def test_get_key_not_found(self):
        """測試獲取不存在的鍵"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            result = client.get("nonexistent_key")
            
            # 驗證結果
            assert result is None
            mock_client.get.assert_called_once_with("nonexistent_key")

    def test_get_no_client(self):
        """測試沒有客戶端連接時獲取值"""
        # 創建沒有客戶端的實例
        client = RedisClient("redis://invalid:6379")
        
        # 執行測試
        result = client.get("test_key")
        
        # 驗證結果
        assert result is None

    def test_set_success(self):
        """測試成功設定值"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            test_data = {"name": "台北101", "rating": 4.5}
            client.set("place_1", test_data, ttl=1800)
            
            # 驗證結果
            mock_client.set.assert_called_once_with("place_1", json.dumps(test_data), ex=1800)

    def test_set_default_ttl(self):
        """測試使用預設 TTL 設定值"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            test_data = {"name": "西門町"}
            client.set("place_2", test_data)
            
            # 驗證結果（預設 TTL 為 3600 秒）
            mock_client.set.assert_called_once_with("place_2", json.dumps(test_data), ex=3600)

    def test_set_no_client(self):
        """測試沒有客戶端連接時設定值"""
        # 創建沒有客戶端的實例
        client = RedisClient("redis://invalid:6379")
        
        # 執行測試
        test_data = {"name": "故宮博物院"}
        client.set("place_3", test_data)
        
        # 驗證結果（不應該拋出異常）

    def test_set_complex_data(self):
        """測試設定複雜資料結構"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            complex_data = {
                "places": [
                    {"id": 1, "name": "台北101", "categories": ["觀光景點", "建築"]},
                    {"id": 2, "name": "西門町", "categories": ["購物", "美食"]}
                ],
                "metadata": {
                    "total": 2,
                    "last_updated": "2024-01-15T10:00:00Z"
                }
            }
            client.set("places_cache", complex_data, ttl=7200)
            
            # 驗證結果
            mock_client.set.assert_called_once_with("places_cache", json.dumps(complex_data), ex=7200)

    def test_get_complex_data(self):
        """測試獲取複雜資料結構"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            complex_json = '{"places": [{"id": 1, "name": "台北101"}], "total": 1}'
            mock_client.get.return_value = complex_json
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            result = client.get("places_cache")
            
            # 驗證結果
            expected = {"places": [{"id": 1, "name": "台北101"}], "total": 1}
            assert result == expected

    def test_set_string_value(self):
        """測試設定字串值"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            client.set("simple_key", "simple_value", ttl=60)
            
            # 驗證結果
            mock_client.set.assert_called_once_with("simple_key", '"simple_value"', ex=60)

    def test_set_numeric_value(self):
        """測試設定數值"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 執行測試
            client.set("rating", 4.5, ttl=300)
            
            # 驗證結果
            mock_client.set.assert_called_once_with("rating", "4.5", ex=300)

    def test_singleton_instance(self):
        """測試單例實例"""
        # 驗證單例實例存在
        assert redis_client is not None
        assert isinstance(redis_client, RedisClient)

    def test_environment_variable_usage(self):
        """測試環境變數的使用"""
        with patch('src.itinerary_planner.infrastructure.clients.redis_client.redis') as mock_redis:
            # 設定 Mock 返回值
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.from_url.return_value = mock_client
            
            # 創建客戶端實例
            client = RedisClient()
            
            # 驗證使用預設 URL（因為 REDIS_URL 在模組級別定義）
            mock_redis.from_url.assert_called_once_with("redis://localhost:6379", decode_responses=True)
