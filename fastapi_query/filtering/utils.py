import inspect
from collections import deque
from copy import deepcopy
from typing import (
    Type,
    Dict,
    Tuple,
    Union,
    Optional,
    Iterable,
    get_origin,
    get_args,
    Any,
    Sequence,
    List,
    Set,
    FrozenSet,
    Deque
)

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.fields import FieldInfo

from fastapi_query._compat import (
    _get_model_fields,
    _validate
)
from .base_params import BaseFilterParams

sequence_annotation_to_type = {
    Sequence: list,
    List: list,
    list: list,
    Tuple: tuple,
    tuple: tuple,
    Set: set,
    set: set,
    FrozenSet: frozenset,
    frozenset: frozenset,
    Deque: deque,
    deque: deque,
}

sequence_types = tuple(sequence_annotation_to_type.keys())


def check_optional_type(tp: Type) -> bool:
    """
    Returns True if the provided type is optional type.

    Parameters:
        tp (Type): A type to check

    Returns:
        val (bool): Value determines whether provided type is Optional or not
    """
    origin = get_origin(tp)
    args = get_args(tp)

    return (

            isinstance(origin, type(Union)) and
            len(args) == 2 and
            args[-1] == type(None)  # noqa
    )


def get_optional_subtype(tp: Type) -> Optional[Type]:
    """
    Returns Subtype of Optional Type or None if type is not Optional.

    Parameters:
        tp (Type): Type to be observed

    Returns:
        val (Optional[Type]): Subtype of provided Type
    """

    if not check_optional_type(tp):
        return None

    return get_args(tp)[0]


def check_sequence_type(
        tp: Type,
        include_optional: bool = True
) -> bool:
    """
    Returns True if the provided type is sequence type.

    Parameters:
        tp (Type): A type to check
        include_optional (bool): Boolean flag determines
            whether an optional sequence type will be accepted or not

    Returns:
        val (bool): Value determines whether provided type is sequence type or not
    """
    origin = get_origin(tp)
    args = get_args(tp)

    is_list = (
            inspect.isclass(origin) and
            any(issubclass(origin, t) for t in sequence_types)
    )
    is_optional_list = (
            check_optional_type(tp) and
            inspect.isclass(get_origin(args[0])) and
            any(issubclass(get_origin(args[0]), t) for t in sequence_types)
    )

    return is_list or (include_optional and is_optional_list)


def check_nested_filter_type(
        tp: Type,
        include_optional: bool = True
) -> bool:
    """
    Returns True if the provided type is Nested Filter Params Type.

    Parameters:
        tp (Type): A type to check
        include_optional (bool): Boolean flag determines
            whether an optional nested filter type will be accepted or not

    Returns:
        val (bool): Value determines whether provided type is Nested Filter Params Type
    """
    args = get_args(tp)

    is_nester_filter = inspect.isclass(tp) and issubclass(tp, BaseFilterParams)
    is_optional_nester_filter = (
            check_optional_type(tp) and
            inspect.isclass(args[0]) and
            issubclass(args[0], BaseFilterParams)
    )

    return is_nester_filter or (include_optional and is_optional_nester_filter)


def flatten_filter_fields(
        filter_class: Type[BaseFilterParams]
) -> Dict[str, Tuple[Union[object, Type], FieldInfo]]:
    """
    Transforms Filter Params Schema to be compatible with FastAPI Depends Function

    Parameters:
        filter_class (Type[BaseFilterParams]): Filter Params Schema

    Returns:
        flattened_schema_fields (Dict): Transformed Schema Fields Dictionary
    """

    ret = {}
    model_fields = _get_model_fields(filter_class)

    for field_name, f in model_fields.items():
        field_info = deepcopy(f.field_info)

        field_type = filter_class.__annotations__.get(field_name, f.type_)

        if check_sequence_type(field_type):
            if isinstance(f.default, Iterable):
                field_info.default = ",".join(map(str, f.default))

            res_field_type = str if f.required else Optional[str]
            ret[field_name] = (res_field_type, field_info)

        elif check_nested_filter_type(field_type):
            nested_filter_type = get_optional_subtype(field_type) or field_type

            prefix = nested_filter_type.Settings.prefix or field_name
            nested_fields = flatten_filter_fields(nested_filter_type)

            ret.update({
                f"{prefix}__{field}": info
                for field, info in nested_fields.items()
            })

        else:
            res_field_type = field_type if f.required else Optional[field_type]

            ret[field_name] = (res_field_type, field_info)

    return ret


def pack_values(
        filter_class: Type[BaseFilterParams],
        values: Dict[str, Any]
) -> BaseFilterParams:
    """
    Transforms the values from flattened schema to original schema.

    Parameters:
        filter_class (Type[BaseFilterParams]): Original Filter Params Schema
        values: (dict[str, Any]): Values

    Returns:
        transformed_values (BaseFilterParams): Transformed Values
    """

    model_fields = _get_model_fields(filter_class)
    construction_dict = {}

    for field_name, f in model_fields.items():
        field_type = filter_class.__annotations__.get(field_name, f.type_)

        if check_nested_filter_type(field_type):
            nested_filter_type = get_optional_subtype(field_type) or field_type

            prefix = nested_filter_type.Settings.prefix or field_name

            nested_values = {
                "__".join(key.split("__")[1:]): value
                for key, value in values.items()
                if key.startswith(f"{prefix}__")
            }

            construction_dict[field_name] = pack_values(
                filter_class=nested_filter_type,
                values=nested_values
            )
        else:
            construction_dict[field_name] = values.get(field_name)

    try:
        res = _validate(filter_class, construction_dict)
    except ValidationError as err:
        errors = [
            {
                **error,
                "loc": ("query", *error["loc"])
            } for error in err.errors()
        ]
        raise RequestValidationError(errors=errors) from None

    return res
