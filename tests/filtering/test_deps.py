from fastapi.testclient import TestClient


def test_filter_dependency(client: TestClient) -> None:
    response = client.get(
        url="/self",
        params={
            "id": 1,
            "username__contains": "user"
        }
    )

    assert response.is_success

    data = response.json()
    assert data["id"] == 1
    assert data["username__contains"] == "user"
