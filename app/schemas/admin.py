from app.schemas.common import CamelModel


class PlatformMetricsResponse(CamelModel):
    total_users: int = 0
    total_stores: int = 0
    total_orders_today: int = 0
    revenue_today: float = 0.0
    pending_store_approvals: int = 0


class PlatformUserResponse(CamelModel):
    id: str
    name: str
    email: str
    role: str
    joined_at: str
    status: str
    activity_metric: str = "0 orders placed"
    version: int = 1


class ToggleUserStatusRequest(CamelModel):
    version: int


class PlatformStoreResponse(CamelModel):
    id: str
    name: str
    owner_name: str
    category: str
    address: str
    status: str
    orders_fulfilled: int = 0
    rating: str = "4.8"
    version: int = 1


class UpdateStoreApprovalRequest(CamelModel):
    status: str
    version: int


class PlatformOrderResponse(CamelModel):
    id: str
    store_id: str
    store_name: str
    customer_name: str
    total: float
    status: str
    placed_at: str
    items_count: int = 0
