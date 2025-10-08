"""
測試配置檔案 - 提供全域的 pytest fixtures 和設定
"""
import pytest
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# 設定測試環境變數
os.environ['TESTING'] = 'true'
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/itinerary_test_db'

from tests.test_orm_models import Base, User, Place, Accommodation, Trip, Itinerary, ItineraryItem, Hour
from sqlalchemy.orm import Session
from unittest.mock import Mock


@pytest.fixture(scope="session")
def test_engine():
    """測試用的資料庫引擎"""
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/itinerary_test_db')
    engine = create_engine(database_url)
    
    # 建立測試資料庫表格
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # 清理測試資料庫
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """測試用的資料庫會話"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def mock_db_session():
    """提供一個 Mock 的 SQLAlchemy Session 用於單元測試"""
    return Mock(spec=Session)


# @pytest.fixture(scope="function")
# def test_client(test_db):
#     """測試用的 FastAPI 客戶端"""
#     # 這個 fixture 需要實際的 FastAPI app 實例
#     # 暫時註解掉，等主應用程式完成後再啟用
#     pass


@pytest.fixture(scope="function")
def mock_external_services():
    """Mock 外部服務 (LLM, OSRM, Embedding)"""
    with patch('src.itinerary_planner.application.graph_nodes.llm_client') as mock_llm, \
         patch('src.itinerary_planner.application.graph_nodes.osrm_client') as mock_osrm, \
         patch('src.itinerary_planner.application.graph_nodes.embedding_client') as mock_embed, \
         patch('src.itinerary_planner.application.services.feedback_parser.llm_client') as mock_feedback_llm:
        
        # Mock LLM 回應
        mock_story = MagicMock()
        mock_story.days = 2
        mock_story.preference.themes = ["美食", "景點"]
        mock_story.preference.budget = "中等"
        mock_story.preference.accommodation_type = "飯店"
        mock_llm.extract_story_from_text.return_value = mock_story
        
        # Mock OSRM 回應
        mock_osrm.get_travel_time_matrix.return_value = [
            [0, 600, 1200],  # 10分鐘, 20分鐘
            [600, 0, 900],   # 10分鐘, 15分鐘
            [1200, 900, 0]   # 20分鐘, 15分鐘
        ]
        mock_osrm.get_route.return_value = {
            "routes": [{"duration": 600, "distance": 5000}]
        }
        
        # Mock Embedding 回應
        mock_embed.get_embedding.return_value = [0.1] * 1536
        
        yield {
            'llm': mock_llm,
            'osrm': mock_osrm,
            'embedding': mock_embed,
            'feedback_llm': mock_feedback_llm
        }


@pytest.fixture(scope="function")
def sample_user(test_db):
    """建立測試用的使用者"""
    user = User(
        email="test@example.com",
        username="testuser",
        provider="email",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_places(test_db):
    """建立測試用的景點資料"""
    places = [
        Place(
            name="台北101",
            categories=["景點", "購物"],
            rating=4.5,
            stay_minutes=120,
            address="台北市信義區信義路五段7號"
        ),
        Place(
            name="鼎泰豐",
            categories=["美食"],
            rating=4.8,
            stay_minutes=90,
            address="台北市信義區信義路五段7號"
        ),
        Place(
            name="西門町",
            categories=["景點", "購物"],
            rating=4.2,
            stay_minutes=180,
            address="台北市萬華區"
        )
    ]
    
    for place in places:
        test_db.add(place)
    test_db.commit()
    
    for place in places:
        test_db.refresh(place)
    
    return places


@pytest.fixture(scope="function")
def sample_accommodations(test_db):
    """建立測試用的住宿資料"""
    accommodations = [
        Accommodation(
            name="台北君悅酒店",
            categories=["飯店"],
            rating=4.6,
            address="台北市信義區松仁路100號"
        ),
        Accommodation(
            name="西門町青年旅館",
            categories=["青年旅館"],
            rating=4.0,
            address="台北市萬華區"
        )
    ]
    
    for acc in accommodations:
        test_db.add(acc)
    test_db.commit()
    
    for acc in accommodations:
        test_db.refresh(acc)
    
    return accommodations


@pytest.fixture(scope="function")
def sample_trip(test_db, sample_user, sample_places):
    """建立測試用的行程"""
    from datetime import datetime
    trip = Trip(
        user_id=sample_user.id,
        title="台北兩日遊",
        description="測試行程",
        start_date=datetime(2025, 2, 1),
        end_date=datetime(2025, 2, 2),
        status="draft"
    )
    test_db.add(trip)
    test_db.commit()
    test_db.refresh(trip)
    
    # 建立行程天數
    day1 = Itinerary(
        trip_id=trip.id,
        day=1
    )
    day2 = Itinerary(
        trip_id=trip.id,
        day=2
    )
    test_db.add_all([day1, day2])
    test_db.commit()
    test_db.refresh(day1)
    test_db.refresh(day2)
    
    # 建立行程項目
    item1 = ItineraryItem(
        itinerary_id=day1.id,
        place_id=sample_places[0].id,
        order_index=1,
        start_time=datetime(2025, 2, 1, 9, 0),
        end_time=datetime(2025, 2, 1, 11, 0)
    )
    item2 = ItineraryItem(
        itinerary_id=day1.id,
        place_id=sample_places[1].id,
        order_index=2,
        start_time=datetime(2025, 2, 1, 12, 0),
        end_time=datetime(2025, 2, 1, 14, 0)
    )
    test_db.add_all([item1, item2])
    test_db.commit()
    
    return trip


@pytest.fixture(scope="function")
def auth_headers(sample_user):
    """產生測試用的認證標頭"""
    from src.itinerary_planner.application.services.auth_service import AuthService
    from src.itinerary_planner.infrastructure.persistence.database import get_db
    
    # 這裡需要實際的資料庫會話來產生 JWT token
    # 在實際測試中，我們會使用 test_db fixture
    return {"Authorization": f"Bearer test_token_{sample_user.id}"}


# 測試標記
pytest_plugins = []

def pytest_configure(config):
    """配置 pytest 標記"""
    config.addinivalue_line("markers", "unit: 單元測試")
    config.addinivalue_line("markers", "integration: 整合測試")
    config.addinivalue_line("markers", "api: API 測試")
    config.addinivalue_line("markers", "database: 資料庫測試")
    config.addinivalue_line("markers", "slow: 慢速測試")
    config.addinivalue_line("markers", "external: 需要外部服務的測試")
