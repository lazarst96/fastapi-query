from typing import Iterator, Callable, Optional

from fastapi import FastAPI, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from fastapi_query.ext.sqlalchemy import paginate
from fastapi_query.filtering import Filter
from fastapi_query.pagination import Paginate, Paginated, PaginationParams
from .models import Product
from .schemas import ProductOut, ProductFilters


def create_app(
        session_constructor: Callable
) -> FastAPI:
    app = FastAPI()

    def get_db() -> Iterator[Session]:
        with session_constructor() as session:
            yield session

    @app.get(
        path="/products",
        response_model=Paginated[ProductOut]
    )
    def get_products(
            db: Session = Depends(get_db),
            pagination_params: PaginationParams = Paginate(),
            filter_params: ProductFilters = Filter(ProductFilters),
            order_by: Optional[str] = Query(default=None)
    ):
        stmt = select(
            Product
        ).options(
            selectinload(Product.categories)
        ).where(
            Product.deleted_at.is_(None)
        )

        return paginate(
            db=db,
            model_class=Product,
            stmt=stmt,
            pagination_params=pagination_params,
            filter_params=filter_params,
            ordering_params=order_by
        )

    return app
