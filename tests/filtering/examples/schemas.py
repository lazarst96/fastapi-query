from datetime import datetime
from typing import Optional, List

from pydantic import Field

from fastapi_query.filtering import BaseFilterParams


class AddressFilters(BaseFilterParams):
    id: Optional[int] = None
    id__not_in: Optional[List[int]] = Field(default=[5, 6])
    line_1__icontains: Optional[str] = None
    city: Optional[str] = None


class OrderFilters(BaseFilterParams):
    id: Optional[int] = None
    id__neq: Optional[int] = None
    amount__lt: Optional[int] = None
    amount__gt: Optional[int] = None


class UserFilters(BaseFilterParams):
    id: Optional[int] = None
    id__in: Optional[List[int]] = Field(default=[1, 2, 3])
    username: Optional[str] = None
    username__contains: Optional[str] = None
    created_at: Optional[datetime] = None
    created_at__gte: Optional[datetime] = None
    created_at__lte: Optional[datetime] = None
    shipping_address_id__isnull: Optional[bool] = Field(default=False)

    shipping_address: Optional[AddressFilters] = None
    billing_address: Optional[AddressFilters] = None
    orders: Optional[OrderFilters] = None
