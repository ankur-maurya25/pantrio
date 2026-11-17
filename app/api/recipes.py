from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.common import PagedResponse
from app.schemas.recipes import RecipeResponse
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("", response_model=PagedResponse[RecipeResponse], status_code=status.HTTP_200_OK)
def get_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = RecipeService(db)
    return service.get_recipes_paginated(page, limit, search)


@router.get("/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK)
def get_recipe_by_id(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    service = RecipeService(db)
    return service.get_recipe_by_id(recipe_id)
