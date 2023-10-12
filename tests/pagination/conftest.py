from typing import Generator

import pytest
from fastapi.testclient import TestClient

from .examples.app import create_app


@pytest.fixture(scope="module")
def app():
    return create_app()


@pytest.fixture(scope="module")
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
