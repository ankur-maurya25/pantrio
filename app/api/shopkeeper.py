from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.api.deps import require_role
from app.db.database import get_db
from app.db.models import User
from app.schemas.common import PagedResponse
from app.schemas.shopkeeper import (
    StoreProfileResponse,
    UpdateStoreProfileRequest,
    ToggleStoreStatusRequest,
    StoreOrderResponse,
    UpdateOrderStatusRequest,
    StoreInventoryItemResponse,
    CreateInventoryItemRequest,
    UpdateInventoryItemRequest,
    StepStockRequest,
    ShopkeeperDashboardResponse
)
from app.services.shopkeeper_service import ShopkeeperService

router = APIRouter(prefix="/shopkeeper", tags=["Shopkeeper"])


@router.get("/dashboard", response_model=ShopkeeperDashboardResponse, status_code=status.HTTP_200_OK)
def get_dashboard(
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.get_dashboard(current_user.id)


@router.get("/orders", response_model=PagedResponse[StoreOrderResponse], status_code=status.HTTP_200_OK)
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.get_orders_paginated(current_user.id, page, limit, status_filter)


@router.patch("/orders/{order_id}/status", response_model=StoreOrderResponse, status_code=status.HTTP_200_OK)
def update_order_status(
    order_id: str,
    req: UpdateOrderStatusRequest,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.update_order_status(current_user.id, order_id, req)


@router.get("/inventory", response_model=PagedResponse[StoreInventoryItemResponse], status_code=status.HTTP_200_OK)
def get_inventory(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.get_inventory_paginated(current_user.id, page, limit, category, search)


@router.post("/inventory", response_model=StoreInventoryItemResponse, status_code=status.HTTP_201_CREATED)
def add_inventory_item(
    req: CreateInventoryItemRequest,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.add_inventory_item(current_user.id, req)


@router.patch("/inventory/{item_id}", response_model=StoreInventoryItemResponse, status_code=status.HTTP_200_OK)
def update_inventory_item(
    item_id: str,
    req: UpdateInventoryItemRequest,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.update_inventory_item(current_user.id, item_id, req)


@router.patch("/inventory/{item_id}/step", response_model=StoreInventoryItemResponse, status_code=status.HTTP_200_OK)
def step_stock_quantity(
    item_id: str,
    req: StepStockRequest,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.step_stock_quantity(current_user.id, item_id, req)


@router.delete("/inventory/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    item_id: str,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    service.delete_inventory_item(current_user.id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/profile", response_model=StoreProfileResponse, status_code=status.HTTP_200_OK)
def update_profile(
    req: UpdateStoreProfileRequest,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.update_profile(current_user.id, req)


@router.patch("/status", response_model=StoreProfileResponse, status_code=status.HTTP_200_OK)
def toggle_store_status(
    req: ToggleStoreStatusRequest,
    current_user: User = Depends(require_role("SHOPKEEPER")),
    db: Session = Depends(get_db)
):
    service = ShopkeeperService(db)
    return service.toggle_store_status(current_user.id, req)
