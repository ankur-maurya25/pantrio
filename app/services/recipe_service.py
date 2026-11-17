from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.db.models import Recipe
from app.repositories.store_repository import StoreRepository
from app.schemas.common import PagedResponse
from app.schemas.recipes import RecipeResponse


class RecipeService:
    def __init__(self, db: Session):
        self.db = db
        self.store_repo = StoreRepository(db)

    def _to_response(self, recipe: Recipe) -> RecipeResponse:
        return RecipeResponse(
            id=recipe.id,
            title=recipe.title,
            duration=recipe.duration,
            calories=recipe.calories,
            difficulty=recipe.difficulty,
            match_percentage=recipe.match_percentage,
            tags=recipe.tags if isinstance(recipe.tags, list) else [],
            ingredients=recipe.ingredients if isinstance(recipe.ingredients, list) else [],
            instructions=recipe.instructions if isinstance(recipe.instructions, list) else [],
            image_url=recipe.image_url or ""
        )

    def get_recipes_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> PagedResponse[RecipeResponse]:
        recipes, total = self.store_repo.get_recipes_paginated(page, limit, search)
        data = [self._to_response(r) for r in recipes]
        has_more = (page * limit) < total
        return PagedResponse[RecipeResponse](
            data=data,
            page=page,
            limit=limit,
            total=total,
            has_more=has_more
        )

    def get_recipe_by_id(self, recipe_id: str) -> RecipeResponse:
        recipe = self.store_repo.get_recipe_by_id(recipe_id)
        if not recipe:
            raise NotFoundException("Recipe not found.")
        return self._to_response(recipe)
