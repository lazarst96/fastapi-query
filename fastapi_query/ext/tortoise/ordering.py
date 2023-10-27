from typing import Optional, Type

from tortoise import Model
from tortoise.queryset import QuerySet

from .utils import check_is_model_field_valid


def _check_is_field_valid(
        model_class: Type[Model],
        field: str
) -> bool:
    field_name = field
    model_fields_map = model_class._meta.fields_map  # noqa

    if field.startswith("+") or field.startswith("-"):
        field_name = field[1:]

    return check_is_model_field_valid(
        model_class=model_class,
        field_name=field_name
    )


def apply_ordering(
        queryset: QuerySet,
        order_by: Optional[str]
) -> QuerySet:
    """
    Function for applying order by on the query object

    Parameters:
        queryset (QuerySet): Pre-constructed Select Statement
        order_by (Optional[str]): Comma-separated fields / field-paths

    Returns:
        result_queryset (QuerySet): Result QuerySet
    """

    if not order_by:
        return queryset

    fields = order_by.split(",")

    model_class = queryset.model

    fields = list(
        filter(
            lambda field: _check_is_field_valid(
                model_class=model_class,
                field=field
            ),
            fields
        )
    )

    print(fields)

    return queryset.order_by(*fields)
