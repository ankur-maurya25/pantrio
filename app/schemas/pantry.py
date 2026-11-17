from typing import Optional
from app.schemas.common import CamelModel


class PantryItemResponse(CamelModel):
    id: str
    name: str
    category: str
    quantity: float
    unit: str
    expiry_date: str
    min_threshold: float = 1.0
    notes: Optional[str] = ""
    status: str = "HEALTHY"
    version: int = 1


class CreatePantryItemRequest(CamelModel):
    name: str
    category: str
    quantity: float
    unit: str
    expiry_days: Optional[int] = 7
    min_threshold: float = 1.0
    notes: Optional[str] = ""


class UpdatePantryItemRequest(CamelModel):
    name: str
    category: str
    quantity: float
    unit: str
    min_threshold: float
    notes: Optional[str] = ""
    version: int


class StepPantryQuantityRequest(CamelModel):
    delta: float
    version: int
