import pytest
from tortoise.queryset import QuerySet

from fastapi_query.ext.tortoise import apply_filters
from fastapi_query.filtering import BaseFilterParams
from .examples.models import (
    Product,
    Order,
    Category
)
from .examples.schemas import (
    ProductFilters,
    OrderFilters,
    AddressNestedFilters,
    CategoryFilters
)


@pytest.mark.asyncio
async def test_category_filters() -> None:
    """ Test Filtering - with Category filters"""
    filter_params = CategoryFilters(
        search="kit"
    )

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset = apply_filters(
        queryset=queryset,
        filters=filter_params
    )

    res = await queryset.all()

    assert len(res) == 1
    assert res[0].name == "kitchen"


@pytest.mark.asyncio
async def test_product_filters() -> None:
    """ Test Filtering - with Product filters"""
    filter_params = ProductFilters(
        name__icontains="pan",
        price__lt=3000,
        price__gt=1500,
    )

    queryset = QuerySet(
        Product
    ).prefetch_related(
        "categories"
    ).filter(
        deleted_at=None
    )

    queryset = apply_filters(
        queryset=queryset,
        filters=filter_params
    )

    res = await queryset.all()

    assert len(res) == 1
    assert res[0].name == "Frying Pan"


@pytest.mark.asyncio
async def test_product_filters_and_search() -> None:
    """ Test Filtering - with Product filters and search"""
    filter_params = ProductFilters(
        search="pan",
        price__lt=3000,
        price__gt=1500,
    )

    queryset = QuerySet(
        Product
    ).prefetch_related(
        "categories"
    ).filter(
        deleted_at=None
    )

    queryset = apply_filters(
        queryset=queryset,
        filters=filter_params
    )

    res = await queryset.all()

    assert len(res) == 1
    assert res[0].name == "Frying Pan"


@pytest.mark.asyncio
async def test_order_filters() -> None:
    """ Test Filtering - with Order filters"""
    filter_params = OrderFilters(
        shipping_address=AddressNestedFilters(
            zip_code="92223"
        ),
        total_amount__gt=1000
    )

    queryset = QuerySet(
        Order
    ).prefetch_related(
        "items", "items__product"
    ).filter(
        deleted_at=None
    )

    queryset = apply_filters(
        queryset=queryset,
        filters=filter_params
    )

    res = await queryset.all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_order_filters_and_search() -> None:
    """ Test Filtering - with Order filters and Search"""
    filter_params = OrderFilters(
        search="west"
    )

    queryset = QuerySet(
        Order
    ).prefetch_related(
        "items", "items__product"
    ).filter(
        deleted_at=None
    )

    queryset = apply_filters(
        queryset=queryset,
        filters=filter_params
    )

    res = await queryset.all()

    assert len(res) == 1


@pytest.mark.asyncio
async def test_invalid_field() -> None:
    """ Test Filtering - Invalid Field"""

    class CategoryInvalidFilters(BaseFilterParams):
        invalid: int

    filter_params = CategoryInvalidFilters(
        invalid=1
    )

    exception_occurred = False

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    try:
        _ = apply_filters(
            queryset=queryset,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


@pytest.mark.asyncio
async def test_invalid_relationship_value_shape() -> None:
    """ Test Filtering - Invalid Relationship Filter Shape"""

    class ProductInvalidFilters(BaseFilterParams):
        categories: str

    filter_params = ProductInvalidFilters(
        categories="test"
    )

    exception_occurred = False

    queryset = QuerySet(
        Product
    ).prefetch_related(
        "categories"
    ).filter(
        deleted_at=None
    )

    try:
        _ = apply_filters(
            queryset=queryset,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


@pytest.mark.asyncio
async def test_invalid_filter_operator() -> None:
    """ Test Filtering - Invalid Operator"""

    class CategoryInvalidFilters(BaseFilterParams):
        id__invalid: int

    filter_params = CategoryInvalidFilters(
        id__invalid=1
    )

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    exception_occurred = False

    try:
        _ = apply_filters(
            queryset=queryset,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


@pytest.mark.asyncio
async def test_no_valid_searchable_field() -> None:
    """ Test Filtering - No Valid Searchable Field"""

    class CategoryInvalidFilters(BaseFilterParams):
        search: str

        class Settings(BaseFilterParams.Settings):
            searchable_fields = ["invalid"]

    filter_params = CategoryInvalidFilters(
        search="test"
    )

    queryset = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    exception_occurred = False

    try:
        _ = apply_filters(
            queryset=queryset,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


@pytest.mark.asyncio
async def test_search_with_empty_searchable_field() -> None:
    """ Test Filtering - No Valid Searchable Field"""

    class CategoryInvalidFilters(BaseFilterParams):
        search: str

        class Settings(BaseFilterParams.Settings):
            searchable_fields = []

    filter_params = CategoryInvalidFilters(
        search="test"
    )

    queryset_before = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset_after = apply_filters(
        queryset=queryset_before,
        filters=filter_params
    )

    res = await queryset_after.all()

    assert len(res) == 7
    assert queryset_before == queryset_after


@pytest.mark.asyncio
async def test_no_filters() -> None:
    """ Test Filtering - No Filters"""

    queryset_before = QuerySet(
        Category
    ).filter(
        deleted_at=None
    )

    queryset_after = apply_filters(
        queryset=queryset_before,
        filters=None
    )

    assert queryset_before == queryset_after
