from typing import Optional, Type, List

from tortoise.expressions import Q
from tortoise.models import Model
from tortoise.queryset import QuerySet

from fastapi_query._compat import _model_dump
from fastapi_query.ext.tortoise.utils import is_field_relationship, check_model_field
from fastapi_query.filtering import BaseFilterParams
from fastapi_query.filtering.enums import FilterOperators
from fastapi_query.utils import flatten_dict

_orm_operator_transformer = {
    FilterOperators.EQ: lambda field, value: (field, value),
    FilterOperators.NEQ: lambda field, value: (f"{field}__not", value),
    FilterOperators.GT: lambda field, value: (f"{field}__gt", value),
    FilterOperators.GTE: lambda field, value: (f"{field}__gte", value),
    FilterOperators.LT: lambda field, value: (f"{field}__lt", value),
    FilterOperators.LTE: lambda field, value: (f"{field}__lte", value),
    FilterOperators.IN: lambda field, value: (f"{field}__in", value),
    FilterOperators.NOT_IN: lambda field, value: (f"{field}__not_in", value),
    FilterOperators.IS_NULL: lambda field, value: (f"{field}__isnull", value),
    FilterOperators.STARTSWITH: lambda field, value: (f"{field}__startswith", value),
    FilterOperators.ISTARTSWITH: lambda field, value: (f"{field}__istartswith", value),
    FilterOperators.ENDSWITH: lambda field, value: (f"{field}__endswith", value),
    FilterOperators.IENDSWITH: lambda field, value: (f"{field}__iendswith", value),
    FilterOperators.CONTAINS: lambda field, value: (f"{field}__contains", value),
    FilterOperators.ICONTAINS: lambda field, value: (f"{field}__icontains", value),
    FilterOperators.IEXACT: lambda field, value: (f"{field}__iexact", value),
}


def _check_filter_fields(
        model_class: Type[Model],
        filters: BaseFilterParams
) -> None:
    model_fields_map = model_class._meta.fields_map  # noqa
    filter_fields = _model_dump(filters, exclude_none=True)

    for field_name, value in filter_fields.items():
        if "__" in field_name:
            parts = field_name.split("__")
            field_name, operator = "__".join(parts[:-1]), parts[-1]

            if operator not in _orm_operator_transformer:
                raise ValueError(f"Invalid Filter Operator - {operator}")

        if field_name == filters.Settings.search_field:
            continue

        if field_name not in model_fields_map:
            raise ValueError(
                f"{model_class.__name__} does not contain [{field_name}] field"
            )

        is_relationship = is_field_relationship(
            model_class=model_class,
            field_name=field_name
        )

        if not isinstance(value, dict) and is_relationship:
            raise ValueError(
                f"Invalid pair [{field_name}, {value}] for {model_class.__name__}!"
            )
        elif is_relationship:
            _check_filter_fields(
                model_class=model_class._meta.fields_map[field_name].related_model,  # noqa
                filters=getattr(filters, field_name)
            )


def _get_search_criteria(
        model_class: Type[Model],
        search_query: str,
        searchable_fields: Optional[List[str]]
) -> Optional[Q]:

    res = {}
    searchable_fields = searchable_fields or []

    for field_name in searchable_fields:
        check_model_field(
            model_class=model_class,
            field_name=field_name
        )

        res[f"{field_name}__icontains"] = search_query

    if not res:
        return None

    return Q(**res, join_type="OR")


def _get_orm_filters(
        model_class: Type[Model],
        filters: BaseFilterParams
) -> Optional[Q]:
    res_filters = {}
    search_criteria_expression: Optional[Q] = None

    # Check if filters are valid
    _check_filter_fields(
        model_class=model_class,
        filters=filters
    )

    filter_fields = flatten_dict(
        obj=_model_dump(filters, exclude_none=True),
        delimiter="__"
    )

    for criteria, value in filter_fields.items():
        parts = criteria.split("__")

        operator = FilterOperators.EQ
        field_name = criteria

        if len(parts) > 1 and parts[-1] in _orm_operator_transformer:
            operator = parts[-1]
            field_name = "__".join(parts[:-1])

        filter_field_name, filter_value = _orm_operator_transformer[operator](
            field=field_name,
            value=value
        )

        if criteria == filters.Settings.search_field:
            search_criteria_expression = _get_search_criteria(
                model_class=model_class,
                search_query=value,
                searchable_fields=filters.Settings.searchable_fields
            )
        else:
            res_filters[filter_field_name] = filter_value

    res = None

    if res_filters:
        res = Q(**res_filters, join_type="AND")

    if search_criteria_expression:
        if res:
            res &= search_criteria_expression
        else:
            res = search_criteria_expression

    return res


def apply_filters(
        queryset: QuerySet,
        filters: Optional[BaseFilterParams]
) -> QuerySet:
    """
    Function for applying filters to the query object

    Parameters:
        queryset (QuerySet): Pre-constructed QuerySet
        filters (BaseFilterParams): Comma-separated fields / field-paths

    Returns:
        result_queryset (QuerySet): Result QuerySet
    """

    model_class = queryset.model

    if not filters:
        return queryset

    filter_expression = _get_orm_filters(
        model_class=model_class,
        filters=filters
    )

    if not filter_expression:
        return queryset

    return queryset.filter(filter_expression)
