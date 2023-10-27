from enum import Enum


class FilterOperators(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LTE = "lte"
    LT = "lt"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "isnull"
    STARTSWITH = "startswith"
    ISTARTSWITH = "istartswith"
    ENDSWITH = "endswith"
    IENDSWITH = "iendswith"
    CONTAINS = "contains"
    ICONTAINS = "icontains"
    IEXACT = "iexact"
