from math import ceil
from typing import Union, Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_query.pagination.schemas import PageParams, LimitOffsetParams

PaginationParams = Union[PageParams, LimitOffsetParams]


def _paginate_query_with_page(
        stmt: Select,
        params: PageParams
) -> Select:
    offset = (params.page - 1) * params.limit
    stmt = stmt.offset(offset=offset).limit(limit=params.limit)

    return stmt


def _paginate_query_with_limit_offset(
        stmt: Select,
        params: LimitOffsetParams
) -> Select:
    stmt = stmt.offset(offset=params.offset).limit(limit=params.limit)

    return stmt


def paginate(
        db: Session,
        stmt: Select,
        params: PaginationParams
) -> dict[str, Any]:
    total_items = db.scalar(
        select(func.count()).select_from(stmt)
    )

    if not params.get_all:

        if isinstance(params, PageParams):
            stmt = _paginate_query_with_page(
                stmt=stmt,
                params=params
            )
        elif isinstance(params, LimitOffsetParams):
            stmt = _paginate_query_with_limit_offset(
                stmt=stmt,
                params=params
            )

    items = db.scalars(stmt).all()

    current_page = params.page if not params.get_all else 1
    items_per_page = params.limit if not params.get_all else total_items
    total_pages = ceil(total_items / params.limit) if not params.get_all else 1

    return {
        "items": items,
        "meta": {
            "current_page": current_page,
            "items_per_page": items_per_page,
            "total_pages": total_pages,
            "total_items": total_items
        }
    }


async def paginate_async(
        db: AsyncSession,
        stmt: Select,
        params: PaginationParams
) -> dict[str, Any]:
    total_items = await db.scalar(select(func.count()).select_from(stmt))

    if not params.get_all:
        offset = (params.page - 1) * params.limit
        stmt = stmt.offset(offset=offset).limit(limit=params.limit)

    items = (await db.scalars(stmt)).all()

    current_page = params.page if not params.get_all else 1
    items_per_page = params.limit if not params.get_all else total_items
    total_pages = ceil(total_items / params.limit) if not params.get_all else 1

    return {
        "items": items,
        "meta": {
            "current_page": current_page,
            "items_per_page": items_per_page,
            "total_pages": total_pages,
            "total_items": total_items
        }
    }

