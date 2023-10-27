from fastapi.testclient import TestClient


def test_get_all_products(client: TestClient) -> None:
    """Test Pagination - Get All Products"""
    response = client.get(
        url="/products",
        params={
            "get_all": True
        }
    )

    data = response.json()

    assert data["meta"]["current_page"] == 1
    assert data["meta"]["items_per_page"] == 6
    assert data["meta"]["total_pages"] == 1
    assert data["meta"]["total_items"] == 6
    assert len(data["items"]) == 6


def test_get_page(client: TestClient) -> None:
    """Test Pagination - Get Page"""
    response = client.get(
        url="/products",
        params={
            "page": 1,
            "size": 2,
            "get_all": False
        }
    )

    data = response.json()

    assert data["meta"]["current_page"] == 1
    assert data["meta"]["items_per_page"] == 2
    assert data["meta"]["total_pages"] == 3
    assert data["meta"]["total_items"] == 6
    assert len(data["items"]) == 2


def test_with_ordering(client: TestClient) -> None:
    """Test Pagination - With Ordering"""
    response = client.get(
        url="/products",
        params={
            "page": 1,
            "size": 2,
            "get_all": False,
            "order_by": "-price"
        }
    )

    data = response.json()

    assert data["meta"]["current_page"] == 1
    assert data["meta"]["items_per_page"] == 2
    assert data["meta"]["total_pages"] == 3
    assert data["meta"]["total_items"] == 6
    assert len(data["items"]) == 2


def test_with_filtering(client: TestClient) -> None:
    """Test Pagination - With Filtering"""
    response = client.get(
        url="/products",
        params={
            "page": 1,
            "size": 2,
            "get_all": False,
            "price__gt": 2000,
            "categories__id__in": "1,2,3"
        }
    )

    data = response.json()

    assert data["meta"]["current_page"] == 1
    assert data["meta"]["items_per_page"] == 2
    assert data["meta"]["total_pages"] == 1
    assert data["meta"]["total_items"] == 2
    assert len(data["items"]) == 2


