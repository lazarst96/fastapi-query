from typing import Any, TypeVar, Dict, Optional

from tortoise.queryset import QuerySet

from fastapi_query.filtering import BaseFilterParams
from fastapi_query.pagination.schemas import PaginationParams
from fastapi_query.pagination.utils import prepare_response
from .filtering import apply_filters
from .ordering import apply_ordering


def _paginate_query_with_page(
        queryset: QuerySet,
        params: PaginationParams
) -> QuerySet:
    """
    Applies Pagination to Query

    Parameters:
        queryset (QuerySe): Pre-constructed QuerySe
        params (PaginationParams): Pagination Params that will be applied

    Returns:
        result_queryset (QuerySe): Result QuerySe
    """
    offset = (params.page - 1) * params.size
    queryset = queryset.offset(offset=offset).limit(limit=params.size)

    return queryset


async def paginate(
        queryset: QuerySet,
        pagination_params: PaginationParams,
        filter_params: Optional[BaseFilterParams] = None,
        ordering_params: Optional[str] = None
) -> Dict[str, Any]:
    """
    Applies Pagination for SQLAlchemy Asyncio Backend

    Parameters:
        queryset (QuerySet): Pre-constructed Select Statement
        pagination_params (PaginationParams): Pagination Params
        filter_params (Optional[BaseFilterParams]): Filtering Params
        ordering_params (Optional[str]): OrderBy Params (comma-separated)

    Returns:
        paginated_response (Dict[str, Any]): Paginated Result
    """

    # Apply Filtering if params are provided
    if filter_params:
        queryset = apply_filters(
            queryset=queryset,
            filters=filter_params
        )

    # Apply Ordering if params are provided
    if ordering_params:
        queryset = apply_ordering(
            queryset=queryset,
            order_by=ordering_params
        )

    total_items = await queryset.count()

    if not pagination_params.get_all:
        queryset = _paginate_query_with_page(
            queryset=queryset,
            params=pagination_params
        )

    items = await queryset.all()

    return prepare_response(
        items=items,
        total_items=total_items,
        pagination_params=pagination_params
    )
