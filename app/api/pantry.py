from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.common import PagedResponse
from app.schemas.pantry import (
    PantryItemResponse,
    CreatePantryItemRequest,
    UpdatePantryItemRequest,
    StepPantryQuantityRequest
)
from app.services.pantry_service import PantryService

router = APIRouter(prefix="/pantry", tags=["Pantry"])


@router.get("/items", response_model=PagedResponse[PantryItemResponse], status_code=status.HTTP_200_OK)
def get_pantry_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PantryService(db)
    return service.get_items_paginated(
        user_id=current_user.id,
        page=page,
        limit=limit,
        category=category,
        status=status_filter,
        search=search
    )


@router.post("/items", response_model=PantryItemResponse, status_code=status.HTTP_201_CREATED)
def add_pantry_item(
    req: CreatePantryItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PantryService(db)
    return service.add_item(current_user.id, req)


@router.patch("/items/{item_id}", response_model=PantryItemResponse, status_code=status.HTTP_200_OK)
def update_pantry_item(
    item_id: str,
    req: UpdatePantryItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PantryService(db)
    return service.update_item(current_user.id, item_id, req)


@router.patch("/items/{item_id}/step", response_model=PantryItemResponse, status_code=status.HTTP_200_OK)
def step_pantry_quantity(
    item_id: str,
    req: StepPantryQuantityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PantryService(db)
    return service.step_quantity(current_user.id, item_id, req)


@router.delete("/items/expired", status_code=status.HTTP_204_NO_CONTENT)
def clear_expired_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PantryService(db)
    service.clear_expired_items(current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pantry_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PantryService(db)
    service.delete_item(current_user.id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
