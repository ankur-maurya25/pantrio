from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.common import PagedResponse
from app.schemas.stores import StoreResponse
from app.services.store_service import StoreService

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("", response_model=PagedResponse[StoreResponse], status_code=status.HTTP_200_OK)
def get_stores(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    filter_query: Optional[str] = Query(None, alias="filter"),
    db: Session = Depends(get_db)
):
    service = StoreService(db)
    return service.get_stores_paginated(page, limit, lat, lng, filter_query)


@router.get("/{store_id}", response_model=StoreResponse, status_code=status.HTTP_200_OK)
def get_store_by_id(
    store_id: str,
    db: Session = Depends(get_db)
):
    service = StoreService(db)
    return service.get_store_by_id(store_id)
