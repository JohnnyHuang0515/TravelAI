import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.itinerary_planner.application.services.performance_optimizer import (
    PerformanceOptimizer,
    CacheEntry,
    PerformanceMetrics
)


class TestPerformanceOptimizer:
    """性能優化器測試"""
    
    @pytest.fixture
    def mock_db_session(self):
        """模擬數據庫會話"""
        return Mock()
    
    @pytest.fixture
    def mock_redis_client(self):
        """模擬Redis客戶端"""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = iter([])
        mock_redis.ping.return_value = True
        mock_redis.ttl.return_value = 3600
        return mock_redis
    
    @pytest.fixture
    def optimizer(self, mock_db_session, mock_redis_client):
        """創建測試用的性能優化器實例"""
        with patch('src.itinerary_planner.application.services.performance_optimizer.redis.Redis', return_value=mock_redis_client):
            optimizer = PerformanceOptimizer(mock_db_session, mock_redis_client)
            return optimizer
    
    def test_cache_result_and_get(self, optimizer, mock_redis_client):
        """測試快取結果和獲取"""
        cache_key = "test_key"
        cache_value = {"test": "data"}
        
        # 測試快取結果
        optimizer.cache_result("test_type", cache_key, cache_value)
        
        # 驗證Redis存儲被調用
        mock_redis_client.setex.assert_called_once()
        
        # 測試獲取快取結果
        mock_redis_client.get.return_value = json.dumps(cache_value)
        result = optimizer.get_cached_result("test_type", cache_key)
        
        assert result == cache_value
        mock_redis_client.get.assert_called_with(f"test_type:{cache_key}")
    
    def test_cache_miss(self, optimizer, mock_redis_client):
        """測試快取未命中"""
        mock_redis_client.get.return_value = None
        
        result = optimizer.get_cached_result("test_type", "nonexistent_key")
        
        assert result is None
    
    def test_memory_cache_lru(self, optimizer):
        """測試內存快取LRU策略"""
        # 填滿快取
        for i in range(optimizer.max_memory_cache_size + 10):
            entry = CacheEntry(
                key=f"key_{i}",
                value=f"value_{i}",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1)
            )
            optimizer._store_in_memory_cache(f"key_{i}", entry)
        
        # 驗證快取大小不超過限制
        assert len(optimizer.memory_cache) <= optimizer.max_memory_cache_size
    
    def test_invalidate_cache(self, optimizer, mock_redis_client):
        """測試快取失效"""
        cache_type = "test_type"
        cache_key = "test_key"
        
        # 使特定鍵失效
        optimizer.invalidate_cache(cache_type, cache_key)
        mock_redis_client.delete.assert_called_with(f"{cache_type}:{cache_key}")
        
        # 使整個類型失效
        optimizer.invalidate_cache(cache_type)
        mock_redis_client.scan_iter.assert_called()
    
    @pytest.mark.asyncio
    async def test_measure_performance_decorator(self, optimizer, mock_redis_client):
        """測試性能測量裝飾器"""
        @optimizer.measure_performance("test_operation")
        async def test_function():
            await asyncio.sleep(0.01)  # 模擬一些工作
            return "test_result"
        
        # 模擬快取未命中
        mock_redis_client.get.return_value = None
        
        result = await test_function()
        
        assert result == "test_result"
        assert len(optimizer.metrics) == 1
        
        metric = optimizer.metrics[0]
        assert metric.operation_name == "test_operation"
        assert metric.execution_time > 0
        assert not metric.cache_hit
        assert metric.error_count == 0
    
    @pytest.mark.asyncio
    async def test_measure_performance_with_cache(self, optimizer, mock_redis_client):
        """測試帶快取的性能測量"""
        @optimizer.measure_performance("test_operation")
        async def test_function():
            return "test_result"
        
        # 第一次調用（快取未命中）
        mock_redis_client.get.return_value = None
        result1 = await test_function()
        
        # 第二次調用（快取命中）
        mock_redis_client.get.return_value = json.dumps("test_result")
        result2 = await test_function()
        
        assert result1 == result2 == "test_result"
        assert len(optimizer.metrics) == 2
        
        # 檢查第二次調用是否命中快取
        cache_hit_metric = optimizer.metrics[1]
        assert cache_hit_metric.cache_hit == True
    
    @pytest.mark.asyncio
    async def test_batch_process(self, optimizer):
        """測試批量處理"""
        items = list(range(10))
        
        async def process_item(item):
            await asyncio.sleep(0.001)
            return item * 2
        
        results = await optimizer.batch_process(items, process_item, batch_size=3, max_concurrent=2)
        
        assert len(results) == 10
        assert all(result == i * 2 for i, result in enumerate(results))
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff(self, optimizer):
        """測試重試機制"""
        call_count = 0
        
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await optimizer.retry_with_backoff(failing_function, max_retries=3)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_max_retries(self, optimizer):
        """測試重試機制達到最大重試次數"""
        async def always_failing_function():
            raise Exception("Permanent failure")
        
        with pytest.raises(Exception, match="Permanent failure"):
            await optimizer.retry_with_backoff(always_failing_function, max_retries=2)
    
    def test_optimize_database_query(self, optimizer):
        """測試數據庫查詢優化"""
        query = "SELECT * FROM users WHERE active = true"
        optimized_query = optimizer.optimize_database_query(query)
        
        assert "LIMIT" in optimized_query
        assert "RESULT_CACHE" in optimized_query
    
    @pytest.mark.asyncio
    async def test_execute_query_with_cache(self, optimizer, mock_db_session, mock_redis_client):
        """測試帶快取的查詢執行"""
        query = "SELECT * FROM test_table"
        params = {"id": 1}
        
        # 模擬數據庫結果
        mock_row = Mock()
        mock_row._mapping = {"id": 1, "name": "test"}
        mock_result = Mock()
        mock_result.__iter__ = Mock(return_value=iter([mock_row]))
        mock_db_session.execute.return_value = mock_result
        
        # 第一次調用（快取未命中）
        mock_redis_client.get.return_value = None
        results = await optimizer.execute_query_with_cache(query, params)
        
        assert len(results) == 1
        assert results[0]["id"] == 1
        assert results[0]["name"] == "test"
        
        # 驗證快取被設置
        mock_redis_client.setex.assert_called()
        
        # 第二次調用（快取命中）
        cached_result = [{"id": 1, "name": "test"}]
        mock_redis_client.get.return_value = json.dumps(cached_result)
        results = await optimizer.execute_query_with_cache(query, params)
        
        assert results == cached_result
        # 數據庫不應該被調用
        assert mock_db_session.execute.call_count == 1
    
    def test_get_performance_report(self, optimizer):
        """測試獲取性能報告"""
        # 添加一些測試指標
        optimizer.metrics = [
            PerformanceMetrics("operation1", 1.0, cache_hit=False),
            PerformanceMetrics("operation1", 0.5, cache_hit=True),
            PerformanceMetrics("operation2", 2.0, cache_hit=False),
        ]
        
        report = optimizer.get_performance_report()
        
        assert "summary" in report
        assert "operation_stats" in report
        assert "cache_stats" in report
        
        summary = report["summary"]
        assert summary["total_operations"] == 3
        assert summary["overall_cache_hit_rate"] == 1/3
        
        operation_stats = report["operation_stats"]
        assert "operation1" in operation_stats
        assert "operation2" in operation_stats
        assert operation_stats["operation1"]["total_calls"] == 2
        assert operation_stats["operation1"]["cache_hits"] == 1
    
    def test_cleanup_expired_cache(self, optimizer):
        """測試清理過期快取"""
        # 添加一些過期和未過期的快取條目
        now = datetime.now()
        expired_entry = CacheEntry(
            key="expired",
            value="data",
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1)
        )
        valid_entry = CacheEntry(
            key="valid",
            value="data",
            created_at=now,
            expires_at=now + timedelta(hours=1)
        )
        
        optimizer.memory_cache = {
            "expired": expired_entry,
            "valid": valid_entry
        }
        
        optimizer.cleanup_expired_cache()
        
        assert "expired" not in optimizer.memory_cache
        assert "valid" in optimizer.memory_cache
    
    def test_optimize_memory_usage(self, optimizer):
        """測試內存使用優化"""
        # 填滿快取
        for i in range(optimizer.max_memory_cache_size + 20):
            entry = CacheEntry(
                key=f"key_{i}",
                value=f"value_{i}",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1)
            )
            optimizer.memory_cache[f"key_{i}"] = entry
        
        # 添加大量指標
        for i in range(optimizer.max_metrics_history + 100):
            optimizer.metrics.append(PerformanceMetrics(f"operation_{i}", 1.0))
        
        optimizer.optimize_memory_usage()
        
        assert len(optimizer.memory_cache) <= optimizer.max_memory_cache_size
        assert len(optimizer.metrics) <= optimizer.max_metrics_history
    
    @pytest.mark.asyncio
    async def test_health_check(self, optimizer, mock_redis_client, mock_db_session):
        """測試健康檢查"""
        # 模擬數據庫執行
        mock_db_session.execute.return_value = Mock()
        
        health_status = await optimizer.health_check()
        
        assert "timestamp" in health_status
        assert "status" in health_status
        assert "components" in health_status
        
        components = health_status["components"]
        assert "redis" in components
        assert "database" in components
        assert "memory_cache" in components
    
    def test_generate_cache_key(self, optimizer):
        """測試生成快取鍵"""
        key1 = optimizer._generate_cache_key("func", ("arg1", "arg2"), {"kwarg": "value"})
        key2 = optimizer._generate_cache_key("func", ("arg1", "arg2"), {"kwarg": "value"})
        
        # 相同參數應該生成相同的鍵
        assert key1 == key2
        
        # 不同參數應該生成不同的鍵
        key3 = optimizer._generate_cache_key("func", ("arg1", "arg3"), {"kwarg": "value"})
        assert key1 != key3


class TestCacheEntry:
    """快取條目測試"""
    
    def test_cache_entry_creation(self):
        """測試快取條目創建"""
        now = datetime.now()
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            access_count=5,
            last_accessed=now,
            tags=["tag1", "tag2"]
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.access_count == 5
        assert entry.tags == ["tag1", "tag2"]


class TestPerformanceMetrics:
    """性能指標測試"""
    
    def test_performance_metrics_creation(self):
        """測試性能指標創建"""
        now = datetime.now()
        metric = PerformanceMetrics(
            operation_name="test_operation",
            execution_time=1.5,
            cache_hit=True,
            memory_usage=1024,
            error_count=0,
            timestamp=now
        )
        
        assert metric.operation_name == "test_operation"
        assert metric.execution_time == 1.5
        assert metric.cache_hit == True
        assert metric.memory_usage == 1024
        assert metric.error_count == 0
        assert metric.timestamp == now


if __name__ == "__main__":
    pytest.main([__file__])

