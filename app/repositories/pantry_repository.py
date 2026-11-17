from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import PantryItem


class PantryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: str, user_id: Optional[str] = None) -> Optional[PantryItem]:
        query = self.db.query(PantryItem).filter(PantryItem.id == item_id)
        if user_id:
            query = query.filter(PantryItem.user_id == user_id)
        return query.first()

    def get_items_paginated(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[PantryItem], int]:
        query = self.db.query(PantryItem).filter(PantryItem.user_id == user_id)
        if category:
            query = query.filter(PantryItem.category.ilike(category))
        if status:
            query = query.filter(PantryItem.status == status.upper())
        if search:
            query = query.filter(PantryItem.name.ilike(f"%{search}%"))

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(PantryItem.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create(self, item: PantryItem) -> PantryItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: PantryItem) -> PantryItem:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: PantryItem) -> None:
        self.db.delete(item)
        self.db.commit()

    def delete_expired(self, user_id: str) -> int:
        deleted = self.db.query(PantryItem).filter(
            PantryItem.user_id == user_id,
            PantryItem.status == "EXPIRED"
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted
