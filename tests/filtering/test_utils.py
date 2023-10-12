from typing import Type, Optional, List, Any, Dict

import pytest
from fastapi.exceptions import RequestValidationError

from fastapi_query.filtering.utils import (
    check_optional_type,
    get_optional_subtype,
    check_sequence_type,
    check_nested_filter_type,
    flatten_filter_fields,
    pack_values
)
from .examples.fields_info import (
    USER_FIELDS_INFO,
    ORDER_FIELDS_INFO,
    ADDRESS_FIELDS_INFO,
    FieldInfoAttrs
)
from .examples.schemas import UserFilters, OrderFilters, AddressFilters


@pytest.mark.parametrize(
    "tp,expected",
    [
        (Optional[int], True),
        (Optional[List[str]], True),
        (float, False),
        (List[Dict[str, Any]], False),
        (Any, False)
    ]
)
def test_check_optional_type(
        tp: Type,
        expected: bool
) -> None:
    assert check_optional_type(tp=tp) == expected


@pytest.mark.parametrize(
    "tp,expected",
    [
        (Optional[int], int),
        (Optional[List[str]], List[str]),
        (float, None),
        (Optional[Dict[str, List[Any]]], Dict[str, List[Any]]),
        (Optional[Any], Any)
    ]
)
def test_get_optional_subtype(
        tp: Type,
        expected: Type
) -> None:
    assert get_optional_subtype(tp=tp) == expected


@pytest.mark.parametrize(
    "tp,include_optional,expected",
    [
        (Optional[int], True, False),
        (Optional[List[str]], True, True),
        (float, False, False),
        (List[Dict[str, Any]], False, True),
        (List[Dict[str, Any]], True, True),
        (Any, False, False)
    ]
)
def test_check_sequence_type(
        tp: Type,
        include_optional: bool,
        expected: bool
) -> None:
    res = check_sequence_type(
        tp=tp,
        include_optional=include_optional
    )
    assert res == expected


@pytest.mark.parametrize(
    "tp,include_optional,expected",
    [
        (UserFilters, True, True),
        (Optional[UserFilters], True, True),
        (UserFilters, False, True),
        (Optional[int], True, False),
        (Optional[List[str]], True, False),
        (float, False, False),
        (List[Dict[str, Any]], False, False),
        (Any, False, False)
    ]
)
def test_check_nested_filter_type(
        tp: Type,
        include_optional: bool,
        expected: bool
) -> None:
    res = check_nested_filter_type(
        tp=tp,
        include_optional=include_optional
    )
    assert res == expected


@pytest.mark.parametrize(
    "filter_class,expected_attr",
    [
        (AddressFilters, ADDRESS_FIELDS_INFO),
        (OrderFilters, ORDER_FIELDS_INFO),
        (UserFilters, USER_FIELDS_INFO),
    ]
)
def test_flatten_filter_fields(
        filter_class: Any,
        expected_attr: Dict[str, FieldInfoAttrs]
) -> None:
    res = flatten_filter_fields(filter_class=filter_class)

    for field_name, val in res.items():
        field_type, field_info = val

        assert field_type == expected_attr[field_name]["type"]
        assert field_info.is_required() == expected_attr[field_name]["required"]
        assert field_info.default == expected_attr[field_name]["default"]


@pytest.mark.parametrize(
    "filter_class,values,expected,exception_should_occur",
    [
        (
                AddressFilters,
                {"id": 1, "id__nin": "5,6"},
                {"id": 1, "id__nin": [5, 6]},
                False
        ),
        (
                UserFilters,
                {
                    "id": 1,
                    "id__in": "1,2,3",
                    "shipping_address__id": 1,
                    "billing_address__city": "San Diego",
                },
                {
                    "id": 1,
                    "id__in": [1, 2, 3],
                    "shipping_address": {
                        "id": 1
                    },
                    "billing_address": {
                        "city": "San Diego"
                    },
                    "orders": {}
                },
                False
        ),
        (
                OrderFilters,
                {"id": 1, "id__neq": "invalid"},
                None,
                True
        )
    ]
)
def test_pack_values(
        filter_class: Any,
        values: Dict[str, Any],
        expected: Dict[str, FieldInfoAttrs],
        exception_should_occur: bool
) -> None:
    exception_occurred = False
    try:
        res = pack_values(
            filter_class=filter_class,
            values=values
        )
        assert res.model_dump(exclude_none=True) == expected
    except RequestValidationError:
        exception_occurred = True

    assert exception_should_occur == exception_occurred

