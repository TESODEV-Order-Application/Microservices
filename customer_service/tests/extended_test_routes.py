
import pytest
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI instance is in main.py
from app.routes import router  # Importing the router

from unittest.mock import patch
from bson import Binary
from uuid import uuid4

# Create a TestClient for the app
client = TestClient(app)

# Mock MongoDB collection
@pytest.fixture
def mock_mongodb():
    with patch("app.routes.mongodb.collections") as mock_db:
        yield mock_db

# Test the customer creation route
def test_create_customer(mock_mongodb):
    response = client.post("/customer/", json={
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        }
    })

    assert response.status_code == 200
    assert "uuid" in response.json()

    # Check that the insert_one was called on the MongoDB collection
    assert mock_mongodb["customers"].insert_one.called

# Test the customer update route
def test_update_customer(mock_mongodb):
    customer_id = uuid4()
    binary_customer_id = Binary.from_uuid(customer_id)
    
    mock_mongodb["customers"].update_one.return_value.matched_count = 1

    response = client.put(f"/customer/{customer_id}", json={
        "name": "Jane Doe",
        "email": "janedoe@example.com",
        "address": {
            "addressLine": "456 Another St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 67890
        }
    })

    assert response.status_code == 200
    assert response.json() is True

    # Check that the update_one was called on the MongoDB collection
    assert mock_mongodb["customers"].update_one.called

# Test the customer deletion route
def test_delete_customer(mock_mongodb):
    customer_id = uuid4()
    binary_customer_id = Binary.from_uuid(customer_id)

    mock_mongodb["customers"].delete_one.return_value.deleted_count = 1

    response = client.delete(f"/customer/{customer_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Check that the delete_one was called on the MongoDB collection
    assert mock_mongodb["customers"].delete_one.called

# Test getting all customers
def test_get_all_customers(mock_mongodb):
    mock_mongodb["customers"].find.return_value.to_list.return_value = [{
        "id": uuid4(),
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        },
        "createdAt": "2024-08-20T12:34:56.123456",
        "updatedAt": "2024-08-20T12:34:56.123456"
    }]

    response = client.get("/customer/")

    assert response.status_code == 200
    assert len(response.json()) > 0

    # Check that the find was called on the MongoDB collection
    assert mock_mongodb["customers"].find.called

# Test getting a specific customer by ID
def test_get_customer_by_id(mock_mongodb):
    customer_id = uuid4()
    binary_customer_id = Binary.from_uuid(customer_id)

    mock_mongodb["customers"].find_one.return_value = {
        "id": customer_id,
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        },
        "createdAt": "2024-08-20T12:34:56.123456",
        "updatedAt": "2024-08-20T12:34:56.123456"
    }

    response = client.get(f"/customer/{customer_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(customer_id)

    # Check that the find_one was called on the MongoDB collection
    assert mock_mongodb["customers"].find_one.called

# Test validating customer existence
def test_validate_customer(mock_mongodb):
    customer_id = uuid4()
    binary_customer_id = Binary.from_uuid(customer_id)

    mock_mongodb["customers"].find_one.return_value = {
        "id": customer_id,
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        }
    }

    response = client.get(f"/customer/validate/{customer_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Check that the find_one was called on the MongoDB collection
    assert mock_mongodb["customers"].find_one.called
