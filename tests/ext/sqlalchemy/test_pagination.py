import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_query.ext.sqlalchemy import paginate, paginate_async
from fastapi_query.pagination import PaginationParams
from .examples.models import (
    Product,
    Category
)
from .examples.schemas import (
    ProductFilters
)


def test_basic_category(db: Session) -> None:
    """ Test Pagination - Basic"""

    params = PaginationParams(
        page=1,
        size=20,
        get_all=False
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    res = paginate(
        db=db,
        stmt=stmt,
        pagination_params=params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == params.page
    assert meta["items_per_page"] == params.size
    assert meta["total_pages"] == 1
    assert meta["total_items"] == 7
    assert len(items) == 7


def test_basic_category_with_get_all(db: Session) -> None:
    """ Test Pagination - Basic with get_all Option"""

    params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    res = paginate(
        db=db,
        stmt=stmt,
        pagination_params=params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == 1
    assert meta["items_per_page"] == meta["total_items"]
    assert meta["total_pages"] == 1
    assert len(items) == meta["total_items"]


def test_product_with_filters(db: Session) -> None:
    """ Test Pagination - Basic with filters"""
    filter_params = ProductFilters(
        name__ilike="pan",
        price__lt=3000,
        price__gt=1500,
    )

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Product
    ).where(
        Product.deleted_at.is_(None)
    )

    res = paginate(
        db=db,
        stmt=stmt,
        model_class=Product,
        pagination_params=pagination_params,
        filter_params=filter_params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == 1
    assert meta["items_per_page"] == meta["total_items"]
    assert meta["total_pages"] == 1
    assert len(items) == meta["total_items"]


def test_product_with_ordering(db: Session) -> None:
    """ Test Pagination - Basic with ordering"""
    ordering_params = "-name"

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Product
    ).where(
        Product.deleted_at.is_(None)
    )

    res = paginate(
        db=db,
        stmt=stmt,
        model_class=Product,
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


def test_missing_model_class(db: Session) -> None:
    """ Test Pagination - Basic with filters"""
    filter_params = ProductFilters(
        name__ilike="pan",
        price__lt=3000,
        price__gt=1500,
    )

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Product
    ).where(
        Product.deleted_at.is_(None)
    )

    exception_occurred = False

    try:
        _ = paginate(
            db=db,
            stmt=stmt,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


@pytest.mark.asyncio
async def test_async_basic(async_db: AsyncSession) -> None:
    """ Test Async Pagination - Basic"""

    params = PaginationParams(
        page=1,
        size=20,
        get_all=False
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    res = await paginate_async(
        db=async_db,
        stmt=stmt,
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
async def test_async_basic_with_get_all(async_db: AsyncSession) -> None:
    """ Test Async Pagination - Basic with get_all"""

    params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    res = await paginate_async(
        db=async_db,
        stmt=stmt,
        pagination_params=params
    )

    meta = res["meta"]
    items = res["items"]

    assert meta["current_page"] == 1
    assert meta["items_per_page"] == meta["total_items"]
    assert meta["total_pages"] == 1
    assert len(items) == meta["total_items"]


@pytest.mark.asyncio
async def test_async_with_filters(async_db: AsyncSession) -> None:
    """ Test Async Pagination - Basic with filters"""
    filter_params = ProductFilters(
        name__ilike="pan",
        price__lt=3000,
        price__gt=1500,
    )

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Product
    ).where(
        Product.deleted_at.is_(None)
    )

    res = await paginate_async(
        db=async_db,
        stmt=stmt,
        model_class=Product,
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
async def test_async_with_ordering(async_db: AsyncSession) -> None:
    """ Test Async Pagination - Basic with ordering"""
    ordering_params = "-name"

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Product
    ).where(
        Product.deleted_at.is_(None)
    )

    res = await paginate_async(
        db=async_db,
        stmt=stmt,
        model_class=Product,
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


@pytest.mark.asyncio
async def test_async_with_missing_model_class(async_db: AsyncSession) -> None:
    """ Test Async Pagination - Basic with filters"""
    filter_params = ProductFilters(
        name__ilike="pan",
        price__lt=3000,
        price__gt=1500,
    )

    pagination_params = PaginationParams(
        page=1,
        size=20,
        get_all=True
    )

    stmt = select(
        Product
    ).where(
        Product.deleted_at.is_(None)
    )

    exception_occurred = False

    try:
        _ = await paginate_async(
            db=async_db,
            stmt=stmt,
            pagination_params=pagination_params,
            filter_params=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred
