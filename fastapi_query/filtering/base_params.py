from typing import List, Optional, Type

from pydantic import BaseModel, model_validator


OPERATORS_WITH_SEQ_ARG = {'in', 'not_in'}


class BaseFilterParams(BaseModel):

    @model_validator(mode='before')
    def parse_raw_values(cls, values):

        res = {}
        # print("Model", values)

        for field, value in values.items():
            if (
                    value is not None and
                    '__' in field and
                    field.split("__")[-1] in OPERATORS_WITH_SEQ_ARG

            ):
                res[field] = value.split(',')
            else:
                res[field] = value

        return res

    class Config:
        prefix: Optional[str] = None
        searchable_fields: List[str] = []


def WithPrefix( # noqa
        model: Type[BaseFilterParams],
        prefix: str
) -> Type[BaseFilterParams]:

    global_prefix = prefix

    class WrapperFilterParams(model):
        class Config(model.Config):
            prefix = global_prefix

    return WrapperFilterParams
