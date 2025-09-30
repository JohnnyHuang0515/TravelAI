from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# 從環境變數讀取資料庫連線 URL，並提供一個本地開發的預設值
# 預設格式: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/itinerary_db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI 的依賴注入函式
def get_db():
    """為每個 API 請求提供一個獨立的資料庫會話。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
