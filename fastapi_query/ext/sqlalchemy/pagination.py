from typing import Any, TypeVar, Dict, Optional, Union

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, Query

from fastapi_query.filtering import BaseFilterParams
from fastapi_query.pagination.schemas import PaginationParams
from fastapi_query.pagination.utils import prepare_response
from .filtering import apply_filters
from .ordering import apply_ordering

ModelClass = TypeVar("ModelClass")


def _paginate_query_with_page(
        stmt: Union[Select, Query],
        params: PaginationParams
) -> Select:
    """
    Applies Pagination to Query

    Parameters:
        stmt (Select): Pre-constructed Select Statement
        params (PaginationParams): Pagination Params that will be applied

    Returns:
        result_stmt (Select): Result Statement
    """
    offset = (params.page - 1) * params.size
    stmt = stmt.offset(offset=offset).limit(limit=params.size)

    return stmt


def paginate(
        db: Session,
        stmt: Union[Select, Query],
        pagination_params: PaginationParams,
        model_class: Optional[Any] = None,
        filter_params: Optional[BaseFilterParams] = None,
        ordering_params: Optional[str] = None
) -> Dict[str, Any]:
    """
    Applies Pagination for SQLAlchemy Backend

    Parameters:
        db (Session): SQLAlchemy Active Session
        stmt (Union[Select, Query]): Pre-constructed Select Statement
        pagination_params (PaginationParams): Pagination Params
        model_class (Optional[Any]): SQLAlchemy Model Class
        filter_params (Optional[BaseFilterParams]): Filtering Params
        ordering_params (Optional[str]): OrderBy Params (comma-separated)

    Returns:
        paginated_response (Dict[str, Any]): Paginated Result
    """

    if (filter_params or ordering_params) and not model_class:
        raise ValueError(
            "'model_class' is required when either filtering or ordering is applied"
        )

    # Apply Filtering if params are provided
    if filter_params:
        stmt = apply_filters(
            model_class=model_class,
            stmt=stmt,
            filters=filter_params
        )

    # Apply Ordering if params are provided
    if ordering_params:
        stmt = apply_ordering(
            model_class=model_class,
            stmt=stmt,
            order_by=ordering_params
        )

    total_items = db.scalar(
        select(func.count()).select_from(stmt.subquery())
    )

    if not pagination_params.get_all:
        stmt = _paginate_query_with_page(
            stmt=stmt,
            params=pagination_params
        )

    items = list(db.scalars(stmt).all())

    return prepare_response(
        items=items,
        total_items=total_items,
        pagination_params=pagination_params
    )


async def paginate_async(
        db: AsyncSession,
        stmt: Union[Select, Query],
        pagination_params: PaginationParams,
        model_class: Optional[Any] = None,
        filter_params: Optional[BaseFilterParams] = None,
        ordering_params: Optional[str] = None
) -> Dict[str, Any]:
    """
    Applies Pagination for SQLAlchemy Asyncio Backend

    Parameters:
        db (AsyncSession): SQLAlchemy Async Active Session
        stmt (Union[Select, Query]): Pre-constructed Select Statement
        pagination_params (PaginationParams): Pagination Params
        model_class (Optional[Any]): SQLAlchemy Model Class
        filter_params (Optional[BaseFilterParams]): Filtering Params
        ordering_params (Optional[str]): OrderBy Params (comma-separated)

    Returns:
        paginated_response (Dict[str, Any]): Paginated Result
    """

    if (filter_params or ordering_params) and not model_class:
        raise ValueError(
            "'model_class' is required when either filtering or ordering is applied"
        )

    # Apply Filtering if params are provided
    if filter_params:
        stmt = apply_filters(
            model_class=model_class,
            stmt=stmt,
            filters=filter_params
        )

    # Apply Ordering if params are provided
    if ordering_params:
        stmt = apply_ordering(
            model_class=model_class,
            stmt=stmt,
            order_by=ordering_params
        )

    total_items = await db.scalar(
        select(func.count()).select_from(stmt.subquery())
    )

    if not pagination_params.get_all:
        stmt = _paginate_query_with_page(
            stmt=stmt,
            params=pagination_params
        )

    items = list(
        (await db.scalars(stmt)).all()
    )

    return prepare_response(
        items=items,
        total_items=total_items,
        pagination_params=pagination_params
    )
