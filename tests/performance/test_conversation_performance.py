import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, AsyncMock, patch
import json

from src.itinerary_planner.application.services.unified_conversation_engine import UnifiedConversationEngine
from src.itinerary_planner.application.services.performance_optimizer import PerformanceOptimizer


class TestConversationPerformance:
    """對話系統性能測試"""
    
    @pytest.fixture
    def mock_db_session(self):
        return Mock()
    
    @pytest.fixture
    def mock_redis_client(self):
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = iter([])
        mock_redis.ping.return_value = True
        return mock_redis
    
    @pytest.fixture
    def mock_llm_client(self):
        mock_client = Mock()
        mock_client.generate_response = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def performance_optimizer(self, mock_db_session, mock_redis_client):
        with patch('src.itinerary_planner.application.services.performance_optimizer.redis.Redis', return_value=mock_redis_client):
            return PerformanceOptimizer(mock_db_session, mock_redis_client)
    
    @pytest.fixture
    def conversation_engine(self, mock_db_session, mock_redis_client, mock_llm_client):
        with patch('src.itinerary_planner.application.services.unified_conversation_engine.GeminiLLMClient', return_value=mock_llm_client):
            with patch('src.itinerary_planner.application.services.unified_conversation_engine.redis.Redis', return_value=mock_redis_client):
                return UnifiedConversationEngine(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_single_message_performance(self, conversation_engine, mock_llm_client):
        """測試單一訊息處理性能"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "greeting",
            json.dumps({"destination": "台北", "duration": 3})
        ]
        
        # 測量處理時間
        start_time = time.time()
        
        result = await conversation_engine.process_message(
            session_id="perf_test_session",
            user_message="我想去台北旅遊3天"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert result is not None
        assert processing_time < 5.0  # 應該在5秒內完成
        print(f"Single message processing time: {processing_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_concurrent_message_performance(self, conversation_engine, mock_llm_client):
        """測試並發訊息處理性能"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "greeting", json.dumps({"destination": "台北"}),
            "greeting", json.dumps({"destination": "高雄"}),
            "greeting", json.dumps({"destination": "台南"}),
            "greeting", json.dumps({"destination": "台中"}),
            "greeting", json.dumps({"destination": "花蓮"})
        ] * 10  # 重複10次以支持50個請求
        
        # 準備並發請求
        messages = [
            f"我想去{location}旅遊" 
            for location in ["台北", "高雄", "台南", "台中", "花蓮"] * 10
        ]
        
        # 測量並發處理時間
        start_time = time.time()
        
        tasks = [
            conversation_engine.process_message(
                session_id=f"perf_test_session_{i}",
                user_message=message
            )
            for i, message in enumerate(messages)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 驗證結果
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(messages)
        
        avg_time_per_message = total_time / len(messages)
        print(f"Concurrent processing: {len(messages)} messages in {total_time:.3f}s")
        print(f"Average time per message: {avg_time_per_message:.3f}s")
        
        assert avg_time_per_message < 2.0  # 平均每個訊息應該在2秒內處理
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, performance_optimizer, mock_redis_client):
        """測試快取性能"""
        cache_key = "performance_test_key"
        cache_value = {"test": "data", "large_data": "x" * 1000}  # 較大的數據
        
        # 測試快取寫入性能
        write_times = []
        for i in range(100):
            start_time = time.time()
            performance_optimizer.cache_result("test_type", f"{cache_key}_{i}", cache_value)
            write_times.append(time.time() - start_time)
        
        avg_write_time = statistics.mean(write_times)
        print(f"Average cache write time: {avg_write_time:.6f}s")
        
        # 測試快取讀取性能
        mock_redis_client.get.return_value = json.dumps(cache_value)
        
        read_times = []
        for i in range(100):
            start_time = time.time()
            result = performance_optimizer.get_cached_result("test_type", f"{cache_key}_{i}")
            read_times.append(time.time() - start_time)
        
        avg_read_time = statistics.mean(read_times)
        print(f"Average cache read time: {avg_read_time:.6f}s")
        
        assert avg_write_time < 0.01  # 寫入應該很快
        assert avg_read_time < 0.01   # 讀取應該很快
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, conversation_engine, mock_llm_client):
        """測試高負載下的內存使用"""
        import psutil
        import os
        
        # 獲取初始內存使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "provide_info", json.dumps({"destination": f"城市{i}", "duration": 3})
            for i in range(1000)
        ]
        
        # 處理大量請求
        tasks = []
        for i in range(1000):
            task = conversation_engine.process_message(
                session_id=f"memory_test_session_{i}",
                user_message=f"我想去城市{i}旅遊"
            )
            tasks.append(task)
        
        # 分批處理以避免過載
        batch_size = 50
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            
            # 檢查內存使用
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            print(f"Batch {i//batch_size + 1}: Memory increase: {memory_increase:.2f}MB")
            
            # 內存增長不應該過大
            assert memory_increase < 500  # 不應該超過500MB
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self, conversation_engine, mock_llm_client):
        """測試回應時間一致性"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "greeting", json.dumps({"destination": "台北"})
        ] * 50
        
        response_times = []
        
        for i in range(50):
            start_time = time.time()
            
            await conversation_engine.process_message(
                session_id=f"consistency_test_session_{i}",
                user_message="我想去台北旅遊"
            )
            
            response_times.append(time.time() - start_time)
        
        # 計算統計數據
        mean_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        std_dev = statistics.stdev(response_times)
        
        print(f"Response time statistics:")
        print(f"  Mean: {mean_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  Std Dev: {std_dev:.3f}s")
        print(f"  Min: {min(response_times):.3f}s")
        print(f"  Max: {max(response_times):.3f}s")
        
        # 驗證一致性
        assert std_dev < mean_time * 0.5  # 標準差不應該超過均值的50%
        assert max(response_times) < mean_time * 3  # 最大時間不應該超過均值的3倍
    
    def test_thread_pool_performance(self, conversation_engine, mock_llm_client):
        """測試線程池性能"""
        # 設置LLM回應
        mock_llm_client.generate_response.side_effect = [
            "greeting", json.dumps({"destination": f"城市{i}"})
            for i in range(100)
        ]
        
        def sync_process_message(session_id, message):
            """同步包裝器"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    conversation_engine.process_message(session_id, message)
                )
            finally:
                loop.close()
        
        # 使用線程池
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(
                    sync_process_message,
                    f"thread_test_session_{i}",
                    f"我想去城市{i}旅遊"
                )
                for i in range(100)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Thread pool processing: 100 messages in {total_time:.3f}s")
        print(f"Average time per message: {total_time/100:.3f}s")
        
        assert len(results) == 100
        assert total_time < 30.0  # 應該在30秒內完成
    
    @pytest.mark.asyncio
    async def test_error_recovery_performance(self, conversation_engine, mock_llm_client):
        """測試錯誤恢復性能"""
        # 設置一些失敗的LLM回應
        responses = []
        for i in range(20):
            if i % 5 == 0:  # 每5個請求失敗一次
                responses.append(Exception("LLM service error"))
            else:
                responses.extend(["greeting", json.dumps({"destination": f"城市{i}"})])
        
        mock_llm_client.generate_response.side_effect = responses
        
        start_time = time.time()
        
        tasks = []
        for i in range(20):
            task = conversation_engine.process_message(
                session_id=f"error_test_session_{i}",
                user_message=f"我想去城市{i}旅遊"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 檢查結果
        successful_results = [r for r in results if not isinstance(r, Exception)]
        error_results = [r for r in results if isinstance(r, Exception)]
        
        print(f"Error recovery test: {len(successful_results)} successful, {len(error_results)} errors")
        print(f"Total time: {total_time:.3f}s")
        
        # 即使有錯誤，系統也應該繼續運行
        assert len(successful_results) > 0
        assert total_time < 10.0  # 錯誤恢復不應該太慢
    
    @pytest.mark.asyncio
    async def test_large_message_performance(self, conversation_engine, mock_llm_client):
        """測試大訊息處理性能"""
        # 創建一個較長的訊息
        long_message = "我想去台北旅遊，喜歡美食、文化、自然景點，預算中等，想要悠閒的旅遊風格，計劃3天2夜，2個人，希望有詳細的行程安排，包含交通方式和時間規劃"
        
        mock_llm_client.generate_response.side_effect = [
            "provide_info",
            json.dumps({
                "destination": "台北",
                "duration": 3,
                "interests": ["美食", "文化", "自然"],
                "budget": "medium",
                "travel_style": "relaxed",
                "group_size": 2
            })
        ]
        
        start_time = time.time()
        
        result = await conversation_engine.process_message(
            session_id="large_message_test",
            user_message=long_message
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert result is not None
        assert processing_time < 3.0  # 長訊息也應該快速處理
        print(f"Large message processing time: {processing_time:.3f}s")
    
    def test_performance_metrics_collection(self, performance_optimizer):
        """測試性能指標收集"""
        # 添加一些測試指標
        for i in range(100):
            metric = PerformanceMetrics(
                operation_name=f"test_operation_{i % 5}",
                execution_time=0.1 + (i % 10) * 0.01,
                cache_hit=i % 3 == 0,
                error_count=0
            )
            performance_optimizer._record_metrics(metric)
        
        # 獲取性能報告
        report = performance_optimizer.get_performance_report()
        
        assert report["summary"]["total_operations"] == 100
        assert len(report["operation_stats"]) == 5  # 5種不同的操作
        
        # 檢查快取命中率
        cache_hit_rate = report["summary"]["overall_cache_hit_rate"]
        assert 0 <= cache_hit_rate <= 1
        
        print(f"Performance metrics collection test:")
        print(f"  Total operations: {report['summary']['total_operations']}")
        print(f"  Cache hit rate: {cache_hit_rate:.2%}")
        print(f"  Average execution time: {report['summary']['average_execution_time']:.3f}s")


class TestPerformanceBenchmarks:
    """性能基準測試"""
    
    @pytest.mark.asyncio
    async def test_benchmark_conversation_engine(self):
        """對話引擎基準測試"""
        with patch('src.itinerary_planner.application.services.unified_conversation_engine.GeminiLLMClient') as mock_llm_class, \
             patch('src.itinerary_planner.application.services.unified_conversation_engine.redis.Redis') as mock_redis_class:
            
            mock_llm = AsyncMock()
            mock_llm.generate_response.side_effect = [
                "greeting", json.dumps({"destination": "台北"})
            ] * 100
            mock_llm_class.return_value = mock_llm
            
            mock_redis = Mock()
            mock_redis.get.return_value = None
            mock_redis.setex.return_value = True
            mock_redis_class.return_value = mock_redis
            
            engine = UnifiedConversationEngine(Mock())
            
            # 基準測試
            start_time = time.time()
            
            tasks = []
            for i in range(100):
                task = engine.process_message(
                    session_id=f"benchmark_session_{i}",
                    user_message="我想去台北旅遊"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 計算性能指標
            messages_per_second = len(results) / total_time
            avg_response_time = total_time / len(results)
            
            print(f"\n=== Conversation Engine Benchmark ===")
            print(f"Total messages: {len(results)}")
            print(f"Total time: {total_time:.3f}s")
            print(f"Messages per second: {messages_per_second:.2f}")
            print(f"Average response time: {avg_response_time:.3f}s")
            
            # 性能要求
            assert messages_per_second > 10  # 每秒至少處理10個訊息
            assert avg_response_time < 1.0   # 平均回應時間少於1秒
    
    def test_benchmark_cache_performance(self):
        """快取性能基準測試"""
        with patch('src.itinerary_planner.application.services.performance_optimizer.redis.Redis') as mock_redis_class:
            mock_redis = Mock()
            mock_redis.get.return_value = None
            mock_redis.setex.return_value = True
            mock_redis_class.return_value = mock_redis
            
            optimizer = PerformanceOptimizer(Mock(), mock_redis)
            
            # 基準測試：快取寫入
            start_time = time.time()
            
            for i in range(1000):
                optimizer.cache_result("benchmark", f"key_{i}", {"data": f"value_{i}"})
            
            write_time = time.time() - start_time
            
            # 基準測試：快取讀取
            mock_redis.get.return_value = json.dumps({"data": "test_value"})
            
            start_time = time.time()
            
            for i in range(1000):
                optimizer.get_cached_result("benchmark", f"key_{i}")
            
            read_time = time.time() - start_time
            
            print(f"\n=== Cache Performance Benchmark ===")
            print(f"Write 1000 entries: {write_time:.3f}s")
            print(f"Read 1000 entries: {read_time:.3f}s")
            print(f"Write operations/sec: {1000/write_time:.2f}")
            print(f"Read operations/sec: {1000/read_time:.2f}")
            
            # 性能要求
            assert write_time < 1.0   # 寫入1000個條目應該少於1秒
            assert read_time < 0.5    # 讀取1000個條目應該少於0.5秒


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

