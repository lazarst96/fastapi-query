from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, joinedload

from fastapi_query.ext.sqlalchemy import apply_filters
from fastapi_query.filtering import BaseFilterParams
from .examples.models import (
    Product,
    Order,
    OrderItem,
    Category
)
from .examples.schemas import (
    ProductFilters,
    OrderFilters,
    AddressNestedFilters,
    CategoryFilters
)


def test_category_filters(db: Session) -> None:
    """ Test Filtering - with Category filters"""
    filter_params = CategoryFilters(
        search="kit"
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt = apply_filters(
        model_class=Category,
        stmt=stmt,
        filters=filter_params
    )

    res = db.scalars(stmt).all()

    assert len(res) == 1
    assert res[0].name == "kitchen"


def test_product_filters(db: Session) -> None:
    """ Test Filtering - with Product filters"""
    filter_params = ProductFilters(
        name__icontains="pan",
        price__lt=3000,
        price__gt=1500,
    )

    stmt = select(
        Product
    ).options(
        selectinload(Product.categories)
    ).where(
        Product.deleted_at.is_(None)
    )

    stmt = apply_filters(
        model_class=Product,
        stmt=stmt,
        filters=filter_params
    )

    res = db.scalars(stmt).all()

    assert len(res) == 1
    assert res[0].name == "Frying Pan"


def test_product_filters_and_search(db: Session) -> None:
    """ Test Filtering - with Product filters and search"""
    filter_params = ProductFilters(
        search="pan",
        price__lt=3000,
        price__gt=1500,
    )

    stmt = select(
        Product
    ).options(
        selectinload(Product.categories)
    ).where(
        Product.deleted_at.is_(None)
    )

    stmt = apply_filters(
        model_class=Product,
        stmt=stmt,
        filters=filter_params
    )

    res = db.scalars(stmt).all()

    assert len(res) == 1
    assert res[0].name == "Frying Pan"


def test_order_filters(db: Session) -> None:
    """ Test Filtering - with Order filters"""
    filter_params = OrderFilters(
        shipping_address=AddressNestedFilters(
            full_address_icontains="92223",
            zip_code="92223"
        ),
        total_amount__gt=1000
    )

    stmt = select(
        Order
    ).options(
        joinedload(Order.shipping_address),
        selectinload(Order.items).joinedload(OrderItem.product)
    ).where(
        Order.deleted_at.is_(None)
    )

    stmt = apply_filters(
        model_class=Order,
        stmt=stmt,
        filters=filter_params
    )

    res = db.scalars(stmt).all()

    assert len(res) == 0


def test_order_filters_and_search(db: Session) -> None:
    """ Test Filtering - with Order filters and Search"""
    filter_params = OrderFilters(
        search="west"
    )

    stmt = select(
        Order
    ).options(
        joinedload(Order.shipping_address),
        selectinload(Order.items).joinedload(OrderItem.product)
    ).where(
        Order.deleted_at.is_(None)
    )

    stmt = apply_filters(
        model_class=Order,
        stmt=stmt,
        filters=filter_params
    )

    res = db.scalars(stmt).all()

    assert len(res) == 1


def test_invalid_field(db: Session) -> None:
    """ Test Filtering - Invalid Field"""

    class CategoryInvalidFilters(BaseFilterParams):
        invalid: int

    filter_params = CategoryInvalidFilters(
        invalid=1
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    exception_occurred = False

    try:
        apply_filters(
            model_class=Category,
            stmt=stmt,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


def test_invalid_relationship_value_shape(db: Session) -> None:
    """ Test Filtering - Invalid Relationship Filter Shape"""

    class ProductInvalidFilters(BaseFilterParams):
        categories: str

    filter_params = ProductInvalidFilters(
        categories="test"
    )

    exception_occurred = False

    stmt = select(
        Order
    ).options(
        joinedload(Order.shipping_address),
        selectinload(Order.items).joinedload(OrderItem.product)
    ).where(
        Order.deleted_at.is_(None)
    )

    try:
        _ = apply_filters(
            model_class=Order,
            stmt=stmt,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


def test_invalid_filter_operator(db: Session) -> None:
    """ Test Filtering - Invalid Operator"""

    class CategoryInvalidFilters(BaseFilterParams):
        id__invalid: int

    filter_params = CategoryInvalidFilters(
        id__invalid=1
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    exception_occurred = False

    try:
        apply_filters(
            model_class=Category,
            stmt=stmt,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


def test_no_valid_searchable_field(db: Session) -> None:
    """ Test Filtering - No Valid Searchable Field"""

    class CategoryInvalidFilters(BaseFilterParams):
        search: str

        class Settings(BaseFilterParams.Settings):
            searchable_fields = ["invalid"]

    filter_params = CategoryInvalidFilters(
        search="test"
    )

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    exception_occurred = False

    try:
        apply_filters(
            model_class=Category,
            stmt=stmt,
            filters=filter_params
        )
    except ValueError:
        exception_occurred = True

    assert exception_occurred


def test_search_with_empty_searchable_field(db: Session) -> None:
    """ Test Filtering - No Valid Searchable Field"""

    class CategoryInvalidFilters(BaseFilterParams):
        search: str

        class Settings(BaseFilterParams.Settings):
            searchable_fields = []

    filter_params = CategoryInvalidFilters(
        search="test"
    )

    stmt_before = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt_after = apply_filters(
        model_class=Category,
        stmt=stmt_before,
        filters=filter_params
    )

    res = db.scalars(stmt_after).all()

    assert len(res) == 7
    assert stmt_before == stmt_after


def test_no_filters(db: Session) -> None:
    """ Test Filtering - No Filters"""

    stmt_before = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt_after = apply_filters(
        model_class=Category,
        stmt=stmt_before,
        filters=None
    )

    assert stmt_before == stmt_after
