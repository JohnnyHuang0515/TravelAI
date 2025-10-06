from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="智慧旅遊行程規劃器 API",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由 API
from .api.v1.routing import router as routing_router
app.include_router(routing_router, prefix="/v1")

# 健康檢查端點
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 地點搜索端點
@app.get("/v1/places/search")
def search_places(
    lat: Optional[float] = Query(None, description="緯度"),
    lon: Optional[float] = Query(None, description="經度"),
    radius: int = Query(5000, description="搜索半徑（公尺）"),
    categories: Optional[str] = Query(None, description="類別（多個用逗號分隔）"),
    min_rating: Optional[float] = Query(None, description="最低評分"),
    db: Session = Depends(lambda: None)  # 暫時的依賴
):
    """
    搜索地點 API 端點。
    """
    try:
        # 延遲導入以避免循環依賴
        from .infrastructure.persistence.database import get_db
        from .infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
        
        # 重新獲取資料庫連接
        from .infrastructure.persistence.database import SessionLocal
        db_session = SessionLocal()
        
        # 處理類別參數
        categories_list = None
        if categories:
            categories_list = [cat.strip() for cat in categories.split(',')]
        
        logger.info(f"Search places request: lat={lat}, lon={lon}, radius={radius}, categories={categories_list}, min_rating={min_rating}")
        
        repo = PostgresPlaceRepository(db_session)
        places = repo.search(
            lat=lat,
            lon=lon,
            radius=radius,
            categories=categories_list,
            min_rating=min_rating
        )
        
        logger.info(f"Found {len(places)} places")
        
        # 轉換為簡單的字典格式
        result = []
        for place in places:
            result.append({
                "id": str(place.id),
                "name": place.name,
                "categories": place.categories or [],
                "rating": float(place.rating) if place.rating else None,
                "stay_minutes": place.stay_minutes,
                "price_range": place.price_range
            })
        
        db_session.close()
        return result
        
    except Exception as e:
        logger.error(f"Error in search_places: {str(e)}", exc_info=True)
        return {"error": str(e)}

# 註冊行程規劃路由
try:
    from .api.v1.endpoints import planning
    app.include_router(planning.router, prefix="/v1/itinerary", tags=["Itinerary Planning"])
    logger.info("✅ 行程規劃路由註冊成功")
except Exception as e:
    logger.error(f"❌ 行程規劃路由註冊失敗: {e}")
    import traceback
    traceback.print_exc()

# 註冊對話式規劃路由
try:
    from .api.v1.endpoints import conversation
    app.include_router(conversation.router, prefix="/v1/chat", tags=["Conversational Planning"])
    logger.info("✅ 對話式規劃路由註冊成功")
except Exception as e:
    logger.error(f"❌ 對話式規劃路由註冊失敗: {e}")
    import traceback
    traceback.print_exc()

# 註冊認證路由
try:
    from .api.v1.endpoints import auth
    app.include_router(auth.router, prefix="/v1/auth", tags=["認證"])
    logger.info("✅ 認證路由註冊成功")
except Exception as e:
    logger.error(f"❌ 認證路由註冊失敗: {e}")
    import traceback
    traceback.print_exc()

# 註冊行程管理路由
try:
    from .api.v1.endpoints import trips
    app.include_router(trips.router, prefix="/v1", tags=["行程管理"])
    logger.info("✅ 行程管理路由註冊成功")
except Exception as e:
    logger.error(f"❌ 行程管理路由註冊失敗: {e}")
    import traceback
    traceback.print_exc()

# 註冊景點推薦路由
try:
    from .api.v1.endpoints import places_enhanced
    app.include_router(places_enhanced.router, prefix="/v1", tags=["景點推薦"])
    logger.info("✅ 景點推薦路由註冊成功")
except Exception as e:
    logger.error(f"❌ 景點推薦路由註冊失敗: {e}")
    import traceback
    traceback.print_exc()

# 註冊路由計算路由
try:
    from .api.v1.endpoints import routing
    app.include_router(routing.router, prefix="/v1", tags=["路由計算"])
    logger.info("✅ 路由計算路由註冊成功")
except Exception as e:
    logger.error(f"❌ 路由計算路由註冊失敗: {e}")
    import traceback
    traceback.print_exc()