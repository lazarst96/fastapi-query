from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from fastapi_query.filtering import BaseFilterParams


class BaseResponseModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class CategoryOut(BaseResponseModel):
    name: str


class ProductOut(BaseResponseModel):
    name: str
    price: int
    categories: Optional[List[CategoryOut]]


class AddressOut(BaseResponseModel):
    line_1: str
    line_2: Optional[str]
    city: str
    state: Optional[str]
    country: str
    zip_code: str


class OrderItemOut(BaseResponseModel):
    product: ProductOut
    qty: int


class OrderOut(BaseResponseModel):
    total_amount: int
    shipping_address: Optional[AddressOut]
    items: List[OrderItemOut]


# Filters
class CategoryNestedFilters(BaseFilterParams):
    id: Optional[int] = None
    id__in: Optional[List[int]] = None
    id__nin: Optional[List[int]] = None


class CategoryFilters(CategoryNestedFilters):
    search: Optional[str] = None

    class Settings(CategoryNestedFilters.Settings):
        searchable_fields = ["name"]


class ProductFilters(BaseFilterParams):
    search: Optional[str] = None
    name__ilike: Optional[str] = None
    price__lt: Optional[int] = None
    price__gt: Optional[int] = None

    categories: Optional[CategoryNestedFilters] = None

    class Settings(BaseFilterParams.Settings):
        searchable_fields = ["name", "categories__name"]


class AddressNestedFilters(BaseFilterParams):
    city: Optional[str] = None
    zip_code: Optional[str] = None
    zip_code__in: Optional[List[str]] = None


class OrderItemFilters(BaseFilterParams):
    qty: Optional[int] = None
    product_id: Optional[int] = None


class OrderFilters(BaseFilterParams):
    search: Optional[str] = None
    total_amount__lt: Optional[int] = None
    total_amount__gt: Optional[int] = None

    shipping_address: Optional[AddressNestedFilters] = None
    items: Optional[OrderItemFilters] = None

    class Settings(BaseFilterParams.Settings):
        searchable_fields = ["shipping_address__line_1"]
