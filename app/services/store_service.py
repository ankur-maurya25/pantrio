from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.db.models import Store, CustomerLocation
from app.repositories.store_repository import StoreRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PagedResponse
from app.schemas.customer import CustomerLocationDto
from app.schemas.stores import StoreResponse


class StoreService:
    def __init__(self, db: Session):
        self.db = db
        self.store_repo = StoreRepository(db)
        self.user_repo = UserRepository(db)

    def _to_response(self, store: Store) -> StoreResponse:
        return StoreResponse(
            id=store.id,
            name=store.name,
            category=store.category,
            delivery_time=store.delivery_time,
            rating=store.rating,
            orders_fulfilled=store.orders_fulfilled,
            delivery_fee=store.delivery_fee,
            is_open=store.is_open,
            address=store.address or "",
            lat=store.lat,
            lng=store.lng
        )

    def get_stores_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        filter_str: Optional[str] = None
    ) -> PagedResponse[StoreResponse]:
        stores, total = self.store_repo.get_stores_paginated(
            page=page,
            limit=limit,
            category=filter_str,
            search=filter_str,
            status="APPROVED"
        )
        data = [self._to_response(s) for s in stores]
        has_more = (page * limit) < total
        return PagedResponse[StoreResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def get_store_by_id(self, store_id: str) -> StoreResponse:
        store = self.store_repo.get_store_by_id(store_id)
        if not store:
            raise NotFoundException("Store not found.")
        return self._to_response(store)

    # Customer location
    def get_customer_location(self, user_id: str) -> CustomerLocationDto:
        loc = self.user_repo.get_customer_location(user_id)
        if not loc:
            return CustomerLocationDto(address="Indiranagar, Bangalore", lat=12.9784, lng=77.6408)
        return CustomerLocationDto(address=loc.address, lat=loc.lat, lng=loc.lng)

    def update_customer_location(self, user_id: str, req: CustomerLocationDto) -> CustomerLocationDto:
        loc = self.user_repo.get_customer_location(user_id)
        if loc:
            loc.address = req.address
            loc.lat = req.lat
            loc.lng = req.lng
            loc.updated_at = datetime.now(timezone.utc)
            self.user_repo.save_customer_location(loc)
        else:
            loc = CustomerLocation(
                user_id=user_id,
                address=req.address,
                lat=req.lat,
                lng=req.lng
            )
            self.user_repo.save_customer_location(loc)
        return CustomerLocationDto(address=loc.address, lat=loc.lat, lng=loc.lng)
