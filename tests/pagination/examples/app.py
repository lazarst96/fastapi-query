from fastapi import FastAPI

from fastapi_query.pagination import PaginationParams, Paginate


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/self")
    def get_filters(
            pagination_params: PaginationParams = Paginate()
    ):
        return pagination_params

    return app
