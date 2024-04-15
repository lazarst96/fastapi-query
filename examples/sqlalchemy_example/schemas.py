from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from fastapi_query.filtering import BaseFilterParams


class NestedPaperFilters(BaseFilterParams):
    id: Optional[int] = None


class TagFilters(BaseFilterParams):
    id: Optional[int] = None
    id__in: Optional[List[int]] = None
    name: Optional[str] = None
    name__icontains: Optional[str] = None

    papers: Optional[NestedPaperFilters] = None


class UserFilters(BaseFilterParams):
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    first_name__icontains: Optional[str] = None
    last_name: Optional[str] = None
    last_name__icontains: Optional[str] = None
    email: Optional[str] = None
    email__contains: Optional[str] = None
    deleted_at__isnull: Optional[bool] = None
    deleted_at__gte: Optional[datetime] = None

    tags: Optional[TagFilters] = None

    class Settings(BaseFilterParams.Settings):
        searchable_fields = ["full_name", "email", "tags__name"]


class PaperFilters(BaseFilterParams):
    title__icontains: Optional[str] = None
    author_id: Optional[int] = None
    author_id__neq: Optional[int] = None
    author_id__not_in: Optional[List[int]] = None

    tags: Optional[TagFilters] = None


class TagOut(BaseModel):
    id: int
    name: str


class AddressOut(BaseModel):
    id: int
    line_1: str
    line_2: Optional[str] = None
    city: str
    zip_code: str
    country: str


class UserNestedOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UserOut(UserNestedOut):
    tags: List[TagOut]
    shipping_address: Optional[AddressOut]
    billing_address: Optional[AddressOut]


class PaperOut(BaseModel):
    id: int
    title: str

    author: Optional[UserNestedOut] = None
    tags: List[TagOut]
