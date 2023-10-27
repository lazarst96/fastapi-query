from .models import Category, Product, Address, Order, OrderItem


async def seed_db() -> None:
    category1 = await Category.create(name="kitchen")
    category2 = await Category.create(name="garden")
    category3 = await Category.create(name="entertainment")
    category4 = await Category.create(name="rest")
    category5 = await Category.create(name="kids")
    category6 = await Category.create(name="car")
    category7 = await Category.create(name="other")

    # Products
    product1 = await Product.create(
        name="Frying Pan",
        price=2000
    )
    await product1.categories.add(category1)

    product2 = await Product.create(
        name="Toaster",
        price=3500
    )
    await product2.categories.add(category2)

    product3 = await Product.create(
        name="Lazy Bag",
        price=5500
    )
    await product3.categories.add(category4)

    product4 = await Product.create(
        name="Table Soccer",
        price=25199,
    )
    await product4.categories.add(category3, category5)

    product5 = await Product.create(
        name="Car Washing Machine",
        price=34399,
    )
    await product5.categories.add(category6)

    product6 = await Product.create(
        name="Washing Machine",
        price=52999,
    )
    await product6.categories.add(category7)

    # Orders
    shipping_address1 = await Address.create(
        line_1="Main Street 1",
        city="San Diego",
        zip_code="90123",
        state="CA",
        country="US"
    )
    order1 = await Order.create(
        total_amount=4000,
        shipping_address=shipping_address1
    )
    await OrderItem.create(
        order=order1,
        product=product1,
        qty=2
    )

    shipping_address2 = await Address.create(
        line_1="Main Street 1",
        city="San Diego",
        zip_code="90123",
        state="CA",
        country="US"
    )
    order2 = await Order.create(
        total_amount=5500,
        shipping_address=shipping_address2
    )
    await OrderItem.create(
        order=order2,
        product=product1,
        qty=1
    )
    await OrderItem.create(
        order=order2,
        product=product2,
        qty=1
    )

    shipping_address3 = await Address.create(
        line_1="West Street 1",
        city="San Diego",
        zip_code="90123",
        state="CA",
        country="US"
    )
    order3 = await Order.create(
        total_amount=30699,
        shipping_address=shipping_address3
    )
    await OrderItem.create(
        order=order3,
        product=product3,
        qty=1
    )
    await OrderItem.create(
        order=order3,
        product=product4,
        qty=1
    )

    shipping_address4 = await Address.create(
        line_1="Main Street 1",
        city="San Diego",
        zip_code="90123",
        state="CA",
        country="US"
    )
    order4 = await Order.create(
        total_amount=52999,
        shipping_address=shipping_address4
    )
    await OrderItem.create(
        order=order4,
        product=product6,
        qty=1
    )
