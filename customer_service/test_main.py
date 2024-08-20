import pytest
from fastapi.testclient import TestClient
from main import app
from app.routes import router
from typing import List
from fastapi import HTTPException
from datetime import datetime

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


##################CREATE##################
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
##########################################

##################UPDATE##################
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
##########################################

##################DELETE##################
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
##########################################

##################GETALL##################
from unittest.mock import MagicMock

# Test the getAll customers route for a successful case with customers present
def test_get_all_customers(mock_mongodb):
    # Mock the return value of the find operation
    mock1 = {
        "id": str(uuid4()),
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        },
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    mock2 = {
        "id": str(uuid4()),
        "name": "Jane Doe",
        "email": "janedoe@example.com",
        "address": {
            "addressLine": "456 Elm St",
            "city": "Gotham",
            "country": "Wonderland",
            "cityCode": 67890
        },
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    mock_find = MagicMock()
    mock_find.to_list = AsyncMock(return_value=[
        mock1,
        mock2
    ])
    mock_mongodb["customers"].find.return_value = mock_find

    response = client.get("/customer/")

    assert response.status_code == 200

    # Check that the returned customer list matches the mock data
    response_data = response.json()
    assert len(response_data) == 2
    
    # Verify that the specific fields match the mock data
    assert response_data[0]["name"] == mock1["name"]
    assert response_data[0]["email"] == mock1["email"]
    assert response_data[0]["address"]["city"] == mock1["address"]["city"]
    
    assert response_data[1]["name"] == mock2["name"]
    assert response_data[1]["email"] == mock2["email"]
    assert response_data[1]["address"]["city"] == mock2["address"]["city"]

    # Ensure find and to_list methods were called correctly
    mock_mongodb["customers"].find.assert_called_once_with({}, {"_id": 0, "name": 0})
    mock_find.to_list.assert_called_once_with(length=None)

# Test the getAll customers route for a case where no customers are found
def test_get_all_customers_empty(mock_mongodb):
    # Mock the return value of the find operation to return an empty list
    mock_mongodb["customers"].find.return_value.to_list = AsyncMock(return_value=[])

    response = client.get("/customer/")

    assert response.status_code == 200

    # Check that the returned customer list is empty
    response_data = response.json()
    assert response_data == []

    # Ensure find and to_list methods were called correctly
    mock_mongodb["customers"].find.assert_called_once_with({}, {"_id": 0, "name": 0})
    mock_mongodb["customers"].find().to_list.assert_called_once_with(length=None)
##########################################

"""
##################GET#####################
# Test the customer retrieval route for a successful case
def test_get_customer_success(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find_one operation
    mock_mongodb["customers"].find_one = AsyncMock(return_value={
        "id": Binary.from_uuid(customer_id),
        "name": "John Doe",
        "email": "johndoe@example.com",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        }
    })

    response = client.get(f"/customer/{customer_id}")

    assert response.status_code == 200

    # Check that the returned customer data matches the mock data
    response_data = response.json()
    assert response_data["id"] == str(customer_id)
    assert response_data["name"] == "John Doe"
    assert response_data["email"] == "johndoe@example.com"
    assert response_data["address"]["addressLine"] == "123 Main St"
    assert response_data["address"]["city"] == "Metropolis"

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(customer_id)}, {"_id": 0}
    )

# Test the customer retrieval route for a case where the customer is not found
def test_get_customer_not_found(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find_one operation to simulate not found
    mock_mongodb["customers"].find_one = AsyncMock(return_value=None)

    response = client.get(f"/customer/{customer_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(customer_id)}, {"_id": 0}
    )
##########################################
"""