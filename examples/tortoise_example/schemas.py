from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from fastapi_query.filtering import BaseFilterParams


class NestedPaperFilters(BaseFilterParams):
    id: Optional[int] = None


class TournamentFilters(BaseFilterParams):
    search: Optional[str] = None
    id: Optional[int] = None
    id__in: Optional[List[int]] = None
    name: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None

    class Settings(BaseFilterParams.Settings):
        searchable_fields = ["id", "name"]


class TournamentNestedFilters(BaseFilterParams):
    id: Optional[int] = None


class EventFilters(BaseFilterParams):
    search: Optional[str] = None
    id: Optional[int] = None
    id__in: Optional[List[int]] = None
    name: Optional[str] = None
    name__icontains: Optional[str] = None

    tournament: Optional[TournamentNestedFilters] = None

    class Settings(BaseFilterParams.Settings):
        searchable_fields = ["name", "tournament__name"]


class TournamentOut(BaseModel):
    id: int
    name: str
    created_at: datetime


class TeamOut(BaseModel):
    id: int
    name: str


class EventOut(BaseModel):
    id: int
    name: str
    modified_at: datetime
    tournament: TournamentOut
    participants: List[TeamOut]
    prize: Optional[float] = None

