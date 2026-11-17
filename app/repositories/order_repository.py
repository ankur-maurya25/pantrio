from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import StoreOrder, StoreOrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_order_by_id(self, order_id: str, store_id: Optional[str] = None) -> Optional[StoreOrder]:
        query = self.db.query(StoreOrder).filter(StoreOrder.id == order_id)
        if store_id:
            query = query.filter(StoreOrder.store_id == store_id)
        return query.first()

    def get_orders_by_store_paginated(
        self,
        store_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[StoreOrder], int]:
        query = self.db.query(StoreOrder).filter(StoreOrder.store_id == store_id)
        if status:
            query = query.filter(StoreOrder.status == status.upper())

        total = query.count()
        offset = (page - 1) * limit
        orders = query.order_by(StoreOrder.created_at.desc()).offset(offset).limit(limit).all()
        return orders, total

    def get_all_orders_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[StoreOrder], int]:
        query = self.db.query(StoreOrder)
        if status:
            query = query.filter(StoreOrder.status == status.upper())

        total = query.count()
        offset = (page - 1) * limit
        orders = query.order_by(StoreOrder.created_at.desc()).offset(offset).limit(limit).all()
        return orders, total

    def create_order(self, order: StoreOrder, items: List[StoreOrderItem]) -> StoreOrder:
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        for item in items:
            item.order_id = order.id
            self.db.add(item)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_order(self, order: StoreOrder) -> StoreOrder:
        self.db.commit()
        self.db.refresh(order)
        return order
