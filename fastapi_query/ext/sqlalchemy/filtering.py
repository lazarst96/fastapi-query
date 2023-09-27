from typing import Any, Dict

from sqlalchemy import Select, and_, Column
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Relationship

from fastapi_query.filtering import BaseFilterParams


def _backward_compatible_value_for_like_and_ilike(value: str) -> str:
    """Add % if not in value to be backward compatible.

    Args:
        value (str): The value to filter.

    Returns:
        Either the unmodified value if a percent sign is present, the value wrapped in % otherwise to preserve
        current behavior.
    """
    if "%" not in value:
        value = f"%{value}%"
    return value


_orm_operator_transformer = {
    "neq": lambda value: ("__ne__", value),
    "gt": lambda value: ("__gt__", value),
    "gte": lambda value: ("__ge__", value),
    "in": lambda value: ("in_", value),
    "isnull": lambda value: ("is_", None) if value is True else ("is_not", None),
    "lt": lambda value: ("__lt__", value),
    "lte": lambda value: ("__le__", value),
    "like": lambda value: ("like", _backward_compatible_value_for_like_and_ilike(value)),
    "ilike": lambda value: ("ilike", _backward_compatible_value_for_like_and_ilike(value)),
    "not": lambda value: ("is_not", value),
    "not_in": lambda value: ("not_in", value)
}


def _get_orm_filters(
        model_class: Any,
        filters: BaseFilterParams
):
    columns: Dict[str, Column] = dict(inspect(model_class).columns)
    relationships: Dict[str, Relationship] = dict(inspect(model_class).relationships)

    res = []
    filter_fields = filters.model_dump(exclude_none=True)

    for field_name, value in filter_fields.items():
        if "__" in field_name:
            parts = field_name.split("__")
            field_name, operator = "__".join(parts[:-1]), parts[-1]
            operator, value = _orm_operator_transformer[operator](value)
        else:
            operator = "__eq__"

        if field_name in columns:
            model_field = getattr(model_class, field_name)
            res.append(getattr(model_field, operator)(value))

        elif value and field_name in relationships and relationships[field_name]:

            is_many = relationships[field_name].uselist
            nested_orm_filters = _get_orm_filters(
                model_class=relationships[field_name].mapper.class_,  # noqa
                filters=getattr(filters, field_name)
            )

            model_field = getattr(model_class, field_name)

            if is_many:
                res.append(model_field.any(*nested_orm_filters))
            else:
                res.append(model_field.has(*nested_orm_filters))

    return res


def apply_filters(
        model_class: Any,
        stmt: Select,
        filters: BaseFilterParams
) -> Select:
    orm_filters = _get_orm_filters(
        model_class=model_class,
        filters=filters
    )

    return stmt.filter(and_(*orm_filters))
