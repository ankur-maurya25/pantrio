from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.db.models import Store, StoreInventory, StoreOrder, StoreOrderItem
from app.repositories.store_repository import StoreRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.common import PagedResponse
from app.schemas.shopkeeper import (
    StoreProfileResponse,
    UpdateStoreProfileRequest,
    ToggleStoreStatusRequest,
    StoreOrderItemDto,
    StoreOrderResponse,
    UpdateOrderStatusRequest,
    StoreInventoryItemResponse,
    CreateInventoryItemRequest,
    UpdateInventoryItemRequest,
    StepStockRequest,
    ShopkeeperDashboardResponse
)


class ShopkeeperService:
    def __init__(self, db: Session):
        self.db = db
        self.store_repo = StoreRepository(db)
        self.order_repo = OrderRepository(db)

    def _get_merchant_store(self, owner_id: str) -> Store:
        store = self.store_repo.get_store_by_owner_id(owner_id)
        if not store:
            raise NotFoundException("Merchant store profile not found.")
        return store

    def _store_to_profile(self, store: Store) -> StoreProfileResponse:
        return StoreProfileResponse(
            name=store.name,
            owner_name=store.owner_name,
            address=store.address,
            delivery_time=store.delivery_time,
            delivery_radius=store.delivery_radius,
            operating_hours=store.operating_hours,
            is_open=store.is_open,
            version=store.version
        )

    def _order_to_response(self, order: StoreOrder) -> StoreOrderResponse:
        items = [
            StoreOrderItemDto(
                id=item.id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                price=item.price
            )
            for item in order.items
        ]
        return StoreOrderResponse(
            id=order.id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone or "",
            customer_address=order.customer_address,
            total=order.total,
            status=order.status,
            placed_at=order.placed_at,
            items=items,
            version=order.version
        )

    def _inventory_to_response(self, item: StoreInventory) -> StoreInventoryItemResponse:
        return StoreInventoryItemResponse(
            id=item.id,
            name=item.name,
            category=item.category,
            stock_qty=item.stock_qty,
            unit=item.unit,
            price=item.price,
            is_available=item.is_available,
            min_threshold=item.min_threshold,
            version=item.version
        )

    def get_dashboard(self, owner_id: str) -> ShopkeeperDashboardResponse:
        store = self._get_merchant_store(owner_id)
        orders, total_orders = self.order_repo.get_orders_by_store_paginated(store.id, 1, 100)
        inventory, total_inventory = self.store_repo.get_inventory_paginated(store.id, 1, 100)

        revenue_sum = sum(o.total for o in orders if o.status != "CANCELLED")
        pending_count = sum(1 for o in orders if o.status in ["PENDING", "PREPARING"])
        low_stock_count = sum(1 for i in inventory if i.stock_qty <= i.min_threshold)

        return ShopkeeperDashboardResponse(
            profile=self._store_to_profile(store),
            today_revenue=revenue_sum,
            total_orders_today=total_orders,
            pending_actions=pending_count,
            low_stock_alerts=low_stock_count,
            today_orders_count=total_orders,
            pending_orders_count=pending_count,
            low_stock_items_count=low_stock_count
        )

    def get_orders_paginated(
        self,
        owner_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> PagedResponse[StoreOrderResponse]:
        store = self._get_merchant_store(owner_id)
        orders, total = self.order_repo.get_orders_by_store_paginated(store.id, page, limit, status)
        data = [self._order_to_response(o) for o in orders]
        has_more = (page * limit) < total
        return PagedResponse[StoreOrderResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def update_order_status(
        self,
        owner_id: str,
        order_id: str,
        req: UpdateOrderStatusRequest
    ) -> StoreOrderResponse:
        store = self._get_merchant_store(owner_id)
        order = self.order_repo.get_order_by_id(order_id, store.id)
        if not order:
            raise NotFoundException("Store order not found.")

        # OCC Version check
        if order.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        order.status = req.status.upper()
        order.version += 1
        updated = self.order_repo.update_order(order)
        return self._order_to_response(updated)

    def get_inventory_paginated(
        self,
        owner_id: str,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> PagedResponse[StoreInventoryItemResponse]:
        store = self._get_merchant_store(owner_id)
        items, total = self.store_repo.get_inventory_paginated(store.id, page, limit, category, search)
        data = [self._inventory_to_response(i) for i in items]
        has_more = (page * limit) < total
        return PagedResponse[StoreInventoryItemResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def add_inventory_item(self, owner_id: str, req: CreateInventoryItemRequest) -> StoreInventoryItemResponse:
        store = self._get_merchant_store(owner_id)
        item = StoreInventory(
            store_id=store.id,
            name=req.name,
            category=req.category,
            stock_qty=req.stock_qty,
            unit=req.unit,
            price=req.price,
            is_available=True,
            min_threshold=req.min_threshold,
            version=1
        )
        created = self.store_repo.create_inventory_item(item)
        return self._inventory_to_response(created)

    def update_inventory_item(
        self,
        owner_id: str,
        item_id: str,
        req: UpdateInventoryItemRequest
    ) -> StoreInventoryItemResponse:
        store = self._get_merchant_store(owner_id)
        item = self.store_repo.get_inventory_item_by_id(item_id, store.id)
        if not item:
            raise NotFoundException("Store inventory item not found.")

        # OCC Version check
        if item.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        item.name = req.name
        item.category = req.category
        item.stock_qty = req.stock_qty
        item.unit = req.unit
        item.price = req.price
        item.is_available = req.is_available
        item.min_threshold = req.min_threshold
        item.version += 1

        updated = self.store_repo.update_inventory_item(item)
        return self._inventory_to_response(updated)

    def step_stock_quantity(
        self,
        owner_id: str,
        item_id: str,
        req: StepStockRequest
    ) -> StoreInventoryItemResponse:
        store = self._get_merchant_store(owner_id)
        item = self.store_repo.get_inventory_item_by_id(item_id, store.id)
        if not item:
            raise NotFoundException("Store inventory item not found.")

        # OCC Version check
        if item.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        new_stock = max(0.0, item.stock_qty + req.delta)
        item.stock_qty = round(new_stock, 2)
        item.is_available = item.stock_qty > 0
        item.version += 1

        updated = self.store_repo.update_inventory_item(item)
        return self._inventory_to_response(updated)

    def delete_inventory_item(self, owner_id: str, item_id: str) -> None:
        store = self._get_merchant_store(owner_id)
        item = self.store_repo.get_inventory_item_by_id(item_id, store.id)
        if not item:
            raise NotFoundException("Store inventory item not found.")
        self.store_repo.delete_inventory_item(item)

    def update_profile(self, owner_id: str, req: UpdateStoreProfileRequest) -> StoreProfileResponse:
        store = self._get_merchant_store(owner_id)

        # OCC Version check
        if store.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        store.name = req.name
        store.address = req.address
        store.delivery_time = req.delivery_time
        store.delivery_radius = req.delivery_radius
        store.operating_hours = req.operating_hours
        store.version += 1

        updated = self.store_repo.update_store(store)
        return self._store_to_profile(updated)

    def toggle_store_status(self, owner_id: str, req: ToggleStoreStatusRequest) -> StoreProfileResponse:
        store = self._get_merchant_store(owner_id)

        # OCC Version check
        if store.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        store.is_open = not store.is_open
        store.version += 1

        updated = self.store_repo.update_store(store)
        return self._store_to_profile(updated)
