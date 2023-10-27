from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise.queryset import QuerySet

from fastapi_query.ext.tortoise import apply_filters, paginate
from fastapi_query.filtering import Filter
from fastapi_query.pagination import Paginated, PaginationParams, Paginate
from .models import Tournament, Event
from .schemas import TournamentFilters, EventFilters, EventOut

app = FastAPI()

register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["examples.tortoise_example.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get(
    path="/tournaments"
)
async def get_tournaments(
        filter_params: TournamentFilters = Filter(TournamentFilters)
):
    queryset = apply_filters(
        queryset=QuerySet(model=Tournament),
        filters=filter_params
    )

    print(await queryset.all())

    return {
        "msg": "OK"
    }


@app.get(
    path="/events",
    response_model=Paginated[EventOut]
)
async def get_events(
        pagination_params: PaginationParams = Paginate(),
        filter_params: EventFilters = Filter(EventFilters)
):
    queryset = QuerySet(
        model=Event
    ).select_related(
        "tournament"
    ).prefetch_related(
        "participants"
    )

    return await paginate(
        queryset=queryset,
        pagination_params=pagination_params,
        filter_params=filter_params
    )
