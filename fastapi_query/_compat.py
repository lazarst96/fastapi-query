from dataclasses import dataclass
from typing import Any, Dict, Type, Callable

from pydantic import BaseModel
from pydantic.version import VERSION as PYDANTIC_VERSION
from typing_extensions import Annotated, Literal

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

if PYDANTIC_V2:
    from pydantic import model_validator
    from pydantic.fields import FieldInfo
    from pydantic import TypeAdapter
    from pydantic_core import PydanticUndefined, PydanticUndefinedType

    Undefined = PydanticUndefined
    UndefinedType = PydanticUndefinedType


    @dataclass
    class ModelField:
        field_info: FieldInfo
        name: str
        mode: Literal["validation", "serialization"] = "validation"

        @property
        def alias(self) -> str:
            a = self.field_info.alias
            return a if a is not None else self.name

        @property
        def required(self) -> bool:
            return self.field_info.is_required()

        @property
        def default(self) -> Any:
            return self.get_default()

        @property
        def type_(self) -> Any:
            return self.field_info.annotation

        def __post_init__(self) -> None:
            self._type_adapter: TypeAdapter[Any] = TypeAdapter(
                Annotated[self.field_info.annotation, self.field_info]
            )

        def get_default(self) -> Any:
            if self.field_info.is_required():
                return Undefined
            return self.field_info.get_default(call_default_factory=True)

        def __hash__(self) -> int:
            # Each ModelField is unique for our purposes, to allow making a dict from
            # ModelField to its JSON Schema.
            return id(self)


    def _get_model_fields(
            model: Type[BaseModel]
    ) -> Dict[str, ModelField]:

        return {
            name: ModelField(
                name=name,
                field_info=field_info
            ) for name, field_info in model.model_fields.items()
        }


    def _model_dump(
            model: BaseModel,
            mode: Literal["json", "python"] = "json",
            **kwargs: Any
    ) -> Any:
        return model.model_dump(mode=mode, **kwargs)


    def _validate(
            model: Type[BaseModel],
            value: Any
    ) -> Any:
        return model.model_validate(obj=value)


    def _model_validator(
            *args,
            mode: Literal["before", "after"] = "before"
    ) -> classmethod:
        return model_validator(*args, mode=mode)  # noqa


    def _is_model_field_required(field: Any) -> bool:
        return field.is_required()
else:
    from pydantic import root_validator
    from pydantic.fields import ModelField


    def _get_model_fields(
            model: Type[BaseModel]
    ) -> Dict[str, ModelField]:
        return model.__fields__


    def _model_dump(
            model: BaseModel,
            mode: Literal["json", "python"] = "json",
            **kwargs: Any
    ) -> Any:
        return model.dict(**kwargs)


    def _validate(
            model: Type[BaseModel],
            value: Any
    ) -> Any:
        return model.validate(value=value)


    def _model_validator(
            *args,
            mode: Literal["before", "after"] = "before"
    ) -> Callable:
        return root_validator(*args, pre=mode == "before")  # noqa


    def _is_model_field_required(field: Any) -> bool:
        return field.required

__all__ = [
    "PYDANTIC_V2",
    "_model_dump",
    "_model_validator",
    "_get_model_fields",
    "_validate",
    "_is_model_field_required"
]
