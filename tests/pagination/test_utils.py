from typing import List, Any

import pytest

from fastapi_query.pagination import PaginationParams
from fastapi_query.pagination.utils import prepare_response


@pytest.mark.parametrize(
    "items,total_items,page,size,get_all,current_page,total_pages,items_per_page",
    [
        ([{}] * 20, 1000, 1, 20, False, 1, 50, 20),
        ([{}] * 20, 1000, 5, 20, False, 5, 50, 20),
        ([{}] * 20, 10, 1, 20, False, 1, 1, 20),
        ([{}] * 100, 100, 1, 20, True, 1, 1, 100),
        ([{}] * 50, 100, 3, 20, True, 1, 1, 100),
    ]
)
def test_prepare_response(
        items: List[Any],
        total_items: int,
        page: int,
        size: int,
        get_all: bool,
        current_page: int,
        total_pages: int,
        items_per_page: int
) -> None:
    res = prepare_response(
        items=items,
        total_items=total_items,
        pagination_params=PaginationParams(
            page=page,
            size=size,
            get_all=get_all
        )
    )

    meta = res["meta"]
    assert meta["current_page"] == current_page
    assert meta["items_per_page"] == items_per_page
    assert meta["total_pages"] == total_pages
    assert meta["total_items"] == total_items

    assert res["items"] == items
