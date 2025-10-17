"""
ORM 模型定義
包含所有資料表的 SQLAlchemy 模型
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, ARRAY, UUID as PG_UUID, 
    ForeignKey, Time, Text, Boolean, Date, BigInteger,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
# from pgvector.sqlalchemy import Vector  # 暫時移除向量支援
from .database import Base


# ============================================================================
# 景點相關模型（已存在）
# ============================================================================

class Place(Base):
    """地點 (Place) 的 ORM 模型"""
    __tablename__ = "places"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), index=True)  # WGS 84
    categories = Column(ARRAY(String))
    tags = Column(ARRAY(String))
    stay_minutes = Column(Integer, default=60, nullable=False)
    price_range = Column(Integer)
    rating = Column(Numeric(2, 1))
    description = Column(Text)
    address = Column(Text)
    phone = Column(String(50))
    website = Column(String(500))
    photo_urls = Column(ARRAY(String))
    source = Column(String(50))
    source_id = Column(String(255))
    place_metadata = Column(JSONB)
    # embedding = Column(Vector(384))  # 向量嵌入支援語義搜尋 (暫時移除)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    hours = relationship("Hour", back_populates="place", cascade="all, delete-orphan")
    favorites = relationship("PlaceFavorite", back_populates="place", cascade="all, delete-orphan")
    visits = relationship("TripVisit", back_populates="place")


class Hour(Base):
    """營業時間 (Hour) 的 ORM 模型"""
    __tablename__ = "hours"

    place_id = Column(PG_UUID(as_uuid=True), ForeignKey("places.id"), primary_key=True)
    weekday = Column(Integer, primary_key=True)  # 0=Sunday, 1=Monday, ...
    open_min = Column(Integer, primary_key=True)  # 從午夜起算的分鐘數
    close_min = Column(Integer, nullable=False)  # 跨夜時 close_min < open_min
    
    # 關聯
    place = relationship("Place", back_populates="hours")


class Accommodation(Base):
    """住宿 (Accommodation) 的 ORM 模型"""
    __tablename__ = "accommodations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), index=True)
    type = Column(String, nullable=False)  # 'hotel', 'hostel', 'homestay'
    price_range = Column(Integer)  # 1-5
    rating = Column(Numeric(2, 1))
    check_in_time = Column(Time, default='15:00')
    check_out_time = Column(Time, default='11:00')
    amenities = Column(ARRAY(String))  # 設施列表
    address = Column(Text)
    phone = Column(String)
    website = Column(String)
    # embedding = Column(Vector(384))  # 向量嵌入支援語義搜尋 (暫時移除)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    trip_days = relationship("TripDay", back_populates="accommodation")


# ============================================================================
# 使用者相關模型（新增）
# ============================================================================

class User(Base):
    """使用者 (User) 的 ORM 模型"""
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100))
    password_hash = Column(String(255))  # bcrypt 雜湊
    provider = Column(String(50))  # 'email', 'google', 'facebook'
    provider_id = Column(String(255))  # OAuth provider ID (統一使用此欄位)
    avatar_url = Column(String(500))  # 使用者頭像 URL
    profile = Column(JSONB, default=dict)  # {phone, bio, ...}
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)  # Email 驗證狀態
    
    # 關聯
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trips = relationship("UserTrip", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("PlaceFavorite", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ConversationSession", back_populates="user", cascade="all, delete-orphan")
    feedback_events = relationship("FeedbackEvent", back_populates="user", cascade="all, delete-orphan")
    
    # 約束
    __table_args__ = (
        CheckConstraint(
            "(provider = 'email' AND password_hash IS NOT NULL) OR "
            "(provider IN ('google', 'facebook') AND provider_id IS NOT NULL)",
            name="check_auth_method"
        ),
    )


class UserPreference(Base):
    """使用者偏好設定 (UserPreference) 的 ORM 模型"""
    __tablename__ = "user_preferences"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    favorite_themes = Column(ARRAY(String))  # ['美食', '自然', '文化', ...]
    travel_pace = Column(String(20), default='moderate')  # 'relaxed', 'moderate', 'packed'
    budget_level = Column(String(20), default='moderate')  # 'budget', 'moderate', 'luxury'
    default_daily_start = Column(Time, default='09:00')
    default_daily_end = Column(Time, default='18:00')
    custom_settings = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="preferences")
    
    # 約束
    __table_args__ = (
        CheckConstraint("travel_pace IN ('relaxed', 'moderate', 'packed')", name="check_travel_pace"),
        CheckConstraint("budget_level IN ('budget', 'moderate', 'luxury')", name="check_budget_level"),
    )


# ============================================================================
# 行程相關模型（新增）
# ============================================================================

class UserTrip(Base):
    """使用者行程 (UserTrip) 的 ORM 模型"""
    __tablename__ = "user_trips"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    destination = Column(String(255), index=True)  # 主要目的地
    duration_days = Column(Integer, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    itinerary_data = Column(JSONB, nullable=False)  # 完整行程 JSON
    is_public = Column(Boolean, default=False, index=True)
    share_token = Column(String(64), unique=True)  # 分享 Token
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    user = relationship("User", back_populates="trips")
    days = relationship("TripDay", back_populates="trip", cascade="all, delete-orphan", order_by="TripDay.day_number")
    feedback_events = relationship("FeedbackEvent", back_populates="trip", cascade="all, delete-orphan")
    
    # 約束
    __table_args__ = (
        CheckConstraint("duration_days > 0", name="check_duration_days"),
        CheckConstraint("end_date >= start_date", name="check_dates"),
    )


class TripDay(Base):
    """行程天數明細 (TripDay) 的 ORM 模型"""
    __tablename__ = "trip_days"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(PG_UUID(as_uuid=True), ForeignKey("user_trips.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)  # 第幾天
    date = Column(Date, nullable=False, index=True)
    accommodation_id = Column(PG_UUID(as_uuid=True), ForeignKey("accommodations.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    trip = relationship("UserTrip", back_populates="days")
    accommodation = relationship("Accommodation", back_populates="trip_days")
    visits = relationship("TripVisit", back_populates="trip_day", cascade="all, delete-orphan", order_by="TripVisit.visit_order")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("trip_id", "day_number", name="uq_trip_day_number"),
        CheckConstraint("day_number > 0", name="check_day_number"),
    )


class TripVisit(Base):
    """行程景點訪問 (TripVisit) 的 ORM 模型"""
    __tablename__ = "trip_visits"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_day_id = Column(PG_UUID(as_uuid=True), ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=False, index=True)
    place_id = Column(PG_UUID(as_uuid=True), ForeignKey("places.id", ondelete="SET NULL"), index=True)
    visit_order = Column(Integer, nullable=False)  # 訪問順序
    eta = Column(Time, nullable=False)  # Estimated Time of Arrival
    etd = Column(Time, nullable=False)  # Estimated Time of Departure
    travel_minutes = Column(Integer, default=0)  # 交通時間（分鐘）
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    trip_day = relationship("TripDay", back_populates="visits")
    place = relationship("Place", back_populates="visits")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("trip_day_id", "visit_order", name="uq_trip_day_visit_order"),
        CheckConstraint("visit_order > 0", name="check_visit_order"),
    )


class PlaceFavorite(Base):
    """景點收藏 (PlaceFavorite) 的 ORM 模型"""
    __tablename__ = "place_favorites"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    place_id = Column(PG_UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 關聯
    user = relationship("User", back_populates="favorites")
    place = relationship("Place", back_populates="favorites")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("user_id", "place_id", name="uq_user_place_favorite"),
    )


# ============================================================================
# 對話與回饋模型（新增）
# ============================================================================

class ConversationSession(Base):
    """對話 Session (ConversationSession) 的 ORM 模型"""
    __tablename__ = "conversation_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)  # 可為 NULL（訪客）
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    state_data = Column(JSONB, default=dict)  # LangGraph 狀態
    last_user_input = Column(Text)
    last_ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, index=True)  # Session 過期時間
    is_active = Column(Boolean, default=True)
    
    # 關聯
    user = relationship("User", back_populates="sessions")


class FeedbackEvent(Base):
    """使用者回饋記錄 (FeedbackEvent) 的 ORM 模型"""
    __tablename__ = "feedback_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(255), index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    trip_id = Column(PG_UUID(as_uuid=True), ForeignKey("user_trips.id", ondelete="SET NULL"), index=True)
    place_id = Column(PG_UUID(as_uuid=True))  # 不設定 FK，可能是尚未加入的景點
    op = Column(String(20))  # 'DROP', 'REPLACE', 'MOVE', 'ADD'
    feedback_text = Column(Text)  # 原始回饋文字
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 關聯
    user = relationship("User", back_populates="feedback_events")
    trip = relationship("UserTrip", back_populates="feedback_events")
    
    # 約束
    __table_args__ = (
        CheckConstraint("op IN ('DROP', 'REPLACE', 'MOVE', 'ADD')", name="check_op"),
    )


# ============================================================================
# 公車運輸相關模型（新增）
# ============================================================================

class BusRoute(Base):
    """公車路線 (BusRoute) 的 ORM 模型"""
    __tablename__ = "bus_routes"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(String(50), unique=True, nullable=False, index=True)  # 路線ID (如: 11, 12)
    route_name = Column(String(50), nullable=False, index=True)  # 路線編號 (如: 紅1, 綠12)
    departure_stop = Column(String(255), nullable=False)  # 起站
    destination_stop = Column(String(255), nullable=False)  # 迄站
    route_type = Column(String(50))  # 路線類型
    status = Column(String(50))  # 營運狀態
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯
    stations = relationship("BusStation", back_populates="route", cascade="all, delete-orphan")
    trips = relationship("BusTrip", back_populates="route", cascade="all, delete-orphan")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("route_id", name="uq_bus_route_id"),
        UniqueConstraint("route_name", name="uq_bus_route_name"),
    )


class BusStation(Base):
    """公車站點 (BusStation) 的 ORM 模型"""
    __tablename__ = "bus_stations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(PG_UUID(as_uuid=True), ForeignKey("bus_routes.id", ondelete="CASCADE"), nullable=False, index=True)
    station_id = Column(String(50), nullable=False, index=True)  # 站牌ID
    station_name = Column(String(255), nullable=False)  # 站名
    sequence = Column(Integer, nullable=False)  # 站序
    direction = Column(Integer, nullable=False)  # 方向 (0: 去程, 1: 回程)
    geom = Column(Geometry('POINT', srid=4326), index=True)  # 站點座標
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    route = relationship("BusRoute", back_populates="stations")
    stop_times = relationship("BusStopTime", back_populates="station", cascade="all, delete-orphan")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("route_id", "station_id", "direction", "sequence", name="uq_bus_station_sequence"),
    )


class BusTrip(Base):
    """公車班次 (BusTrip) 的 ORM 模型"""
    __tablename__ = "bus_trips"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(PG_UUID(as_uuid=True), ForeignKey("bus_routes.id", ondelete="CASCADE"), nullable=False, index=True)
    trip_id = Column(String(50), nullable=False, index=True)  # 班次ID
    direction = Column(Integer, nullable=False)  # 方向 (0: 去程, 1: 回程)
    departure_time = Column(Time, nullable=False)  # 發車時間
    departure_station = Column(String(255), nullable=False)  # 發車站名
    operating_days = Column(ARRAY(String))  # 營運日 ["Monday", "Tuesday", ...]
    is_low_floor = Column(Boolean, default=False)  # 是否為低地板公車
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    route = relationship("BusRoute", back_populates="trips")
    stop_times = relationship("BusStopTime", back_populates="trip", cascade="all, delete-orphan")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("route_id", "trip_id", "direction", name="uq_bus_trip"),
    )


class BusStopTime(Base):
    """公車時刻表 (BusStopTime) 的 ORM 模型"""
    __tablename__ = "bus_stop_times"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(PG_UUID(as_uuid=True), ForeignKey("bus_trips.id", ondelete="CASCADE"), nullable=False, index=True)
    station_id = Column(PG_UUID(as_uuid=True), ForeignKey("bus_stations.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)  # 站序
    arrival_time = Column(Time, nullable=False)  # 抵達時間
    departure_time = Column(Time, nullable=False)  # 離站時間
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    trip = relationship("BusTrip", back_populates="stop_times")
    station = relationship("BusStation", back_populates="stop_times")
    
    # 約束
    __table_args__ = (
        UniqueConstraint("trip_id", "sequence", name="uq_bus_stop_time_sequence"),
    )


# ============================================================================
# 運輸整合相關模型（新增）
# ============================================================================

class TransportConnection(Base):
    """運輸連接點 (TransportConnection) 的 ORM 模型"""
    __tablename__ = "transport_connections"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(PG_UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=True, index=True)
    station_id = Column(PG_UUID(as_uuid=True), ForeignKey("bus_stations.id", ondelete="CASCADE"), nullable=True, index=True)
    connection_type = Column(String(50), nullable=False)  # 'bus_station', 'transfer_point'
    distance_meters = Column(Integer)  # 距離 (公尺)
    walking_time_minutes = Column(Integer)  # 步行時間 (分鐘)
    is_accessible = Column(Boolean, default=True)  # 是否無障礙
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 約束
    __table_args__ = (
        CheckConstraint(
            "(place_id IS NOT NULL AND station_id IS NULL) OR "
            "(place_id IS NULL AND station_id IS NOT NULL)",
            name="check_connection_reference"
        ),
    )