from typing import List
from app.schemas.common import CamelModel


class RecipeResponse(CamelModel):
    id: str
    title: str
    duration: str
    calories: str
    difficulty: str
    match_percentage: int = 100
    tags: List[str] = []
    ingredients: List[str] = []
    instructions: List[str] = []
    image_url: str = ""
