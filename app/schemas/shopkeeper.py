from typing import List, Optional
from app.schemas.common import CamelModel


class StoreProfileResponse(CamelModel):
    name: str
    owner_name: str
    address: str
    delivery_time: str
    delivery_radius: str
    operating_hours: str
    is_open: bool
    version: int = 1


class UpdateStoreProfileRequest(CamelModel):
    name: str
    address: str
    delivery_time: str
    delivery_radius: str
    operating_hours: str
    version: int


class ToggleStoreStatusRequest(CamelModel):
    version: int


class StoreOrderItemDto(CamelModel):
    id: str
    name: str
    quantity: float
    unit: str
    price: float


class StoreOrderResponse(CamelModel):
    id: str
    customer_name: str
    customer_phone: str = ""
    customer_address: str
    total: float
    status: str
    placed_at: str
    items: List[StoreOrderItemDto] = []
    version: int = 1


class UpdateOrderStatusRequest(CamelModel):
    status: str
    version: int


class StoreInventoryItemResponse(CamelModel):
    id: str
    name: str
    category: str
    stock_qty: float
    unit: str
    price: float
    is_available: bool = True
    min_threshold: float = 2.0
    version: int = 1


class CreateInventoryItemRequest(CamelModel):
    name: str
    category: str
    stock_qty: float
    unit: str
    price: float
    min_threshold: float = 2.0


class UpdateInventoryItemRequest(CamelModel):
    name: str
    category: str
    stock_qty: float
    unit: str
    price: float
    is_available: bool
    min_threshold: float
    version: int


class StepStockRequest(CamelModel):
    delta: float
    version: int


class ShopkeeperDashboardResponse(CamelModel):
    profile: StoreProfileResponse
    today_revenue: float = 0.0
    total_orders_today: int = 0
    pending_actions: int = 0
    low_stock_alerts: int = 0
    today_orders_count: int = 0
    pending_orders_count: int = 0
    low_stock_items_count: int = 0

