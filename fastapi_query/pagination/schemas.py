from typing import TypeVar, Generic, List

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class PaginatedMeta(BaseModel):
    current_page: int
    items_per_page: int
    total_pages: int
    total_items: int


class Paginated(BaseModel, Generic[DataT]):
    items: List[DataT]
    meta: PaginatedMeta


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=200)
    get_all: bool = Field(default=False)
