from typing import List, Optional

from fastapi import FastAPI

from fastapi_query.filtering import Filter, BaseFilterParams, WithPrefix
from fastapi_query.pagination import Paginate, PageParams

app = FastAPI()


class TagFilters(BaseFilterParams):
    name: Optional[str] = None
    name__ilike: Optional[str] = None


class ItemFilters(BaseFilterParams):
    id: Optional[int] = None
    id__in: Optional[List[int]] = None
    title: Optional[str] = None
    title__ilike: Optional[str] = None
    tag: WithPrefix(TagFilters, prefix="tags") | None = None


@app.get(
    path='/items',
    response_model=List
)
async def get_all_items(
        filter_params: ItemFilters = Filter(ItemFilters),
        pagination_params: PageParams = Paginate()
):
    print(pagination_params)
    print(filter_params)

    return []
