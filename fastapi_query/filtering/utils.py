import inspect
import types
from copy import deepcopy
from typing import Type, Dict, Tuple, Union, Optional, Iterable, get_origin, get_args, Any

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.fields import FieldInfo

from .base_params import BaseFilterParams


def check_optional_type(tp: Type) -> bool:
    """
    Returns True if the provided type is optional type.

    Parameters:
        tp (Type): A type to check

    Returns:
        val (bool): Boolean Value that determines whether provided type is Optional or not
    """
    origin = get_origin(tp)
    args = get_args(tp)

    return (
            origin in (Union, types.UnionType) and
            len(args) == 2 and
            args[-1] == types.NoneType
    )


def get_optional_subtype(tp: Type) -> Optional[Type]:
    """
    Returns Subtype of Optional Type.

    Parameters:
        tp (Type): Type to be observed

    Returns:
        val (Type | None): Subtype of provided Optional Type or None if type is not Optional
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
        include_optional (bool): Boolean flag determines whether an optional sequence type will be accepted or not

    Returns:
        val (bool): Boolean Value that determines whether provided type is sequence type or not
    """
    sequence_types = [list, set, frozenset, tuple]
    origin = get_origin(tp)
    args = get_args(tp)

    is_list = inspect.isclass(origin) and any([issubclass(origin, t) for t in sequence_types])
    is_optional_list = (
            check_optional_type(tp) and
            inspect.isclass(get_origin(args[0])) and
            any([issubclass(get_origin(args[0]), t) for t in sequence_types])
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
        include_optional (bool): Boolean flag determines whether an optional nested filter type will be accepted or not

    Returns:
        val (bool): Boolean Value that determines whether provided type is Nested Filter Params Type
    """
    origin = get_origin(tp)
    args = get_args(tp)

    is_nester_filter = inspect.isclass(origin) and issubclass(origin, BaseFilterParams)
    is_optional_nester_filter = (
            check_optional_type(tp) and
            inspect.isclass(args[0]) and
            issubclass(args[0], BaseFilterParams)
    )

    return is_nester_filter or (include_optional and is_optional_nester_filter)


def flatten_filter_fields(
        filter_class: Type[BaseFilterParams]
) -> Dict[str, Tuple[Union[object, Type], Optional[FieldInfo]]]:
    """
    Transforms Filter Params Schema to be compatible with FastAPI Depends Function

    Parameters:
        filter_class (Type[BaseFilterParams]): Filter Params Schema

    Returns:
        flattened_schema_fields (Dict): Transformed Schema Fields Dictionary
    """

    ret = {}

    for field_name, info in filter_class.model_fields.items():
        field_info = deepcopy(info)

        field_type = filter_class.__annotations__.get(field_name, field_info.annotation)

        if check_sequence_type(field_info.annotation):
            if isinstance(field_info.default, Iterable):
                field_info.default = ",".join(field_info.default)

            ret[field_name] = (str if field_info.is_required() else Optional[str], field_info)

        elif check_nested_filter_type(field_type):
            nested_filter_type = get_optional_subtype(field_type) or field_type

            prefix = nested_filter_type.Config.prefix or field_name
            nested_fields = flatten_filter_fields(nested_filter_type)

            ret.update({f"{prefix}__{field}": info for field, info in nested_fields.items()})

        else:
            ret[field_name] = (field_type if field_info.is_required() else Optional[field_type], field_info)

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

    model_fields = filter_class.model_fields
    construction_dict = {}

    for field_name, info in model_fields.items():
        field_type = filter_class.__annotations__.get(field_name, info.annotation)

        if check_nested_filter_type(field_type):
            nested_filter_type = get_optional_subtype(field_type) or field_type

            prefix = nested_filter_type.Config.prefix or field_name

            nested_values = {
                "__".join(key.split('__')[1:]): value
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
        res = filter_class.model_validate(construction_dict)
    except ValidationError as err:
        errors = list(
            map(
                lambda error: {
                    **error,
                    "loc": ('query', *error['loc'])
                },
                err.errors()
            )
        )
        raise RequestValidationError(errors=errors)

    return res
