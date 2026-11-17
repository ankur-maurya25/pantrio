from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import require_role
from app.db.database import get_db
from app.db.models import User
from app.schemas.common import PagedResponse
from app.schemas.admin import (
    PlatformMetricsResponse,
    PlatformUserResponse,
    ToggleUserStatusRequest,
    PlatformStoreResponse,
    UpdateStoreApprovalRequest,
    PlatformOrderResponse
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics", response_model=PlatformMetricsResponse, status_code=status.HTTP_200_OK)
def get_metrics(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_metrics()


@router.get("/users", response_model=PagedResponse[PlatformUserResponse], status_code=status.HTTP_200_OK)
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_users_paginated(page, limit, role, search)


@router.patch("/users/{user_id}/status", response_model=PlatformUserResponse, status_code=status.HTTP_200_OK)
def toggle_user_status(
    user_id: str,
    req: ToggleUserStatusRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.toggle_user_status(user_id, req)


@router.get("/stores", response_model=PagedResponse[PlatformStoreResponse], status_code=status.HTTP_200_OK)
def get_stores(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_stores_paginated(page, limit, status_filter, search)


@router.patch("/stores/{store_id}/status", response_model=PlatformStoreResponse, status_code=status.HTTP_200_OK)
def update_store_approval_status(
    store_id: str,
    req: UpdateStoreApprovalRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.update_store_approval_status(store_id, req)


@router.get("/orders", response_model=PagedResponse[PlatformOrderResponse], status_code=status.HTTP_200_OK)
def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    return service.get_orders_paginated(page, limit, status_filter)
