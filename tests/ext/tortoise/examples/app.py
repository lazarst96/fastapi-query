from typing import Optional

from fastapi import FastAPI, Query
from tortoise.queryset import QuerySet

from fastapi_query.ext.tortoise import paginate
from fastapi_query.filtering import Filter
from fastapi_query.pagination import Paginate, Paginated, PaginationParams
from .models import Product
from .schemas import ProductOut, ProductFilters


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get(
        path="/products",
        response_model=Paginated[ProductOut]
    )
    async def get_products(
            pagination_params: PaginationParams = Paginate(),
            filter_params: ProductFilters = Filter(ProductFilters),
            order_by: Optional[str] = Query(default=None)
    ):
        queryset = QuerySet(
            model=Product
        ).prefetch_related(
            "categories"
        ).filter(
            deleted_at=None
        )

        return await paginate(
            queryset=queryset,
            pagination_params=pagination_params,
            filter_params=filter_params,
            ordering_params=order_by
        )

    return app
