import asyncio
from typing import Generator

import pytest
from _pytest.tmpdir import TempPathFactory
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tortoise import Tortoise

from .examples.app import create_app
from .examples.seed import seed_db


async def init_database(database_url: str) -> None:
    module_path = ".".join([*__name__.split(".")[:-1], "examples.models"])
    await Tortoise.init(
        db_url=database_url,
        modules={"models": [module_path]},
        _create_db=True,
    )
    await Tortoise.generate_schemas()

    # Seed db
    await seed_db()


async def drop_database() -> None:
    await Tortoise._drop_databases()  # noqa


@pytest.fixture(scope="module")
def sqlite_file_path(tmp_path_factory: TempPathFactory):
    file_path = tmp_path_factory.mktemp("data") / "fastapi_query_tortoise.sqlite"
    yield file_path


@pytest.fixture(scope="module")
def database_url(sqlite_file_path: str) -> str:
    return f"sqlite:///{sqlite_file_path}"


@pytest.fixture(scope="module", autouse=True)
def init_tests(database_url: str) -> Generator[None, None, None]:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        init_database(database_url=database_url)
    )

    yield

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        drop_database()
    )


@pytest.fixture(scope="module")
def app(database_url: str) -> FastAPI:
    return create_app()


@pytest.fixture(scope="module")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
