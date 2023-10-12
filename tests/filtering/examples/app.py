from fastapi import FastAPI

from fastapi_query.filtering import Filter
from .schemas import UserFilters


def create_app():
    app = FastAPI()

    @app.get("/self")
    def get_filters(
            filter_params: UserFilters = Filter(UserFilters)
    ):
        return filter_params

    return app
