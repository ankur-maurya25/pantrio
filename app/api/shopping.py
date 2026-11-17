from typing import List
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.common import PagedResponse
from app.schemas.shopping import (
    ShoppingItemResponse,
    CreateShoppingItemRequest,
    ToggleShoppingItemRequest,
    BulkDeleteShoppingItemsRequest
)
from app.services.shopping_service import ShoppingService

router = APIRouter(prefix="/shopping", tags=["Shopping"])


@router.get("/items", response_model=PagedResponse[ShoppingItemResponse], status_code=status.HTTP_200_OK)
def get_shopping_items(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ShoppingService(db)
    return service.get_items_paginated(current_user.id, page, limit)


@router.post("/items", response_model=ShoppingItemResponse, status_code=status.HTTP_201_CREATED)
def add_shopping_item(
    req: CreateShoppingItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ShoppingService(db)
    return service.add_item(current_user.id, req)


@router.post("/items/bulk", response_model=List[ShoppingItemResponse], status_code=status.HTTP_201_CREATED)
def add_shopping_items_bulk(
    reqs: List[CreateShoppingItemRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ShoppingService(db)
    return service.add_items_bulk(current_user.id, reqs)


@router.patch("/items/{item_id}/toggle", response_model=ShoppingItemResponse, status_code=status.HTTP_200_OK)
def toggle_shopping_item(
    item_id: str,
    req: ToggleShoppingItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ShoppingService(db)
    return service.toggle_item(current_user.id, item_id, req)


@router.delete("/items/bulk", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_items_bulk(
    req: BulkDeleteShoppingItemsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ShoppingService(db)
    service.delete_items_bulk(current_user.id, req)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ShoppingService(db)
    service.delete_item(current_user.id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
