from typing import Generator, Callable

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import sessionmaker, Session

from .examples.app import create_app
from .examples.models import Base
from .examples.seed import seed_db


@pytest.fixture(scope="session")
def sqlite_file_path(tmp_path_factory):
    file_path = tmp_path_factory.mktemp("data") / "fastapi_query_test.sqlite"
    yield file_path


@pytest.fixture(scope="session")
def database_url(sqlite_file_path) -> str:
    return f"sqlite:///{sqlite_file_path}"


@pytest.fixture(scope="session")
def async_database_url(sqlite_file_path: str) -> str:
    return f"sqlite+aiosqlite:///{sqlite_file_path}"


@pytest.fixture(scope="session")
def engine(database_url: str) -> Generator[Engine, None, None]:
    engine = create_engine(database_url)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with sessionmaker(engine, autoflush=True, class_=Session)() as db:
        seed_db(db=db)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def async_engine(async_database_url: str, engine: Engine) -> AsyncEngine:
    return create_async_engine(async_database_url)


@pytest.fixture(scope="session")
def session_constructor(engine: Engine) -> Callable:
    return sessionmaker(engine, autoflush=True, class_=Session)


@pytest.fixture(scope="function")
def db(session_constructor: Callable) -> Generator[Session, None, None]:
    with session_constructor() as db:
        yield db


@pytest_asyncio.fixture(scope="function")
async def async_db(async_engine: AsyncEngine) -> Generator[AsyncSession, None, None]:
    SessionLocal = async_sessionmaker(  # noqa
        bind=async_engine,
        autoflush=True,
        class_=AsyncSession
    )
    async with SessionLocal() as db:
        yield db


@pytest.fixture(scope="module")
def app(session_constructor):
    return create_app(
        session_constructor=session_constructor
    )


@pytest.fixture(scope="module")
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
