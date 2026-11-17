from typing import List, Optional
from app.schemas.common import CamelModel


class ShoppingItemResponse(CamelModel):
    id: str
    name: str
    subtext: str = ""
    price: float = 0.0
    is_checked: bool = False
    category: str
    version: int = 1


class CreateShoppingItemRequest(CamelModel):
    name: str
    subtext: Optional[str] = ""
    price: float = 0.0
    category: str = "OTHER"


class ToggleShoppingItemRequest(CamelModel):
    version: int


class BulkDeleteShoppingItemsRequest(CamelModel):
    ids: List[str]
