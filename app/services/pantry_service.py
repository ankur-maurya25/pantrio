import math
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.db.models import PantryItem
from app.repositories.pantry_repository import PantryRepository
from app.schemas.common import PagedResponse
from app.schemas.pantry import (
    PantryItemResponse,
    CreatePantryItemRequest,
    UpdatePantryItemRequest,
    StepPantryQuantityRequest
)


class PantryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PantryRepository(db)

    def _derive_status(self, quantity: float, min_threshold: float, expiry_days: int) -> str:
        if expiry_days <= 0:
            return "EXPIRED"
        if expiry_days <= 2:
            return "EXPIRING"
        if quantity <= min_threshold:
            return "LOW_STOCK"
        return "HEALTHY"

    def _to_response(self, item: PantryItem) -> PantryItemResponse:
        return PantryItemResponse(
            id=item.id,
            name=item.name,
            category=item.category,
            quantity=item.quantity,
            unit=item.unit,
            expiry_date=item.expiry_date,
            min_threshold=item.min_threshold,
            notes=item.notes or "",
            status=item.status,
            version=item.version
        )

    def get_items_paginated(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> PagedResponse[PantryItemResponse]:
        items, total = self.repo.get_items_paginated(user_id, page, limit, category, status, search)
        data = [self._to_response(item) for item in items]
        has_more = (page * limit) < total
        return PagedResponse[PantryItemResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def add_item(self, user_id: str, req: CreatePantryItemRequest) -> PantryItemResponse:
        if req.quantity < 0:
            raise ValidationException("Quantity cannot be negative.")

        expiry_days = req.expiry_days if req.expiry_days is not None else 7
        if expiry_days == 1:
            expiry_str = "Expires tomorrow"
        elif expiry_days <= 0:
            expiry_str = "Expired"
        else:
            expiry_str = f"Expires in {expiry_days} days"

        status = self._derive_status(req.quantity, req.min_threshold, expiry_days)

        item = PantryItem(
            user_id=user_id,
            name=req.name,
            category=req.category,
            quantity=req.quantity,
            unit=req.unit,
            expiry_date=expiry_str,
            min_threshold=req.min_threshold,
            notes=req.notes or "",
            status=status,
            version=1
        )
        created = self.repo.create(item)
        return self._to_response(created)

    def update_item(self, user_id: str, item_id: str, req: UpdatePantryItemRequest) -> PantryItemResponse:
        item = self.repo.get_by_id(item_id, user_id)
        if not item:
            raise NotFoundException("Pantry item not found.")

        # OCC Version check
        if item.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        item.name = req.name
        item.category = req.category
        item.quantity = req.quantity
        item.unit = req.unit
        item.min_threshold = req.min_threshold
        if req.notes is not None:
            item.notes = req.notes

        # Re-derive status
        if item.quantity <= item.min_threshold and item.status not in ["EXPIRED", "EXPIRING"]:
            item.status = "LOW_STOCK"
        elif item.quantity > item.min_threshold and item.status == "LOW_STOCK":
            item.status = "HEALTHY"

        item.version += 1
        updated = self.repo.update(item)
        return self._to_response(updated)

    def step_quantity(self, user_id: str, item_id: str, req: StepPantryQuantityRequest) -> PantryItemResponse:
        item = self.repo.get_by_id(item_id, user_id)
        if not item:
            raise NotFoundException("Pantry item not found.")

        # OCC Version check
        if item.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        new_qty = max(0.0, item.quantity + req.delta)
        item.quantity = round(new_qty, 2)

        if item.quantity <= item.min_threshold and item.status not in ["EXPIRED", "EXPIRING"]:
            item.status = "LOW_STOCK"
        elif item.quantity > item.min_threshold and item.status == "LOW_STOCK":
            item.status = "HEALTHY"

        item.version += 1
        updated = self.repo.update(item)
        return self._to_response(updated)

    def delete_item(self, user_id: str, item_id: str) -> None:
        item = self.repo.get_by_id(item_id, user_id)
        if not item:
            raise NotFoundException("Pantry item not found.")
        self.repo.delete(item)

    def clear_expired_items(self, user_id: str) -> int:
        return self.repo.delete_expired(user_id)
