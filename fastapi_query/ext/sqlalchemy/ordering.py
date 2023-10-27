from typing import Any, Optional, List, Dict, Union

from sqlalchemy import Select, inspect
from sqlalchemy.orm import Relationship, Query


def _get_field(
    model_class: Any,
    field_path: List[str]
):
    """
    Returns Model Fields based on the field path

    Parameters:
        model_class (Any): SQLAlchemy Model Class
        field_path (List[str]): Field Path

    Returns:
        result_field (Any): Result Model Field
    """
    field_path = list(filter(lambda item: len(item.strip()) > 0, field_path))

    if not field_path:
        return None

    field_name = field_path[0]

    if not hasattr(model_class, field_name):
        return None

    if len(field_path) == 1:
        return getattr(model_class, field_name)

    relationships: Dict[str, Relationship] = dict(inspect(model_class).relationships)

    if field_name not in relationships:
        return None

    return _get_field(
        model_class=relationships[field_name].mapper.class_,  # noqa
        field_path=field_path[1:]
    )


def apply_ordering(
        model_class: Any,
        stmt: Union[Select, Query],
        order_by: Optional[str]
) -> Union[Select, Query]:
    """
    Function for applying order by on the query object

    Parameters:
        model_class (Any): SQLAlchemy Model Class
        stmt (Union[Select, Query]): Pre-constructed Select Statement
        order_by (Optional[str]): Comma-separated fields / field-paths

    Returns:
        result_stmt (Union[Select, Query]): Result Statement
    """

    if not order_by:
        return stmt

    fields = order_by.split(",")
    criterion = []

    for field in fields:
        field = field.strip()
        desc = False
        if field.startswith(("-", "+")):
            desc = field[0] == "-"
            field = field[1:]

        model_field = _get_field(
            model_class=model_class,
            field_path=field.split("__")
        )

        if not model_field:
            continue

        criterion.append(model_field.desc() if desc else model_field)

    if criterion:
        stmt = stmt.order_by(*criterion)

    return stmt
