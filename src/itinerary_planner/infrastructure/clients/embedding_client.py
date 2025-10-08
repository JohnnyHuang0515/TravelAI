import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingClient:
    """向量嵌入客戶端，用於生成文字嵌入"""
    
    def __init__(self):
        # 使用支援中文的模型
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def get_embedding(self, text: str) -> list:
        """
        將文字轉換為向量嵌入
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

# 建立單例
embedding_client = EmbeddingClient()