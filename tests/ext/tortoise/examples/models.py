from tortoise import fields
from tortoise.models import Model


class TimestampsMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)


class Category(Model, TimestampsMixin):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, index=True)

    class Meta:
        table = "categories"


class Product(Model, TimestampsMixin):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, index=True)
    price = fields.IntField()
    categories: fields.ManyToManyRelation["Category"] = fields.ManyToManyField(
        model_name="models.Category",
        through="products__categories"
    )

    class Meta:
        table = "products"


class Address(Model, TimestampsMixin):
    id = fields.IntField(pk=True)
    line_1 = fields.CharField(max_length=256)
    line_2 = fields.CharField(max_length=256, null=True)
    city = fields.CharField(max_length=256)
    state = fields.CharField(max_length=2, null=True)
    country = fields.CharField(max_length=2)
    zip_code = fields.CharField(max_length=10)

    class Meta:
        table = "addresses"


class Order(Model, TimestampsMixin):
    id = fields.IntField(pk=True)
    total_amount = fields.IntField()
    shipping_address = fields.OneToOneField("models.Address")

    class Meta:
        table = "orders"


class OrderItem(Model, TimestampsMixin):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField("models.Order", related_name="items")
    product = fields.ForeignKeyField("models.Product")
    qty = fields.IntField()

    class Meta:
        table = "order_items"
