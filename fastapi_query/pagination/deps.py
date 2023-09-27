from typing import Literal

from fastapi import Depends

from .schemas import PageParams, LimitOffsetParams

PaginationStrategy = Literal['page', 'limit-offset']


def Paginate(  # noqa
        strategy: PaginationStrategy = 'page'
):
    if strategy == 'page':
        params_schema = PageParams
    else:
        params_schema = LimitOffsetParams

    return Depends(params_schema)
