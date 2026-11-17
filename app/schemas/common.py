from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    components = string.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


T = TypeVar("T")


class PagedResponse(CamelModel, Generic[T]):
    data: List[T] = []
    page: int = 1
    limit: int = 20
    total: int = 0
    has_more: bool = False


class ErrorDetail(CamelModel):
    code: str
    message: str


class ErrorResponse(CamelModel):
    error: ErrorDetail


class SuccessResponse(CamelModel):
    success: bool = True
