from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.product import Product


def create_customer(client: TestClient, email: str) -> int:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Inventory",
            "last_name": "Buyer",
            "email": email,
            "phone": None,
            "company": None,
        },
    )
    return response.json()["id"]


def create_product(client: TestClient, sku: str, quantity: int, price: str = "10.00") -> int:
    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Inventory {sku}",
            "sku": sku,
            "description": None,
            "quantity": quantity,
            "price": price,
        },
    )
    return response.json()["id"]


def get_quantity(db_session: Session, product_id: int) -> int:
    return db_session.get(Product, product_id).quantity


def test_failed_order_does_not_reduce_inventory(
    client: TestClient,
    db_session: Session,
) -> None:
    customer_id = create_customer(client, "inventory.failed@example.com")
    product_id = create_product(client, "INV-FAILED", quantity=2)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 3}],
        },
    )

    assert response.status_code == 409
    assert get_quantity(db_session, product_id) == 2


def test_failed_multi_item_order_does_not_partially_reduce_inventory(
    client: TestClient,
    db_session: Session,
) -> None:
    customer_id = create_customer(client, "inventory.partial@example.com")
    in_stock_product_id = create_product(client, "INV-IN-STOCK", quantity=5)
    low_stock_product_id = create_product(client, "INV-LOW-STOCK", quantity=1)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {"product_id": in_stock_product_id, "quantity": 2},
                {"product_id": low_stock_product_id, "quantity": 2},
            ],
        },
    )

    assert response.status_code == 409
    assert get_quantity(db_session, in_stock_product_id) == 5
    assert get_quantity(db_session, low_stock_product_id) == 1


def test_cancelled_order_reactivation_requires_available_stock(
    client: TestClient,
    db_session: Session,
) -> None:
    first_customer_id = create_customer(client, "inventory.first@example.com")
    second_customer_id = create_customer(client, "inventory.second@example.com")
    product_id = create_product(client, "INV-REACTIVATE", quantity=2)

    first_order = client.post(
        "/api/v1/orders",
        json={
            "customer_id": first_customer_id,
            "items": [{"product_id": product_id, "quantity": 2}],
        },
    ).json()
    cancel_response = client.put(
        f"/api/v1/orders/{first_order['id']}",
        json={"status": "cancelled"},
    )
    second_order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": second_customer_id,
            "items": [{"product_id": product_id, "quantity": 2}],
        },
    )
    reactivate_response = client.put(
        f"/api/v1/orders/{first_order['id']}",
        json={"status": "pending"},
    )

    assert cancel_response.status_code == 200
    assert second_order_response.status_code == 201
    assert reactivate_response.status_code == 409
    assert reactivate_response.json()["detail"] == (
        f"Insufficient stock for products: [{product_id}]."
    )
    assert get_quantity(db_session, product_id) == 0


def test_deleting_cancelled_order_does_not_restore_inventory_twice(
    client: TestClient,
    db_session: Session,
) -> None:
    customer_id = create_customer(client, "inventory.cancelled-delete@example.com")
    product_id = create_product(client, "INV-CANCEL-DELETE", quantity=4)
    order = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 3}],
        },
    ).json()

    cancel_response = client.put(
        f"/api/v1/orders/{order['id']}",
        json={"status": "cancelled"},
    )
    delete_response = client.delete(f"/api/v1/orders/{order['id']}")

    assert cancel_response.status_code == 200
    assert delete_response.status_code == 204
    assert get_quantity(db_session, product_id) == 4


def test_missing_product_order_does_not_reduce_existing_inventory(
    client: TestClient,
    db_session: Session,
) -> None:
    customer_id = create_customer(client, "inventory.missing-product@example.com")
    product_id = create_product(client, "INV-MISSING", quantity=8)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {"product_id": product_id, "quantity": 2},
                {"product_id": 9999, "quantity": 1},
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Products not found: [9999]."
    assert get_quantity(db_session, product_id) == 8
