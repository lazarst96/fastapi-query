from typing import Tuple, List

from sqlalchemy.orm import Session

from .models import Category, Product, Address, Order, OrderItem


def _get_data() -> Tuple[
    List[Category],
    List[Product],
    List[Order]
]:
    categories = [
        Category(name="kitchen"),
        Category(name="garden"),
        Category(name="entertainment"),
        Category(name="rest"),
        Category(name="kids"),
        Category(name="car"),
        Category(name="other")
    ]

    products = [
        Product(
            name="Frying Pan",
            price=2000,
            categories=[categories[0]]
        ),
        Product(
            name="Toaster",
            price=3500,
            categories=[categories[0]]
        ),
        Product(
            name="Lazy Bag",
            price=5500,
            categories=[categories[3]]
        ),
        Product(
            name="Table Soccer",
            price=25199,
            categories=[categories[2], categories[4]]
        ),
        Product(
            name="Car Washing Machine",
            price=34399,
            categories=[categories[5]]
        ),
        Product(
            name="Washing Machine",
            price=52999,
            categories=[categories[6]]
        )
    ]

    orders = [
        Order(
            total_amount=4000,
            shipping_address=Address(
                address_line="Main Street 1",
                city="San Diego",
                zip_code="90123",
                state="CA",
                country="US"
            ),
            items=[
                OrderItem(
                    product=products[0],
                    qty=2
                )
            ]
        ),
        Order(
            total_amount=5500,
            shipping_address=Address(
                address_line="Main Street 1",
                city="San Diego",
                zip_code="90123",
                state="CA",
                country="US"
            ),
            items=[
                OrderItem(
                    product=products[0],
                    qty=1
                ),
                OrderItem(
                    product=products[1],
                    qty=1
                )
            ]
        ),
        Order(
            total_amount=30699,
            shipping_address=Address(
                address_line="West Street 1",
                city="San Diego",
                zip_code="90123",
                state="CA",
                country="US"
            ),
            items=[
                OrderItem(
                    product=products[2],
                    qty=1
                ),
                OrderItem(
                    product=products[3],
                    qty=1
                )
            ]
        ),
        Order(
            total_amount=52999,
            shipping_address=Address(
                address_line="Main Street 1",
                city="San Diego",
                zip_code="90123",
                state="CA",
                country="US"
            ),
            items=[
                OrderItem(
                    product=products[5],
                    qty=1
                )
            ]
        ),
    ]

    return categories, products, orders


def seed_db(db: Session) -> None:
    categories, products, orders = _get_data()

    db.add_all([*categories, *products, *orders])
    db.commit()
