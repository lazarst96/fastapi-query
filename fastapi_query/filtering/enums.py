from enum import Enum


class FilterOperators(str, Enum):
    EQ = 'eq'
    NEQ = 'neq'
    GT = 'gt'
    GTE = 'gte'
    LTE = 'lte'
    LT = 'lt'
    IN = 'in'
    NIN = 'nin'
    IS_NULL = 'isnull'
    LIKE = 'like'
    ILIKE = 'ilike'
    NOT = 'not'
