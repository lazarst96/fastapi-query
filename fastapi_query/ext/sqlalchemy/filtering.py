from typing import Any, Dict, List, Optional, Union

from sqlalchemy import Select, and_, Column, or_, ColumnElement
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Relationship, Query

from fastapi_query._compat import _model_dump
from fastapi_query.filtering import BaseFilterParams
from fastapi_query.filtering.enums import FilterOperators

_orm_operator_transformer = {
    FilterOperators.EQ: lambda value: ("__eq__", value),
    FilterOperators.NEQ: lambda value: ("__ne__", value),
    FilterOperators.GT: lambda value: ("__gt__", value),
    FilterOperators.GTE: lambda value: ("__ge__", value),
    FilterOperators.LT: lambda value: ("__lt__", value),
    FilterOperators.LTE: lambda value: ("__le__", value),
    FilterOperators.IN: lambda value: ("in_", value),
    FilterOperators.NOT_IN: lambda value: ("not_in", value),
    FilterOperators.IS_NULL: lambda value: ("is_", None) if value is True else ("is_not", None),  # noqa: E501
    FilterOperators.STARTSWITH: lambda value: ("like", f"{value}%"),
    FilterOperators.ISTARTSWITH: lambda value: ("ilike", f"{value}%"),
    FilterOperators.ENDSWITH: lambda value: ("like", f"%{value}"),
    FilterOperators.IENDSWITH: lambda value: ("ilike", f"%{value}"),
    FilterOperators.CONTAINS: lambda value: ("like", f"%{value}%"),
    FilterOperators.ICONTAINS: lambda value: ("ilike", f"%{value}%"),
    FilterOperators.IEXACT: lambda value: ("ilike", value),
}


def _get_search_criteria(
        model_class: Any,
        search_query: str,
        searchable_fields: Optional[List[str]]
) -> Optional[ColumnElement[bool]]:
    relationships: Dict[str, Relationship] = dict(inspect(model_class).relationships)

    res = []

    fields = searchable_fields or []
    nested_searchable_fields: Dict[str, List[str]] = {
        field: [] for field in relationships.keys()
    }

    for path in fields:
        field_name, *parts = path.split("__")
        if field_name in relationships:
            nested_searchable_fields[field_name].append("__".join(parts))
        elif hasattr(model_class, field_name):
            model_field = getattr(model_class, field_name)
            res.append(model_field.ilike(f"%{search_query}%"))
        else:
            raise ValueError(
                f"{field_name} is not valid field for [{model_class.__name__}] model!"
            )

    for rel, nest_searchable_fields in nested_searchable_fields.items():
        if not nest_searchable_fields:
            continue

        is_many = relationships[rel].uselist
        model_field = getattr(model_class, rel)

        criteria = _get_search_criteria(
            model_class=relationships[rel].mapper.class_,  # noqa
            search_query=search_query,
            searchable_fields=nest_searchable_fields
        )

        if is_many:
            res.append(
                model_field.any(criteria)
            )
        else:
            res.append(
                model_field.has(criteria)
            )

    if not res:
        return None

    if len(res) == 1:
        return res[0]

    return or_(*res)


def _get_orm_filters(
        model_class: Any,
        filters: BaseFilterParams
) -> List[Any]:
    relationships: Dict[str, Relationship] = dict(inspect(model_class).relationships)

    res = []
    filter_fields = _model_dump(filters, exclude_none=True)

    for field_name, value in filter_fields.items():
        if "__" in field_name:
            parts = field_name.split("__")
            field_name, operator = "__".join(parts[:-1]), parts[-1]

            if operator not in _orm_operator_transformer:
                raise ValueError(f"Invalid Filter Operator - {operator}")

            operator, value = _orm_operator_transformer[operator](value)
        else:
            operator = "__eq__"

        if field_name == filters.Settings.search_field:

            criteria = _get_search_criteria(
                model_class=model_class,
                search_query=value,
                searchable_fields=filters.Settings.searchable_fields
            )
            if criteria is not None:
                res.append(criteria)

        elif (
                isinstance(value, dict) and
                field_name in relationships and
                relationships[field_name]
        ):

            is_many = relationships[field_name].uselist
            nested_orm_filters = _get_orm_filters(
                model_class=relationships[field_name].mapper.class_,  # noqa
                filters=getattr(filters, field_name)
            )

            model_field = getattr(model_class, field_name)
            if is_many:
                res.append(
                    model_field.any(and_(*nested_orm_filters))
                )
            else:
                res.append(
                    model_field.has(and_(*nested_orm_filters))
                )

        elif hasattr(model_class, field_name):
            model_field = getattr(model_class, field_name)
            res.append(getattr(model_field, operator)(value))

        elif value:
            raise ValueError(
                f"Invalid {model_class.__name__} Field - {field_name}"
            )

    return res


def apply_filters(
        model_class: Any,
        stmt: Union[Select, Query],
        filters: Optional[BaseFilterParams]
) -> Union[Select, Query]:
    """
    Function for applying filters to the query object

    Parameters:
        model_class (Any): SQLAlchemy Model Class
        stmt (Union[Select, Query]): Pre-constructed Select Statement
        filters (BaseFilterParams): Comma-separated fields / field-paths

    Returns:
        result_stmt (Union[Select, Query]): Result Statement
    """

    if not filters:
        return stmt

    orm_filters = _get_orm_filters(
        model_class=model_class,
        filters=filters
    )

    if not orm_filters:
        return stmt

    return stmt.filter(and_(*orm_filters))
