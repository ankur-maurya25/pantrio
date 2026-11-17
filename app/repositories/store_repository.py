from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import Store, StoreInventory, Recipe


class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    # Stores
    def get_store_by_id(self, store_id: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.id == store_id).first()

    def get_store_by_owner_id(self, owner_id: str) -> Optional[Store]:
        return self.db.query(Store).filter(Store.owner_id == owner_id).first()

    def get_stores_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Store], int]:
        query = self.db.query(Store)
        if status:
            query = query.filter(Store.status == status.upper())
        if category:
            query = query.filter(Store.category.ilike(f"%{category}%"))
        if search:
            query = query.filter(Store.name.ilike(f"%{search}%") | Store.address.ilike(f"%{search}%"))

        total = query.count()
        offset = (page - 1) * limit
        stores = query.order_by(Store.created_at.desc()).offset(offset).limit(limit).all()
        return stores, total

    def create_store(self, store: Store) -> Store:
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def update_store(self, store: Store) -> Store:
        self.db.commit()
        self.db.refresh(store)
        return store

    # Inventory
    def get_inventory_item_by_id(self, item_id: str, store_id: Optional[str] = None) -> Optional[StoreInventory]:
        query = self.db.query(StoreInventory).filter(StoreInventory.id == item_id)
        if store_id:
            query = query.filter(StoreInventory.store_id == store_id)
        return query.first()

    def get_inventory_paginated(
        self,
        store_id: str,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[StoreInventory], int]:
        query = self.db.query(StoreInventory).filter(StoreInventory.store_id == store_id)
        if category:
            query = query.filter(StoreInventory.category.ilike(f"%{category}%"))
        if search:
            query = query.filter(StoreInventory.name.ilike(f"%{search}%"))

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(StoreInventory.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def create_inventory_item(self, item: StoreInventory) -> StoreInventory:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_inventory_item(self, item: StoreInventory) -> StoreInventory:
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_inventory_item(self, item: StoreInventory) -> None:
        self.db.delete(item)
        self.db.commit()

    # Recipes
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

    def get_recipes_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[Recipe], int]:
        query = self.db.query(Recipe)
        if search:
            query = query.filter(Recipe.title.ilike(f"%{search}%"))

        total = query.count()
        offset = (page - 1) * limit
        recipes = query.order_by(Recipe.created_at.desc()).offset(offset).limit(limit).all()
        return recipes, total

    def create_recipe(self, recipe: Recipe) -> Recipe:
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe
