from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, func, Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )


product_category_association_table = Table(
    "products__categories",
    Base.metadata,
    Column(
        "product_id",
        ForeignKey("products.id"),
        primary_key=True
    ),
    Column(
        "category_id",
        ForeignKey("categories.id"),
        primary_key=True
    ),
)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]
    categories: Mapped[List[Category]] = relationship(
        secondary=product_category_association_table,
        lazy="noload",
    )


class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    line_1: Mapped[str]
    line_2: Mapped[Optional[str]]
    city: Mapped[str]
    state: Mapped[Optional[str]]
    country: Mapped[str]
    zip_code: Mapped[str]


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[int]
    shipping_address_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="addresses.id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        )
    )

    items: Mapped[List["OrderItem"]] = relationship()
    shipping_address: Mapped[Address] = relationship()


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="orders.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        )
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="products.id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        )
    )
    qty: Mapped[int]

    product: Mapped[Product] = relationship()
