from fastapi import Depends

from .schemas import PaginationParams


def Paginate() -> PaginationParams: # noqa
    return Depends(PaginationParams)
