import pytest
from fastapi.testclient import TestClient
from main import app
from app.routes import router

from unittest.mock import patch, AsyncMock
from bson import Binary
from uuid import uuid4, UUID

# Create a TestClient for the app
client = TestClient(app)

# Mock MongoDB collection
@pytest.fixture
def mock_mongodb():
    with patch("app.routes.mongodb.collections") as mock_db:
        mock_db["customers"].insert_one = AsyncMock()
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
    
    response_uuid = response.json()
    try:
        UUID(response_uuid, version=4)
        is_valid_uuid = True
    except ValueError:
        is_valid_uuid = False
    
    assert is_valid_uuid, "The response is not a valid UUID"
    assert mock_mongodb["customers"].insert_one.called


# Test the customer update route
def test_update_customer(mock_mongodb):
    customer_id = uuid4()

    mock_mongodb["customers"].update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

    response = client.put(f"/customer/{customer_id}", json={
        "name": "Jane Doe",
        "email": "janedoe@example.com",
        "address": {
            "addressLine": "456 Elm St",
            "city": "Gotham",
            "country": "Wonderland",
            "cityCode": 67890
        }
    })

    assert response.status_code == 200
    assert response.json() is True

    # Ensure the update_one method was called with the correct parameters
    mock_mongodb["customers"].update_one.assert_called_once()
    
    called_args = mock_mongodb["customers"].update_one.call_args[0]
    assert called_args[0] == {"id": Binary.from_uuid(customer_id)}
    
    # Check that the "updatedAt" field was added
    updated_data = called_args[1]["$set"]
    assert "updatedAt" in updated_data
    assert updated_data["name"] == "Jane Doe"
    assert updated_data["email"] == "janedoe@example.com"
    assert updated_data["address"]["addressLine"] == "456 Elm St"


# Test the customer delete route
def test_delete_customer(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the delete operation
    mock_mongodb["customers"].delete_one = AsyncMock(return_value=AsyncMock(deleted_count=1))

    response = client.delete(f"/customer/{customer_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure the delete_one method was called with the correct parameters
    mock_mongodb["customers"].delete_one.assert_called_once_with({"id": Binary.from_uuid(customer_id)})