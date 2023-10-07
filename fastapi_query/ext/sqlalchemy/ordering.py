from typing import Any, Optional

from sqlalchemy import Select


def apply_ordering(
        model_class: Any,
        stmt: Select,
        order_by: Optional[str]
) -> Select:
    """Function for applying order by on the query object"""

    if not order_by:
        return stmt

    fields = order_by.split(',')
    criterion = []

    for field in fields:
        desc = False
        if field.startswith(('-', '+')):
            desc = field[0] == '-'
            field = field[1:]

        if not hasattr(model_class, field):
            continue

        model_field = getattr(model_class, field)

        criterion.append(model_field.desc() if desc else model_field)

    if criterion:
        stmt = stmt.order_by(*criterion)

    return stmt
