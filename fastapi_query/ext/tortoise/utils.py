from typing import Type

from tortoise import Model


def is_field_relationship(
        model_class: Type[Model],
        field_name: str
) -> bool:
    model_fields_map = model_class._meta.fields_map  # noqa
    field = model_fields_map.get(field_name)

    return bool(field) and hasattr(field, "related_model")


def check_is_model_field_valid(
        model_class: Type[Model],
        field_name: str
) -> bool:
    model_fields_map = model_class._meta.fields_map  # noqa

    model_field_name, *parts = field_name.split("__")

    if model_field_name not in model_fields_map:
        return False

    is_relationship = is_field_relationship(
        model_class=model_class,
        field_name=model_field_name
    )

    if is_relationship:
        return check_is_model_field_valid(
            model_class=model_class._meta.fields_map[model_field_name].related_model,  # noqa
            field_name="__".join(parts)
        )

    return not parts


def check_model_field(
        model_class: Type[Model],
        field_name: str
) -> None:
    is_valid = check_is_model_field_valid(
        model_class=model_class,
        field_name=field_name
    )

    if not is_valid:
        raise ValueError(
            f"{field_name} is not valid field for [{model_class.__name__}] model!"
        )
