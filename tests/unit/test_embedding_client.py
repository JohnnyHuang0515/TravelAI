"""
測試 embedding_client.py
"""

import pytest
import sys
from unittest.mock import Mock, patch
import numpy as np

# Mock sentence_transformers 模組
with patch.dict('sys.modules', {'sentence_transformers': Mock()}):
    from src.itinerary_planner.infrastructure.clients.embedding_client import EmbeddingClient, embedding_client


class TestEmbeddingClient:
    """測試向量嵌入客戶端"""

    def test_embedding_client_initialization(self):
        """測試嵌入客戶端初始化"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 驗證初始化
            assert client.model == mock_model
            mock_transformer.assert_called_once_with('all-MiniLM-L6-v2')

    def test_get_embedding_success(self):
        """測試成功獲取嵌入向量"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
            mock_model.encode.return_value = mock_embedding
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 執行測試
            result = client.get_embedding("測試文字")
            
            # 驗證結果
            assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_model.encode.assert_called_once_with("測試文字")

    def test_get_embedding_different_texts(self):
        """測試不同文字的嵌入向量"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 測試多個文字
            test_texts = [
                "台北101",
                "西門町",
                "故宮博物院",
                "陽明山國家公園"
            ]
            
            for i, text in enumerate(test_texts):
                mock_embedding = np.array([i * 0.1, i * 0.2, i * 0.3])
                mock_model.encode.return_value = mock_embedding
                
                result = client.get_embedding(text)
                
                # 驗證結果
                expected = [i * 0.1, i * 0.2, i * 0.3]
                assert result == expected
                mock_model.encode.assert_called_with(text)

    def test_get_embedding_empty_text(self):
        """測試空文字的嵌入向量"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_embedding = np.array([])
            mock_model.encode.return_value = mock_embedding
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 執行測試
            result = client.get_embedding("")
            
            # 驗證結果
            assert result == []
            mock_model.encode.assert_called_once_with("")

    def test_get_embedding_long_text(self):
        """測試長文字的嵌入向量"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_embedding = np.array([0.1] * 384)  # 模擬 384 維向量
            mock_model.encode.return_value = mock_embedding
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 執行測試
            long_text = "這是一個很長的文字描述，用來測試嵌入客戶端對長文字的處理能力。" * 10
            result = client.get_embedding(long_text)
            
            # 驗證結果
            assert len(result) == 384
            assert all(x == 0.1 for x in result)
            mock_model.encode.assert_called_once_with(long_text)

    def test_singleton_instance(self):
        """測試單例實例"""
        # 驗證單例實例存在
        assert embedding_client is not None
        assert isinstance(embedding_client, EmbeddingClient)

    def test_get_embedding_unicode_text(self):
        """測試 Unicode 文字的嵌入向量"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_embedding = np.array([0.5, 0.6, 0.7])
            mock_model.encode.return_value = mock_embedding
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 執行測試 - 包含各種 Unicode 字符
            unicode_text = "台北101 🏢 西門町 🛍️ 故宮博物院 🏛️"
            result = client.get_embedding(unicode_text)
            
            # 驗證結果
            assert result == [0.5, 0.6, 0.7]
            mock_model.encode.assert_called_once_with(unicode_text)

    def test_get_embedding_special_characters(self):
        """測試特殊字符的嵌入向量"""
        with patch('src.itinerary_planner.infrastructure.clients.embedding_client.SentenceTransformer') as mock_transformer:
            # 設定 Mock 返回值
            mock_model = Mock()
            mock_embedding = np.array([0.8, 0.9, 1.0])
            mock_model.encode.return_value = mock_embedding
            mock_transformer.return_value = mock_model
            
            # 創建客戶端實例
            client = EmbeddingClient()
            
            # 執行測試 - 包含特殊字符
            special_text = "景點名稱：台北101 (Taipei 101) - 地址：信義區信義路五段7號"
            result = client.get_embedding(special_text)
            
            # 驗證結果
            assert result == [0.8, 0.9, 1.0]
            mock_model.encode.assert_called_once_with(special_text)
