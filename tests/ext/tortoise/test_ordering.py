import pytest
from tortoise.queryset import QuerySet

from fastapi_query.ext.tortoise import apply_ordering
from .examples.models import (
    Category,
    Order
)


@pytest.mark.asyncio
async def test_single() -> None:
    """ Test Ordering - with single criteria"""
    order_by = "-name"

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset = apply_ordering(
        queryset=queryset,
        order_by=order_by
    )

    res = await queryset.all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name


@pytest.mark.asyncio
async def test_nested() -> None:
    """ Test Ordering - with nested criteria"""
    order_by = "-shipping_address__line_1"

    queryset = QuerySet(
        Order
    ).select_related(
        "shipping_address"
    ).filter(
        deleted_at=None
    )

    queryset = apply_ordering(
        queryset=queryset,
        order_by=order_by
    )

    res = await queryset.all()

    for i in range(len(res) - 1):
        assert res[i].shipping_address.line_1 >= res[i + 1].shipping_address.line_1


@pytest.mark.asyncio
async def test_multiple() -> None:
    """ Test Ordering - with multiple criteria"""
    order_by = "-name,-created_at"

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset = apply_ordering(
        queryset=queryset,
        order_by=order_by
    )

    res = await queryset.all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name


@pytest.mark.asyncio
async def test_no_criteria() -> None:
    """ Test Ordering - no criteria"""
    order_by = None

    queryset_before = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset_after = apply_ordering(
        queryset=queryset_before,
        order_by=order_by
    )

    assert queryset_before == queryset_after


@pytest.mark.asyncio
async def test_with_invalid_field() -> None:
    """ Test Ordering - with invalid field"""
    order_by = "-invalid,-name"

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset = apply_ordering(
        queryset=queryset,
        order_by=order_by
    )

    res = await queryset.all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name


@pytest.mark.asyncio
async def test_with_empty_field() -> None:
    """ Test Ordering - with empty field"""
    order_by = "-"

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset = apply_ordering(
        queryset=queryset,
        order_by=order_by
    )

    res = await queryset.all()

    assert len(res) > 0


@pytest.mark.asyncio
async def test_nested_invalid_field() -> None:
    """ Test Ordering - with invalid nested field"""
    order_by = "-name__name,-name"

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset = apply_ordering(
        queryset=queryset,
        order_by=order_by
    )

    res = await queryset.all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name
