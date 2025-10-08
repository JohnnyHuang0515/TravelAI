"""
測試用的 ORM 模型，不包含 vector 欄位
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, ARRAY, JSON, UUID
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=True)
    provider = Column(String(50), nullable=True)  # 'email', 'google', 'facebook'
    provider_id = Column(String(255), nullable=True)  # OAuth provider ID
    avatar_url = Column(String(500), nullable=True)
    profile = Column(JSONB, default=dict, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)

class Place(Base):
    __tablename__ = "places"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    stay_minutes = Column(Integer, nullable=False)
    price_range = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    photo_urls = Column(ARRAY(String), nullable=True)
    source = Column(String(50), nullable=True)
    source_id = Column(String(255), nullable=True)
    place_metadata = Column(JSONB, nullable=True)
    # 注意：測試版本不包含 embedding 欄位
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Hour(Base):
    __tablename__ = "hours"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(PostgresUUID(as_uuid=True), ForeignKey("places.id"), nullable=False)
    weekday = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    open_min = Column(Integer, nullable=True)  # minutes from midnight
    close_min = Column(Integer, nullable=True)  # minutes from midnight
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Accommodation(Base):
    __tablename__ = "accommodations"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    price_range = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    photo_urls = Column(ARRAY(String), nullable=True)
    source = Column(String(50), nullable=True)
    source_id = Column(String(255), nullable=True)
    accommodation_metadata = Column(JSONB, nullable=True)
    # 注意：測試版本不包含 embedding 欄位
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    trip_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(PostgresUUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    day = Column(Integer, nullable=False)
    itinerary_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ItineraryItem(Base):
    __tablename__ = "itinerary_items"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(PostgresUUID(as_uuid=True), ForeignKey("itineraries.id"), nullable=False)
    place_id = Column(PostgresUUID(as_uuid=True), ForeignKey("places.id"), nullable=True)
    accommodation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("accommodations.id"), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    order_index = Column(Integer, nullable=False)
    item_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
