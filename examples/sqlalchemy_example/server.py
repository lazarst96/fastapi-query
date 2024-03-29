from typing import List, Optional

from fastapi import FastAPI, Query, Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session, selectinload, joinedload

from fastapi_query.ext.sqlalchemy import apply_filters, paginate, apply_ordering
from fastapi_query.filtering import Filter
from fastapi_query.pagination import Paginate, PaginationParams, Paginated
from .models import User, Base, Paper
from .schemas import UserFilters, UserOut, PaperFilters, PaperOut
from .utils import seed_db

app = FastAPI()

engine = create_engine("postgresql:///fastapi-query-db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post(
    path="/seed"
)
def seed_test_data(
        db: Session = Depends(get_db),
):
    """Fills the Database with the test data"""
    seed_db(db=db)

    return {
        "msg": "OK"
    }


@app.get(
    path="/users",
    response_model=Paginated[UserOut]
)
def get_all_users(
        db: Session = Depends(get_db),
        filter_params: UserFilters = Filter(UserFilters),
        pagination_params: PaginationParams = Paginate(),
        order_by: Optional[str] = Query(default=None)
):
    """Returns Paginated List of all Users"""

    stmt = select(User).options(
        selectinload(User.tags),
        joinedload(User.shipping_address),
        joinedload(User.billing_address),
    )

    return paginate(
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
def get_all_papers(
        db: Session = Depends(get_db),
        filter_params: PaperFilters = Filter(PaperFilters),
        order_by: Optional[str] = Query(default=None)
):
    """Returns Non-Paginated List of all Papers"""

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

    return db.scalars(stmt).all()


@app.on_event("startup")
def startup():
    print("Creating Database Tables")
    Base.metadata.create_all(bind=engine)
