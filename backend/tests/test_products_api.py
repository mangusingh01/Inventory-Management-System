from fastapi.testclient import TestClient


def test_create_product(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Barcode Scanner",
            "sku": "SCAN-001",
            "description": "USB scanner",
            "quantity": 12,
            "price": "79.99",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Barcode Scanner"
    assert body["sku"] == "SCAN-001"
    assert body["quantity"] == 12
    assert body["price"] == "79.99"


def test_create_product_rejects_duplicate_sku(client: TestClient) -> None:
    payload = {
        "name": "Packing Tape",
        "sku": "TAPE-001",
        "description": None,
        "quantity": 100,
        "price": "3.50",
    }

    first_response = client.post("/api/v1/products", json=payload)
    second_response = client.post("/api/v1/products", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "A product with this SKU already exists."


def test_create_product_rejects_negative_quantity(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Shelf Bin",
            "sku": "BIN-001",
            "description": None,
            "quantity": -1,
            "price": "8.25",
        },
    )

    assert response.status_code == 422


def test_list_and_get_products(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Shipping Label",
            "sku": "LABEL-001",
            "description": "Thermal label roll",
            "quantity": 60,
            "price": "12.00",
        },
    )
    product_id = create_response.json()["id"]

    list_response = client.get("/api/v1/products")
    get_response = client.get(f"/api/v1/products/{product_id}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert get_response.status_code == 200
    assert get_response.json()["sku"] == "LABEL-001"


def test_update_product(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Warehouse Cart",
            "sku": "CART-001",
            "description": None,
            "quantity": 4,
            "price": "180.00",
        },
    )
    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Warehouse Cart XL",
            "quantity": 6,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Warehouse Cart XL"
    assert body["quantity"] == 6
    assert body["sku"] == "CART-001"


def test_update_product_rejects_empty_payload(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Inventory Scale",
            "sku": "SCALE-001",
            "description": None,
            "quantity": 2,
            "price": "250.00",
        },
    )
    product_id = create_response.json()["id"]

    response = client.put(f"/api/v1/products/{product_id}", json={})

    assert response.status_code == 422
    assert response.json()["detail"] == "At least one product field must be provided."


def test_update_product_rejects_null_required_field(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Inventory Tablet",
            "sku": "TABLET-001",
            "description": None,
            "quantity": 3,
            "price": "320.00",
        },
    )
    product_id = create_response.json()["id"]

    response = client.put(f"/api/v1/products/{product_id}", json={"sku": None})

    assert response.status_code == 422


def test_delete_product(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/products",
        json={
            "name": "Pallet Wrap",
            "sku": "WRAP-001",
            "description": None,
            "quantity": 20,
            "price": "15.75",
        },
    )
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/products/{product_id}")
    get_response = client.get(f"/api/v1/products/{product_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
