from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.db.models import User, Store, StoreOrder
from app.repositories.user_repository import UserRepository
from app.repositories.store_repository import StoreRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.common import PagedResponse
from app.schemas.admin import (
    PlatformMetricsResponse,
    PlatformUserResponse,
    ToggleUserStatusRequest,
    PlatformStoreResponse,
    UpdateStoreApprovalRequest,
    PlatformOrderResponse
)


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.store_repo = StoreRepository(db)
        self.order_repo = OrderRepository(db)

    def get_metrics(self) -> PlatformMetricsResponse:
        users, total_users = self.user_repo.get_users_paginated(page=1, limit=1000)
        stores, total_stores = self.store_repo.get_stores_paginated(page=1, limit=1000)
        orders, total_orders = self.order_repo.get_all_orders_paginated(page=1, limit=1000)

        verified_stores = sum(1 for s in stores if s.status == "APPROVED")
        pending_stores = sum(1 for s in stores if s.status == "PENDING_APPROVAL")
        revenue_sum = sum(o.total for o in orders if o.status != "CANCELLED")

        return PlatformMetricsResponse(
            total_users=total_users,
            total_stores=verified_stores,
            total_orders_today=total_orders,
            revenue_today=revenue_sum,
            pending_store_approvals=pending_stores
        )

    def get_users_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> PagedResponse[PlatformUserResponse]:
        users, total = self.user_repo.get_users_paginated(page, limit, role, search)
        data = [
            PlatformUserResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                role=u.role,
                joined_at=u.joined_at.strftime("%b %Y") if u.joined_at else "Jan 2026",
                status=u.status,
                activity_metric=u.activity_metric or "0 orders placed",
                version=u.version
            )
            for u in users
        ]
        has_more = (page * limit) < total
        return PagedResponse[PlatformUserResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def toggle_user_status(self, user_id: str, req: ToggleUserStatusRequest) -> PlatformUserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")

        # OCC Version check
        if user.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        user.status = "SUSPENDED" if user.status == "ACTIVE" else "ACTIVE"
        user.version += 1
        updated = self.user_repo.update_user(user)

        return PlatformUserResponse(
            id=updated.id,
            name=updated.name,
            email=updated.email,
            role=updated.role,
            joined_at=updated.joined_at.strftime("%b %Y") if updated.joined_at else "Jan 2026",
            status=updated.status,
            activity_metric=updated.activity_metric or "0 orders placed",
            version=updated.version
        )

    def get_stores_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> PagedResponse[PlatformStoreResponse]:
        stores, total = self.store_repo.get_stores_paginated(
            page=page,
            limit=limit,
            status=status,
            search=search
        )
        data = [
            PlatformStoreResponse(
                id=s.id,
                name=s.name,
                owner_name=s.owner_name,
                category=s.category,
                address=s.address,
                status=s.status,
                orders_fulfilled=s.orders_fulfilled,
                rating=s.rating,
                version=s.version
            )
            for s in stores
        ]
        has_more = (page * limit) < total
        return PagedResponse[PlatformStoreResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def update_store_approval_status(
        self,
        store_id: str,
        req: UpdateStoreApprovalRequest
    ) -> PlatformStoreResponse:
        store = self.store_repo.get_store_by_id(store_id)
        if not store:
            raise NotFoundException("Store not found.")

        # OCC Version check
        if store.version != req.version:
            raise ConflictException("Resource was modified by another request.")

        status_clean = req.status.upper()
        if status_clean not in ["APPROVED", "SUSPENDED", "PENDING_APPROVAL"]:
            raise ValidationException("Invalid store approval status.")

        store.status = status_clean
        store.version += 1
        updated = self.store_repo.update_store(store)

        return PlatformStoreResponse(
            id=updated.id,
            name=updated.name,
            owner_name=updated.owner_name,
            category=updated.category,
            address=updated.address,
            status=updated.status,
            orders_fulfilled=updated.orders_fulfilled,
            rating=updated.rating,
            version=updated.version
        )

    def get_orders_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> PagedResponse[PlatformOrderResponse]:
        orders, total = self.order_repo.get_all_orders_paginated(page, limit, status)
        data = [
            PlatformOrderResponse(
                id=o.id,
                store_id=o.store_id,
                store_name=o.store.name if o.store else "Store",
                customer_name=o.customer_name,
                total=o.total,
                status=o.status,
                placed_at=o.placed_at,
                items_count=len(o.items) if o.items else 1
            )
            for o in orders
        ]
        has_more = (page * limit) < total
        return PagedResponse[PlatformOrderResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )
