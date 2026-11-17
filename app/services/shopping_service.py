from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.db.models import ShoppingItem
from app.repositories.shopping_repository import ShoppingRepository
from app.schemas.common import PagedResponse
from app.schemas.shopping import (
    ShoppingItemResponse,
    CreateShoppingItemRequest,
    ToggleShoppingItemRequest,
    BulkDeleteShoppingItemsRequest
)


class ShoppingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ShoppingRepository(db)

    def _to_response(self, item: ShoppingItem) -> ShoppingItemResponse:
        return ShoppingItemResponse(
            id=item.id,
            name=item.name,
            subtext=item.subtext or "",
            price=item.price,
            is_checked=item.is_checked,
            category=item.category,
            version=item.version
        )

    def get_items_paginated(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> PagedResponse[ShoppingItemResponse]:
        items, total = self.repo.get_items_paginated(user_id, page, limit)
        data = [self._to_response(item) for item in items]
        has_more = (page * limit) < total
        return PagedResponse[ShoppingItemResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def add_item(self, user_id: str, req: CreateShoppingItemRequest) -> ShoppingItemResponse:
        item = ShoppingItem(
            user_id=user_id,
            name=req.name,
            subtext=req.subtext or "",
            price=req.price,
            is_checked=False,
            category=req.category,
            version=1
        )
        created = self.repo.create(item)
        return self._to_response(created)

    def add_items_bulk(self, user_id: str, reqs: List[CreateShoppingItemRequest]) -> List[ShoppingItemResponse]:
        items = [
            ShoppingItem(
                user_id=user_id,
                name=r.name,
                subtext=r.subtext or "",
                price=r.price,
                is_checked=False,
                category=r.category,
                version=1
            )
            for r in reqs
        ]
        created_list = self.repo.create_bulk(items)
        return [self._to_response(item) for item in created_list]

    def toggle_item(self, user_id: str, item_id: str, req: ToggleShoppingItemRequest) -> ShoppingItemResponse:
        item = self.repo.get_by_id(item_id, user_id)
        if not item:
            raise NotFoundException("Shopping item not found.")

        # OCC Version check
        if item.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        item.is_checked = not item.is_checked
        item.version += 1
        updated = self.repo.update(item)
        return self._to_response(updated)

    def delete_item(self, user_id: str, item_id: str) -> None:
        item = self.repo.get_by_id(item_id, user_id)
        if not item:
            raise NotFoundException("Shopping item not found.")
        self.repo.delete(item)

    def delete_items_bulk(self, user_id: str, req: BulkDeleteShoppingItemsRequest) -> int:
        return self.repo.delete_bulk(user_id, req.ids)
