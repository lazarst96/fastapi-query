import pytest
from tortoise.queryset import QuerySet

from fastapi_query.ext.tortoise import paginate
from fastapi_query.pagination import PaginationParams
from .examples.models import (
    Product,
    Category
)
from .examples.schemas import (
    ProductFilters
)


@pytest.mark.asyncio
async def test_async_basic() -> None:
    """ Test Async Pagination - Basic"""

    params = PaginationParams(
        page=1,
        size=20,
        get_all=False
    )

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    res = await paginate(
        queryset=queryset,
        pagination_params=params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == params.page
    assert meta["items_per_page"] == params.size
    assert meta["total_pages"] == 1
    assert meta["total_items"] == 7
    assert len(items) == 7


@pytest.mark.asyncio
async def test_async_basic_with_get_all() -> None:
    """ Test Async Pagination - Basic with get_all"""

    params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    res = await paginate(
        queryset=queryset,
        pagination_params=params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == 1
    assert meta["items_per_page"] == meta["total_items"]
    assert meta["total_pages"] == 1
    assert len(items) == meta["total_items"]


@pytest.mark.asyncio
async def test_async_with_filters() -> None:
    """ Test Async Pagination - Basic with filters"""
    filter_params = ProductFilters(
        name__icontains="pan",
        price__lt=3000,
        price__gt=1500,
    )

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    queryset = QuerySet(
        Product
    ).filter(
        deleted_at=None
    )

    res = await paginate(
        queryset=queryset,
        pagination_params=pagination_params,
        filter_params=filter_params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == 1
    assert meta["items_per_page"] == meta["total_items"]
    assert meta["total_pages"] == 1
    assert len(items) == meta["total_items"]


@pytest.mark.asyncio
async def test_async_with_ordering() -> None:
    """ Test Async Pagination - Basic with ordering"""
    ordering_params = "-name"

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    queryset = QuerySet(
        Product
    ).filter(
        deleted_at=None
    )

    res = await paginate(
        queryset=queryset,
        pagination_params=pagination_params,
        ordering_params=ordering_params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == 1
    assert meta["items_per_page"] == meta["total_items"]
    assert meta["total_pages"] == 1
    assert len(items) == meta["total_items"]

    for i in range(len(items) - 1):
        assert items[i].name >= items[i + 1].name
