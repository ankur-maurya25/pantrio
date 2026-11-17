import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SqlEnum
)
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="CUSTOMER", index=True)  # CUSTOMER, SHOPKEEPER, ADMIN
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, SUSPENDED
    activity_metric = Column(String(100), nullable=False, default="0 orders placed")
    location = Column(String(255), nullable=True, default="Mainpuri")
    joined_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    pantry_items = relationship("PantryItem", back_populates="user", cascade="all, delete-orphan")
    shopping_items = relationship("ShoppingItem", back_populates="user", cascade="all, delete-orphan")
    customer_location = relationship("CustomerLocation", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    stores = relationship("Store", back_populates="owner", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="refresh_tokens")


class CustomerLocation(Base):
    __tablename__ = "customer_locations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False, default=0.0)
    lng = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="customer_location")


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    quantity = Column(Float, nullable=False, default=1.0)
    unit = Column(String(20), nullable=False, default="pcs")
    expiry_date = Column(String(50), nullable=False, default="Expires in 7 days")
    min_threshold = Column(Float, nullable=False, default=1.0)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="HEALTHY", index=True)  # HEALTHY, LOW_STOCK, EXPIRING, EXPIRED
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="pantry_items")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    subtext = Column(String(50), nullable=False, default="")
    price = Column(Float, nullable=False, default=0.0)
    is_checked = Column(Boolean, nullable=False, default=False)
    category = Column(String(50), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="shopping_items")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(100), nullable=False)
    duration = Column(String(30), nullable=False)
    calories = Column(String(30), nullable=False)
    difficulty = Column(String(30), nullable=False)
    match_percentage = Column(Integer, nullable=False, default=100)
    tags = Column(JSON, nullable=False)  # List[str]
    ingredients = Column(JSON, nullable=False)  # List[str]
    instructions = Column(JSON, nullable=False)  # List[str]
    image_url = Column(String(255), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class Store(Base):
    __tablename__ = "stores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    owner_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False, default=0.0)
    lng = Column(Float, nullable=False, default=0.0)
    delivery_time = Column(String(30), nullable=False, default="25-35 mins")
    rating = Column(String(10), nullable=False, default="4.8")
    orders_fulfilled = Column(Integer, nullable=False, default=0)
    delivery_fee = Column(Float, nullable=False, default=25.0)
    delivery_radius = Column(String(30), nullable=False, default="5 km")
    operating_hours = Column(String(50), nullable=False, default="7:00 AM - 10:00 PM")
    is_open = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default="APPROVED", index=True)  # PENDING_APPROVAL, APPROVED, SUSPENDED
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="stores")
    inventory = relationship("StoreInventory", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("StoreOrder", back_populates="store", cascade="all, delete-orphan")


class StoreInventory(Base):
    __tablename__ = "store_inventory"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    stock_qty = Column(Float, nullable=False, default=0.0)
    unit = Column(String(20), nullable=False, default="kg")
    price = Column(Float, nullable=False, default=0.0)
    is_available = Column(Boolean, nullable=False, default=True)
    min_threshold = Column(Float, nullable=False, default=2.0)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    store = relationship("Store", back_populates="inventory")


class StoreOrder(Base):
    __tablename__ = "store_orders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    store_id = Column(String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(30), nullable=False, default="")
    customer_address = Column(String(255), nullable=False)
    total = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), nullable=False, default="PENDING", index=True)  # PENDING, PREPARING, READY_FOR_PICKUP, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
    placed_at = Column(String(50), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    store = relationship("Store", back_populates="orders")
    items = relationship("StoreOrderItem", back_populates="order", cascade="all, delete-orphan")


class StoreOrderItem(Base):
    __tablename__ = "store_order_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("store_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("StoreOrder", back_populates="items")
