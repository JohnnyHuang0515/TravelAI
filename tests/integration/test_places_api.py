import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 設定測試用的資料庫 URL (使用 SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ['DATABASE_URL'] = TEST_DATABASE_URL

# 修正 sys.path
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.itinerary_planner.main import app # 假設 main.py 中有 app 實例
from src.itinerary_planner.infrastructure.persistence.database import Base, get_db
from src.itinerary_planner.infrastructure.persistence.orm_models import Place

# --- 測試用的資料庫設定 ---
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 在測試開始前建立資料表
Base.metadata.create_all(bind=engine)

def override_get_db():
    """提供一個測試用的資料庫會話"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 讓 FastAPI app 使用測試資料庫
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- 測試資料 ---
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # 在測試開始前插入一些資料
    db = TestingSessionLocal()
    
    # 清空舊資料
    db.query(Place).delete()

    # 由於 SQLite 不支援 PostGIS，我們無法直接測試地理查詢
    # 這裡我們簡化測試，只測試其他過濾條件
    place1 = Place(name="Test Restaurant", categories=["美食"], rating=4.5)
    place2 = Place(name="Test Cafe", categories=["咖啡"], rating=3.8)
    place3 = Place(name="Another Restaurant", categories=["美食"], rating=4.8)
    
    db.add_all([place1, place2, place3])
    db.commit()
    
    yield # 執行測試
    
    # 測試結束後清理
    db.query(Place).delete()
    db.commit()
    db.close()

# --- API 測試 ---

def test_search_by_category():
    response = client.get("/v1/places/search?categories=美食")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "Test Restaurant" in [p['name'] for p in data]
    assert "Another Restaurant" in [p['name'] for p in data]

def test_search_by_min_rating():
    response = client.get("/v1/places/search?min_rating=4.6")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == "Another Restaurant"

def test_search_no_results():
    response = client.get("/v1/places/search?categories=景點")
    assert response.status_code == 200
    assert response.json() == []

# 注意：由於 SQLite 不支援 PostGIS，地理半徑搜索的測試無法在此進行。
# 需要一個真實的 Postgres 測試資料庫才能進行完整的整合測試。
