from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.product import Product


def create_customer(client: TestClient) -> int:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Order",
            "last_name": "Buyer",
            "email": "order.buyer@example.com",
            "phone": None,
            "company": None,
        },
    )
    return response.json()["id"]


def create_product(client: TestClient, sku: str, quantity: int = 10, price: str = "5.50") -> int:
    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Product {sku}",
            "sku": sku,
            "description": None,
            "quantity": quantity,
            "price": price,
        },
    )
    return response.json()["id"]


def test_create_order_calculates_total_and_reduces_inventory(
    client: TestClient,
    db_session: Session,
) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client, "ORDER-001", quantity=10, price="7.25")

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 3}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer_id
    assert body["status"] == "pending"
    assert body["total_amount"] == "21.75"
    assert body["items"][0]["unit_price"] == "7.25"
    assert body["items"][0]["line_total"] == "21.75"
    assert db_session.get(Product, product_id).quantity == 7


def test_create_order_combines_duplicate_product_items(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client, "ORDER-002", quantity=10, price="2.00")

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {"product_id": product_id, "quantity": 2},
                {"product_id": product_id, "quantity": 3},
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_amount"] == "10.00"
    assert body["items"][0]["quantity"] == 5


def test_create_order_rejects_missing_customer(client: TestClient) -> None:
    product_id = create_product(client, "ORDER-003")

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": 999,
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found."


def test_create_order_rejects_insufficient_stock(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client, "ORDER-004", quantity=1)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 2}],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == f"Insufficient stock for products: [{product_id}]."


def test_list_and_get_orders(client: TestClient) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client, "ORDER-005")
    create_response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    order_id = create_response.json()["id"]

    list_response = client.get("/api/v1/orders")
    get_response = client.get(f"/api/v1/orders/{order_id}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert get_response.status_code == 200
    assert get_response.json()["id"] == order_id


def test_cancel_order_restores_inventory(client: TestClient, db_session: Session) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client, "ORDER-006", quantity=5)
    create_response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 4}],
        },
    )
    order_id = create_response.json()["id"]

    response = client.put(f"/api/v1/orders/{order_id}", json={"status": "cancelled"})

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert db_session.get(Product, product_id).quantity == 5


def test_delete_order_restores_inventory(client: TestClient, db_session: Session) -> None:
    customer_id = create_customer(client)
    product_id = create_product(client, "ORDER-007", quantity=6)
    create_response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 2}],
        },
    )
    order_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/orders/{order_id}")
    get_response = client.get(f"/api/v1/orders/{order_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
    assert db_session.get(Product, product_id).quantity == 6
