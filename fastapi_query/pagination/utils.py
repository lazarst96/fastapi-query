from math import ceil
from typing import Dict, Any, List

from .schemas import PaginationParams


def prepare_response(
        items: List[Any],
        total_items: int,
        pagination_params: PaginationParams
) -> Dict[str, Any]:

    if pagination_params.get_all:
        current_page = 1
        items_per_page = total_items
        total_pages = 1
    else:
        current_page = pagination_params.page
        items_per_page = pagination_params.size
        total_pages = ceil(total_items / pagination_params.size)

    return {
        "items": items,
        "meta": {
            "current_page": current_page,
            "items_per_page": items_per_page,
            "total_pages": total_pages,
            "total_items": total_items
        }
    }
