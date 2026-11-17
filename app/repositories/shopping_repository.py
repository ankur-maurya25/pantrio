from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import ShoppingItem


class ShoppingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: str, user_id: Optional[str] = None) -> Optional[ShoppingItem]:
        query = self.db.query(ShoppingItem).filter(ShoppingItem.id == item_id)
        if user_id:
            query = query.filter(ShoppingItem.user_id == user_id)
        return query.first()

    def get_items_paginated(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ShoppingItem], int]:
        query = self.db.query(ShoppingItem).filter(ShoppingItem.user_id == user_id)
        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(ShoppingItem.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create(self, item: ShoppingItem) -> ShoppingItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_bulk(self, items: List[ShoppingItem]) -> List[ShoppingItem]:
        self.db.add_all(items)
        self.db.commit()
        for item in items:
            self.db.refresh(item)
        return items

    def update(self, item: ShoppingItem) -> ShoppingItem:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: ShoppingItem) -> None:
        self.db.delete(item)
        self.db.commit()

    def delete_bulk(self, user_id: str, item_ids: List[str]) -> int:
        deleted = self.db.query(ShoppingItem).filter(
            ShoppingItem.user_id == user_id,
            ShoppingItem.id.in_(item_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted
