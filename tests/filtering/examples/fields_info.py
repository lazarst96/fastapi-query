from datetime import datetime
from typing import TypedDict, Dict, Type, Any, Optional


class FieldInfoAttrs(TypedDict):
    type: Any
    required: bool
    default: Optional[Any]


ADDRESS_FIELDS_INFO: Dict[str, FieldInfoAttrs] = {
    "id": {
        "type": Optional[int],
        "required": False,
        "default": None
    },
    "id__not_in": {
        "type": Optional[str],
        "required": False,
        "default": "5,6"
    },
    "line_1__icontains": {
        "type": Optional[str],
        "required": False,
        "default": None
    },
    "city": {
        "type": Optional[str],
        "required": False,
        "default": None
    },
}

ORDER_FIELDS_INFO: Dict[str, FieldInfoAttrs] = {
    "id": {
        "type": Optional[int],
        "required": False,
        "default": None
    },
    "id__neq": {
        "type": Optional[int],
        "required": False,
        "default": None
    },
    "amount__lt": {
        "type": Optional[int],
        "required": False,
        "default": None
    },
    "amount__gt": {
        "type": Optional[int],
        "required": False,
        "default": None
    },
}

USER_FIELDS_INFO: Dict[str, FieldInfoAttrs] = {
    "id": {
        "type": Optional[int],
        "required": False,
        "default": None
    },
    "id__in": {
        "type": Optional[str],
        "required": False,
        "default": "1,2,3"
    },
    "username": {
        "type": Optional[str],
        "required": False,
        "default": None
    },
    "username__contains": {
        "type": Optional[str],
        "required": False,
        "default": None
    },
    "created_at": {
        "type": Optional[datetime],
        "required": False,
        "default": None
    },
    "created_at__gte": {
        "type": Optional[datetime],
        "required": False,
        "default": None
    },
    "created_at__lte": {
        "type": Optional[datetime],
        "required": False,
        "default": None
    },
    "shipping_address_id__isnull": {
        "type": Optional[bool],
        "required": False,
        "default": False
    },
    **{
        f"shipping_address__{fiend_name}": attrs
        for fiend_name, attrs in ADDRESS_FIELDS_INFO.items()
    },
    **{
        f"billing_address__{fiend_name}": attrs
        for fiend_name, attrs in ADDRESS_FIELDS_INFO.items()
    },
    **{
        f"orders__{fiend_name}": attrs
        for fiend_name, attrs in ORDER_FIELDS_INFO.items()
    },
}
