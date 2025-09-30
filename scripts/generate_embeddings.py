#!/usr/bin/env python3
"""
為現有的地點資料生成 embedding
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from itinerary_planner.infrastructure.persistence.database import SessionLocal
from itinerary_planner.infrastructure.persistence.orm_models import Place
from itinerary_planner.infrastructure.clients.embedding_client import embedding_client
from sqlalchemy import text

def generate_embeddings():
    """為所有地點生成 embedding"""
    
    db = SessionLocal()
    try:
        # 啟用 pgvector 擴展
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
        
        # 獲取所有沒有 embedding 的地點
        places = db.query(Place).filter(Place.embedding.is_(None)).all()
        
        print(f"找到 {len(places)} 個地點需要生成 embedding")
        
        for i, place in enumerate(places):
            # 組合地點的文本資訊
            text_parts = [place.name]
            
            if place.categories:
                text_parts.extend(place.categories)
            
            if place.tags:
                text_parts.extend(place.tags)
            
            # 生成 embedding
            combined_text = " ".join(text_parts)
            embedding = embedding_client.get_embedding(combined_text)
            
            # 更新資料庫
            place.embedding = embedding
            db.commit()
            
            if (i + 1) % 10 == 0:
                print(f"已處理 {i + 1}/{len(places)} 個地點")
        
        print(f"完成！已為 {len(places)} 個地點生成 embedding")
        
    except Exception as e:
        print(f"錯誤: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_embeddings()
