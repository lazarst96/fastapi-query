from fastapi.testclient import TestClient


def test_paginate_dependency(client: TestClient) -> None:
    params = {
        "page": 1,
        "size": 20,
        "get_all": False
    }

    response = client.get(
        url="/self",
        params=params
    )

    assert response.is_success

    data = response.json()
    assert data == params
