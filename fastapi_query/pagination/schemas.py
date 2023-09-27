from typing import TypeVar, Generic, Optional

from pydantic import BaseModel, Field

DataT = TypeVar('DataT')


class PaginatedMeta(BaseModel):
    current_page: int
    items_per_page: int
    total_pages: int
    total_items: int


class Paginated(BaseModel, Generic[DataT]):
    items: list[DataT]
    meta: PaginatedMeta


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=200)
    get_all: bool = Field(default=False)


class LimitOffsetParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
    get_all: bool = Field(default=False)


class CursorParams(BaseModel):
    cursor: Optional[int] = Field(default=None, ge=1)
    size: int = Field(default=50, ge=1, le=200)
    get_all: bool = Field(default=False)
