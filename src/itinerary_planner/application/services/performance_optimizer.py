from typing import Dict, List, Optional, Any, Union, Callable
import logging
import json
import asyncio
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass, field
import redis
from sqlalchemy.orm import Session
from sqlalchemy import text
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """快取條目"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class PerformanceMetrics:
    """性能指標"""
    operation_name: str
    execution_time: float
    cache_hit: bool = False
    memory_usage: Optional[int] = None
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceOptimizer:
    """性能優化器"""
    
    def __init__(self, db_session: Session, redis_client: Optional[redis.Redis] = None):
        self.db = db_session
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=1)
        
        # 內存快取（LRU策略）
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.max_memory_cache_size = 1000
        
        # 性能指標收集
        self.metrics: List[PerformanceMetrics] = []
        self.max_metrics_history = 1000
        
        # 快取配置
        self.cache_config = {
            "conversation_context": {"ttl": 3600, "max_size": 500},  # 1小時
            "itinerary_planning": {"ttl": 1800, "max_size": 200},   # 30分鐘
            "place_search": {"ttl": 7200, "max_size": 1000},        # 2小時
            "user_preferences": {"ttl": 86400, "max_size": 100},    # 24小時
            "llm_responses": {"ttl": 3600, "max_size": 300},        # 1小時
        }
        
        # 異步處理配置
        self.async_config = {
            "max_concurrent_requests": 10,
            "request_timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 1
        }
    
    def cache_result(
        self, 
        cache_type: str, 
        key: str, 
        value: Any, 
        tags: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ):
        """快取結果"""
        
        try:
            # 獲取快取配置
            config = self.cache_config.get(cache_type, {"ttl": 3600, "max_size": 100})
            cache_ttl = ttl or config["ttl"]
            
            # 創建快取條目
            cache_entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=cache_ttl),
                tags=tags or []
            )
            
            # 存儲到Redis
            redis_key = f"{cache_type}:{key}"
            self.redis_client.setex(
                redis_key,
                cache_ttl,
                json.dumps(value, default=str, ensure_ascii=False)
            )
            
            # 存儲到內存快取
            self._store_in_memory_cache(redis_key, cache_entry)
            
            logger.debug(f"Cached result for {redis_key}")
            
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def get_cached_result(
        self, 
        cache_type: str, 
        key: str
    ) -> Optional[Any]:
        """獲取快取的結果"""
        
        try:
            redis_key = f"{cache_type}:{key}"
            
            # 先檢查內存快取
            if redis_key in self.memory_cache:
                entry = self.memory_cache[redis_key]
                if entry.expires_at > datetime.now():
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    logger.debug(f"Memory cache hit for {redis_key}")
                    return entry.value
                else:
                    # 過期，移除
                    del self.memory_cache[redis_key]
            
            # 檢查Redis快取
            cached_data = self.redis_client.get(redis_key)
            if cached_data:
                value = json.loads(cached_data)
                
                # 存儲到內存快取
                cache_entry = CacheEntry(
                    key=redis_key,
                    value=value,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(seconds=3600),  # 默認1小時
                    access_count=1,
                    last_accessed=datetime.now()
                )
                self._store_in_memory_cache(redis_key, cache_entry)
                
                logger.debug(f"Redis cache hit for {redis_key}")
                return value
            
            logger.debug(f"Cache miss for {redis_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached result: {e}")
            return None
    
    def _store_in_memory_cache(self, key: str, entry: CacheEntry):
        """存儲到內存快取（LRU策略）"""
        
        # 如果快取已滿，移除最舊的條目
        if len(self.memory_cache) >= self.max_memory_cache_size:
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].last_accessed or self.memory_cache[k].created_at
            )
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = entry
    
    def invalidate_cache(self, cache_type: str, key: Optional[str] = None, tags: Optional[List[str]] = None):
        """使快取失效"""
        
        try:
            if key:
                # 使特定鍵失效
                redis_key = f"{cache_type}:{key}"
                self.redis_client.delete(redis_key)
                if redis_key in self.memory_cache:
                    del self.memory_cache[redis_key]
            
            elif tags:
                # 根據標籤使快取失效
                pattern = f"{cache_type}:*"
                for redis_key in self.redis_client.scan_iter(match=pattern):
                    # 這裡需要額外的邏輯來檢查標籤，簡化處理
                    self.redis_client.delete(redis_key)
            
            else:
                # 使整個類型的快取失效
                pattern = f"{cache_type}:*"
                for redis_key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(redis_key)
            
            # 清理內存快取
            keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{cache_type}:")]
            for key_to_remove in keys_to_remove:
                del self.memory_cache[key_to_remove]
            
            logger.debug(f"Invalidated cache for {cache_type}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    def measure_performance(self, operation_name: str):
        """性能測量裝飾器"""
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                cache_hit = False
                error_count = 0
                
                try:
                    # 嘗試從快取獲取結果
                    cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                    cached_result = self.get_cached_result("function_cache", cache_key)
                    
                    if cached_result is not None:
                        cache_hit = True
                        return cached_result
                    
                    # 執行函數
                    result = await func(*args, **kwargs)
                    
                    # 快取結果
                    self.cache_result("function_cache", cache_key, result)
                    
                    return result
                    
                except Exception as e:
                    error_count = 1
                    logger.error(f"Error in {operation_name}: {e}")
                    raise
                
                finally:
                    # 記錄性能指標
                    execution_time = time.time() - start_time
                    metrics = PerformanceMetrics(
                        operation_name=operation_name,
                        execution_time=execution_time,
                        cache_hit=cache_hit,
                        error_count=error_count
                    )
                    self._record_metrics(metrics)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                cache_hit = False
                error_count = 0
                
                try:
                    # 嘗試從快取獲取結果
                    cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                    cached_result = self.get_cached_result("function_cache", cache_key)
                    
                    if cached_result is not None:
                        cache_hit = True
                        return cached_result
                    
                    # 執行函數
                    result = func(*args, **kwargs)
                    
                    # 快取結果
                    self.cache_result("function_cache", cache_key, result)
                    
                    return result
                    
                except Exception as e:
                    error_count = 1
                    logger.error(f"Error in {operation_name}: {e}")
                    raise
                
                finally:
                    # 記錄性能指標
                    execution_time = time.time() - start_time
                    metrics = PerformanceMetrics(
                        operation_name=operation_name,
                        execution_time=execution_time,
                        cache_hit=cache_hit,
                        error_count=error_count
                    )
                    self._record_metrics(metrics)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成快取鍵"""
        
        # 將參數序列化為字符串
        key_data = {
            "func_name": func_name,
            "args": args,
            "kwargs": kwargs
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        
        # 生成哈希
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _record_metrics(self, metrics: PerformanceMetrics):
        """記錄性能指標"""
        
        self.metrics.append(metrics)
        
        # 保持指標歷史在限制範圍內
        if len(self.metrics) > self.max_metrics_history:
            self.metrics = self.metrics[-self.max_metrics_history:]
    
    async def batch_process(
        self, 
        items: List[Any], 
        process_func: Callable, 
        batch_size: int = 10,
        max_concurrent: Optional[int] = None
    ) -> List[Any]:
        """批量處理"""
        
        max_concurrent = max_concurrent or self.async_config["max_concurrent_requests"]
        results = []
        
        # 分批處理
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # 創建信號量限制並發
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(item):
                async with semaphore:
                    try:
                        return await process_func(item)
                    except Exception as e:
                        logger.error(f"Error processing item {item}: {e}")
                        return None
            
            # 並行處理批次
            batch_results = await asyncio.gather(
                *[process_with_semaphore(item) for item in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
        
        return results
    
    async def retry_with_backoff(
        self, 
        func: Callable, 
        *args, 
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
        backoff_factor: float = 2.0,
        **kwargs
    ) -> Any:
        """帶退避的重試機制"""
        
        max_retries = max_retries or self.async_config["retry_attempts"]
        delay = delay or self.async_config["retry_delay"]
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
        
        raise last_exception
    
    def optimize_database_query(self, query: str, params: Optional[Dict] = None) -> str:
        """優化數據庫查詢"""
        
        try:
            # 添加查詢提示
            optimized_query = query
            
            # 如果是SELECT查詢，添加LIMIT如果沒有
            if query.strip().upper().startswith('SELECT') and 'LIMIT' not in query.upper():
                if 'ORDER BY' in query.upper():
                    optimized_query += ' LIMIT 1000'
                else:
                    optimized_query += ' LIMIT 100'
            
            # 添加查詢快取提示
            if 'SELECT' in query.upper() and 'CACHE' not in query.upper():
                optimized_query = f"/*+ RESULT_CACHE */ {optimized_query}"
            
            return optimized_query
            
        except Exception as e:
            logger.error(f"Error optimizing query: {e}")
            return query
    
    async def execute_query_with_cache(
        self, 
        query: str, 
        params: Optional[Dict] = None,
        cache_ttl: int = 300
    ) -> List[Dict]:
        """執行帶快取的查詢"""
        
        # 生成快取鍵
        cache_key = hashlib.md5(f"{query}:{json.dumps(params or {}, sort_keys=True)}".encode()).hexdigest()
        
        # 嘗試從快取獲取
        cached_result = self.get_cached_result("db_query", cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # 優化查詢
            optimized_query = self.optimize_database_query(query, params)
            
            # 執行查詢
            result = self.db.execute(text(optimized_query), params or {})
            
            # 轉換結果
            rows = []
            for row in result:
                rows.append(dict(row._mapping))
            
            # 快取結果
            self.cache_result("db_query", cache_key, rows, ttl=cache_ttl)
            
            return rows
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def get_performance_report(self) -> Dict[str, Any]:
        """獲取性能報告"""
        
        if not self.metrics:
            return {"message": "No performance data available"}
        
        # 按操作名稱分組
        operation_stats = {}
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in operation_stats:
                operation_stats[op_name] = {
                    "total_calls": 0,
                    "total_time": 0.0,
                    "cache_hits": 0,
                    "errors": 0,
                    "avg_time": 0.0,
                    "cache_hit_rate": 0.0
                }
            
            stats = operation_stats[op_name]
            stats["total_calls"] += 1
            stats["total_time"] += metric.execution_time
            if metric.cache_hit:
                stats["cache_hits"] += 1
            stats["errors"] += metric.error_count
        
        # 計算平均值
        for op_name, stats in operation_stats.items():
            if stats["total_calls"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["total_calls"]
                stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_calls"]
        
        # 整體統計
        total_metrics = len(self.metrics)
        total_time = sum(m.execution_time for m in self.metrics)
        total_cache_hits = sum(1 for m in self.metrics if m.cache_hit)
        total_errors = sum(m.error_count for m in self.metrics)
        
        return {
            "summary": {
                "total_operations": total_metrics,
                "total_execution_time": total_time,
                "average_execution_time": total_time / total_metrics if total_metrics > 0 else 0,
                "overall_cache_hit_rate": total_cache_hits / total_metrics if total_metrics > 0 else 0,
                "total_errors": total_errors,
                "error_rate": total_errors / total_metrics if total_metrics > 0 else 0
            },
            "operation_stats": operation_stats,
            "cache_stats": {
                "memory_cache_size": len(self.memory_cache),
                "max_memory_cache_size": self.max_memory_cache_size,
                "cache_config": self.cache_config
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def cleanup_expired_cache(self):
        """清理過期的快取"""
        
        try:
            # 清理內存快取
            expired_keys = []
            for key, entry in self.memory_cache.items():
                if entry.expires_at <= datetime.now():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            logger.info(f"Cleaned up {len(expired_keys)} expired memory cache entries")
            
            # Redis快取會自動過期，但我們可以主動清理
            for cache_type in self.cache_config.keys():
                pattern = f"{cache_type}:*"
                expired_count = 0
                for key in self.redis_client.scan_iter(match=pattern):
                    ttl = self.redis_client.ttl(key)
                    if ttl == -1:  # 沒有過期時間的鍵
                        expired_count += 1
                        self.redis_client.delete(key)
                
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired Redis cache entries for {cache_type}")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
    
    def optimize_memory_usage(self):
        """優化內存使用"""
        
        try:
            # 清理內存快取
            self.cleanup_expired_cache()
            
            # 如果內存快取仍然太大，移除最少使用的條目
            if len(self.memory_cache) > self.max_memory_cache_size * 0.8:
                # 按最後訪問時間排序，移除最舊的20%
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].last_accessed or x[1].created_at
                )
                
                remove_count = int(len(sorted_entries) * 0.2)
                for i in range(remove_count):
                    key, _ = sorted_entries[i]
                    del self.memory_cache[key]
                
                logger.info(f"Removed {remove_count} least used cache entries")
            
            # 限制性能指標歷史
            if len(self.metrics) > self.max_metrics_history:
                self.metrics = self.metrics[-self.max_metrics_history:]
                logger.info(f"Truncated metrics history to {self.max_metrics_history} entries")
            
        except Exception as e:
            logger.error(f"Error optimizing memory usage: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {}
        }
        
        # 檢查Redis連接
        try:
            self.redis_client.ping()
            health_status["components"]["redis"] = {"status": "healthy", "response_time": 0}
        except Exception as e:
            health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # 檢查數據庫連接
        try:
            start_time = time.time()
            self.db.execute(text("SELECT 1"))
            response_time = time.time() - start_time
            health_status["components"]["database"] = {"status": "healthy", "response_time": response_time}
        except Exception as e:
            health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # 檢查內存使用
        memory_usage = len(self.memory_cache)
        health_status["components"]["memory_cache"] = {
            "status": "healthy" if memory_usage < self.max_memory_cache_size else "warning",
            "usage": memory_usage,
            "max_size": self.max_memory_cache_size,
            "usage_percentage": (memory_usage / self.max_memory_cache_size) * 100
        }
        
        return health_status
