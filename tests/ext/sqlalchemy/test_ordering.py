from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from fastapi_query.ext.sqlalchemy import apply_ordering
from .examples.models import (
    Category,
    Order
)


def test_single(db: Session) -> None:
    """ Test Ordering - with single criteria"""
    order_by = "-name"

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt = apply_ordering(
        model_class=Category,
        stmt=stmt,
        order_by=order_by
    )

    res = db.scalars(stmt).all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name


def test_nested(db: Session) -> None:
    """ Test Ordering - with nested criteria"""
    order_by = "-shipping_address__line_1"

    stmt = select(
        Order
    ).join(
        Order.shipping_address
    ).options(
        contains_eager(Order.shipping_address)
    ).where(
        Order.deleted_at.is_(None)
    )

    stmt = apply_ordering(
        model_class=Order,
        stmt=stmt,
        order_by=order_by
    )

    res = db.scalars(stmt).all()

    for i in range(len(res) - 1):
        assert res[i].shipping_address.line_1 >= res[i + 1].shipping_address.line_1


def test_multiple(db: Session) -> None:
    """ Test Ordering - with multiple criteria"""
    order_by = "-name,-created_at"

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt = apply_ordering(
        model_class=Category,
        stmt=stmt,
        order_by=order_by
    )

    res = db.scalars(stmt).all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name


def test_no_criteria(db: Session) -> None:
    """ Test Ordering - no criteria"""
    order_by = None

    stmt_before = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt_after = apply_ordering(
        model_class=Category,
        stmt=stmt_before,
        order_by=order_by
    )

    assert stmt_before == stmt_after


def test_with_invalid_field(db: Session) -> None:
    """ Test Ordering - with invalid field"""
    order_by = "-invalid,-name"

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt = apply_ordering(
        model_class=Category,
        stmt=stmt,
        order_by=order_by
    )

    res = db.scalars(stmt).all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name


def test_with_empty_field(db: Session) -> None:
    """ Test Ordering - with empty field"""
    order_by = "-"

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt = apply_ordering(
        model_class=Category,
        stmt=stmt,
        order_by=order_by
    )

    res = db.scalars(stmt).all()

    assert len(res) > 0


def test_nested_invalid_field(db: Session) -> None:
    """ Test Ordering - with invalid nested field"""
    order_by = "-name__name,-name"

    stmt = select(
        Category
    ).where(
        Category.deleted_at.is_(None)
    )

    stmt = apply_ordering(
        model_class=Category,
        stmt=stmt,
        order_by=order_by
    )

    res = db.scalars(stmt).all()

    for i in range(len(res) - 1):
        assert res[i].name >= res[i + 1].name
