from fastapi.testclient import TestClient


def test_create_customer(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Avery",
            "last_name": "Shah",
            "email": "avery.shah@example.com",
            "phone": "+1-555-0101",
            "company": "Northwind Supply",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["first_name"] == "Avery"
    assert body["last_name"] == "Shah"
    assert body["email"] == "avery.shah@example.com"
    assert body["phone"] == "+1-555-0101"
    assert body["company"] == "Northwind Supply"


def test_create_customer_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "first_name": "Mira",
        "last_name": "Kapoor",
        "email": "mira.kapoor@example.com",
        "phone": None,
        "company": None,
    }

    first_response = client.post("/api/v1/customers", json=payload)
    second_response = client.post("/api/v1/customers", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "A customer with this email already exists."


def test_create_customer_rejects_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Jordan",
            "last_name": "Lee",
            "email": "not-an-email",
            "phone": None,
            "company": None,
        },
    )

    assert response.status_code == 422


def test_list_and_get_customers(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Nia",
            "last_name": "Patel",
            "email": "nia.patel@example.com",
            "phone": "+1-555-0102",
            "company": "Warehouse Works",
        },
    )
    customer_id = create_response.json()["id"]

    list_response = client.get("/api/v1/customers")
    get_response = client.get(f"/api/v1/customers/{customer_id}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert get_response.status_code == 200
    assert get_response.json()["email"] == "nia.patel@example.com"


def test_update_customer(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Sam",
            "last_name": "Rivera",
            "email": "sam.rivera@example.com",
            "phone": None,
            "company": None,
        },
    )
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/customers/{customer_id}",
        json={
            "first_name": "Samantha",
            "company": "Fulfillment Co",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Samantha"
    assert body["last_name"] == "Rivera"
    assert body["company"] == "Fulfillment Co"


def test_update_customer_rejects_empty_payload(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Dev",
            "last_name": "Morgan",
            "email": "dev.morgan@example.com",
            "phone": None,
            "company": None,
        },
    )
    customer_id = create_response.json()["id"]

    response = client.put(f"/api/v1/customers/{customer_id}", json={})

    assert response.status_code == 422
    assert response.json()["detail"] == "At least one customer field must be provided."


def test_update_customer_rejects_null_required_field(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Riley",
            "last_name": "Chen",
            "email": "riley.chen@example.com",
            "phone": None,
            "company": None,
        },
    )
    customer_id = create_response.json()["id"]

    response = client.put(f"/api/v1/customers/{customer_id}", json={"email": None})

    assert response.status_code == 422


def test_delete_customer(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/customers",
        json={
            "first_name": "Priya",
            "last_name": "Raman",
            "email": "priya.raman@example.com",
            "phone": None,
            "company": None,
        },
    )
    customer_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/customers/{customer_id}")
    get_response = client.get(f"/api/v1/customers/{customer_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
