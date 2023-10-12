from typing import List, Optional, Generator

from fastapi import FastAPI, Query, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload

from fastapi_query.ext.sqlalchemy import (
    apply_filters,
    apply_ordering,
    paginate_async as paginate
)
from fastapi_query.filtering import Filter
from fastapi_query.pagination import Paginate, PaginationParams, Paginated
from .models import User, Base, Paper
from .schemas import UserFilters, UserOut, PaperFilters, PaperOut
from .utils import seed_db

app = FastAPI()

engine = create_async_engine("postgresql+asyncpg:///fastapi-query-db")
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def get_db() -> Generator[AsyncSession, None, None]:
    async with SessionLocal() as db:
        yield db


@app.post(
    path="/seed"
)
async def seed_test_data(
        db: AsyncSession = Depends(get_db),
):
    await seed_db(db=db)

    return {
        "msg": "OK"
    }


@app.get(
    path="/users",
    response_model=Paginated[UserOut]
)
async def get_all_users(
        db: AsyncSession = Depends(get_db),
        filter_params: UserFilters = Filter(UserFilters),
        pagination_params: PaginationParams = Paginate(),
        order_by: Optional[str] = Query(default=None)
):

    stmt = select(User).options(
        selectinload(User.tags),
        joinedload(User.shipping_address),
        joinedload(User.billing_address),
    )

    return await paginate(
        db=db,
        model_class=User,
        stmt=stmt,
        pagination_params=pagination_params,
        filter_params=filter_params,
        ordering_params=order_by
    )


@app.get(
    path="/papers",
    response_model=List[PaperOut]
)
async def get_all_papers(
        db: AsyncSession = Depends(get_db),
        filter_params: PaperFilters = Filter(PaperFilters),
        order_by: Optional[str] = Query(default=None)
):
    stmt = select(Paper).options(
        selectinload(Paper.tags),
        joinedload(Paper.author)
    )

    stmt = apply_filters(
        model_class=Paper,
        stmt=stmt,
        filters=filter_params
    )

    stmt = apply_ordering(
        model_class=Paper,
        stmt=stmt,
        order_by=order_by
    )

    return (await db.scalars(stmt)).all()


@app.on_event("startup")
async def startup():
    print("Creating Database Tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
