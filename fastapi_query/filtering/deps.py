from typing import Type, TypeVar, Optional
from typing_extensions import Annotated

from fastapi import Depends
from pydantic import create_model

from .base_params import BaseFilterParams
from .utils import flatten_filter_fields, pack_values

FilterParamsType = TypeVar('FilterParamsType', bound=BaseFilterParams)

def Filter( # noqa
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

    GeneratedFilterModel: Type[BaseFilterParams] = create_model( # noqa
        model.__class__.__name__,
        **fields
    )

    def wrapped_func(
            inner_filters: Annotated[GeneratedFilterModel, Depends(GeneratedFilterModel)]
    ) -> FilterParamsType:

        values = inner_filters.model_dump()
        return pack_values(
            filter_class=model,
            values=values
        )

    return Depends(wrapped_func)
