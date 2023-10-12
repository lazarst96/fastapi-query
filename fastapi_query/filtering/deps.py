from typing import Type, TypeVar

from fastapi import Depends
from pydantic import create_model
from typing_extensions import Annotated

from fastapi_query._compat import _model_dump
from .base_params import BaseFilterParams
from .utils import flatten_filter_fields, pack_values

FilterParamsType = TypeVar("FilterParamsType", bound=BaseFilterParams)


def Filter(  # noqa
        model: Type[FilterParamsType]
) -> FilterParamsType:
    """
    Filter Dependency

    Parameters:
        model (Type[BaseFilterParams]): Filter Params Schema

    Returns:
        dependency_result (BaseFilterParams): Filter Object
    """
    fields = flatten_filter_fields(model)

    GeneratedFilterModel: Type[BaseFilterParams] = create_model(
        model.__class__.__name__,
        **fields
    )

    InnerFilters = Annotated[GeneratedFilterModel, Depends(GeneratedFilterModel)]

    def wrapped_func(
            inner_filters: InnerFilters
    ) -> FilterParamsType:
        values = _model_dump(inner_filters)
        return pack_values(
            filter_class=model,
            values=values
        )

    return Depends(wrapped_func)
