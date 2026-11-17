from app.schemas.common import CamelModel


class StoreResponse(CamelModel):
    id: str
    name: str
    category: str
    delivery_time: str = "25-35 mins"
    rating: str = "4.8"
    orders_fulfilled: int = 0
    delivery_fee: float = 25.0
    is_open: bool = True
    address: str = ""
    lat: float = 0.0
    lng: float = 0.0
