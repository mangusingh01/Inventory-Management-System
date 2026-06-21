from fastapi.testclient import TestClient


def create_customer(client: TestClient, email: str) -> int:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Dashboard",
            "last_name": "Buyer",
            "email": email,
            "phone": None,
            "company": None,
        },
    )
    return response.json()["id"]


def create_product(
    client: TestClient,
    sku: str,
    quantity: int,
    price: str,
) -> int:
    response = client.post(
        "/api/v1/products",
        json={
            "name": f"Dashboard {sku}",
            "sku": sku,
            "description": None,
            "quantity": quantity,
            "price": price,
        },
    )
    return response.json()["id"]


def create_order(
    client: TestClient,
    customer_id: int,
    product_id: int,
    quantity: int,
) -> int:
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": quantity}],
        },
    )
    return response.json()["id"]


def test_dashboard_returns_empty_summary(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["total_products"] == 0
    assert body["total_customers"] == 0
    assert body["total_orders"] == 0
    assert body["total_inventory_units"] == 0
    assert body["active_order_value"] == "0.00"
    assert body["fulfilled_revenue"] == "0.00"
    assert body["low_stock_products"] == []
    assert body["recent_orders"] == []


def test_dashboard_returns_operational_summary(client: TestClient) -> None:
    customer_id = create_customer(client, "dashboard.buyer@example.com")
    low_stock_product_id = create_product(client, "DASH-LOW", quantity=4, price="6.00")
    stocked_product_id = create_product(client, "DASH-STOCKED", quantity=20, price="10.00")

    fulfilled_order_id = create_order(client, customer_id, stocked_product_id, quantity=2)
    pending_order_id = create_order(client, customer_id, low_stock_product_id, quantity=1)
    fulfilled_response = client.put(
        f"/api/v1/orders/{fulfilled_order_id}",
        json={"status": "fulfilled"},
    )

    response = client.get("/api/v1/dashboard")

    assert fulfilled_response.status_code == 200
    assert response.status_code == 200
    body = response.json()
    assert body["total_products"] == 2
    assert body["total_customers"] == 1
    assert body["total_orders"] == 2
    assert body["total_inventory_units"] == 21
    assert body["low_stock_threshold"] == 5
    assert body["low_stock_product_count"] == 1
    assert body["pending_order_count"] == 1
    assert body["fulfilled_order_count"] == 1
    assert body["cancelled_order_count"] == 0
    assert body["active_order_value"] == "26.00"
    assert body["fulfilled_revenue"] == "20.00"
    assert body["low_stock_products"][0]["id"] == low_stock_product_id
    assert body["recent_orders"][0]["id"] == pending_order_id
