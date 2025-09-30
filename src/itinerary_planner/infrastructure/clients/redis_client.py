import redis
import os
import json
from typing import Optional, Any

# 從環境變數讀取 Redis 連線 URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class RedisClient:
    """一個簡單的 Redis 客戶端，用於快取"""

    def __init__(self, connection_url: str = REDIS_URL):
        try:
            self.client = redis.from_url(connection_url, decode_responses=True)
            self.client.ping()
            print("Successfully connected to Redis.")
        except redis.exceptions.ConnectionError as e:
            print(f"Could not connect to Redis: {e}")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """從快取中獲取一個鍵的值"""
        if not self.client:
            return None
        
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        在快取中設定一個鍵值對，並指定 TTL (秒)。
        值會被序列化為 JSON。
        """
        if not self.client:
            return
        
        self.client.set(key, json.dumps(value), ex=ttl)

# 建立一個單例供應用程式使用
redis_client = RedisClient()
