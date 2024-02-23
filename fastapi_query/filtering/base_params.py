from typing import List, Optional, Type, Dict, Any

from pydantic import BaseModel

from fastapi_query._compat import _model_validator

from .enums import FilterOperators

OPERATORS_WITH_SEQ_ARG = {FilterOperators.IN, FilterOperators.NOT_IN}


class BaseFilterParams(BaseModel):

    @_model_validator(mode="before")
    def parse_raw_values(cls, values: Dict[str, Any]) -> Dict[str, Any]:

        res = {}

        for field, value in values.items():
            if (
                    value is not None and
                    "__" in field and
                    field.split("__")[-1] in OPERATORS_WITH_SEQ_ARG

            ):
                res[field] = value.split(",")
            else:
                res[field] = value

        return res

    class Settings:
        prefix: Optional[str] = None
        search_field: str = "search"
        searchable_fields: List[str] = []


def WithPrefix( # noqa
        model: Type[BaseFilterParams],
        prefix: str
) -> Type[BaseFilterParams]:

    global_prefix = prefix

    class WrapperFilterParams(model):
        class Settings(model.Settings):
            prefix = global_prefix

    return WrapperFilterParams
