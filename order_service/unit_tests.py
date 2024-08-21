import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch, AsyncMock
from bson import Binary
from uuid import uuid4, UUID

from main import app

# Create a TestClient for the app
client = TestClient(app)

# Mock MongoDB collection
@pytest.fixture
def mock_mongodb():
    with patch("app.routes.mongodb.collections") as mock_db:
        mock_db["orders"].insert_one = AsyncMock()
        yield mock_db

#customer
##################CREATE##################
# Test the order creation route
from unittest.mock import patch, AsyncMock

@patch("app.routes.publishMessage")  # Mock the publishMessage function
def test_create_order(mock_publish, mock_mongodb):
    order_id = uuid4()
    
    # Mock the return value of the find_one operation to simulate that the customer exists with a valid address
    mock_mongodb["customers"].find_one = AsyncMock(return_value={
        "address": {
            "addressLine": "123 Main St",
            "city": "Sample City",
            "country": "Sample Country",
            "cityCode": 12345
        }
    })
    
    # Mock the insert_one operation to simulate successful order creation
    mock_mongodb["orders"].insert_one = AsyncMock()

    response = client.post("/order/", json={
        "customerId": str(order_id),
        "quantity": 1,
        "price": 100.0,
        "status": "pending",
        "product": {
            "id": str(uuid4()),
            "name": "Product1",
            "imageUrl": "http://example.com/product1.png"
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
    assert mock_mongodb["orders"].insert_one.called
    assert mock_publish.called  # Ensure the publishMessage function was called
##########################################

"""
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
"""


##################DELETE##################
# Test the customer delete route
def test_delete_order(mock_mongodb):
    order_id = uuid4()

    # Mock the return value of the delete operation
    mock_mongodb["orders"].delete_one = AsyncMock(return_value=AsyncMock(deleted_count=1))

    response = client.delete(f"/order/{order_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure the delete_one method was called with the correct parameters
    mock_mongodb["orders"].delete_one.assert_called_once_with({"id": Binary.from_uuid(order_id)})
##########################################


##################GETALL##################
# Test the getAll orders route for a successful case with orders present
def test_get_all_orders(mock_mongodb):
    # Mock the return value of the find operation
    mock1 = {
        "id": str(uuid4()),
        "customerId": str(uuid4()),
        "quantity": 1,
        "price": 100.0,
        "status": "pending",
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        },
        "product": {
            "id": str(uuid4()),
            "name": "Product1",
            "imageUrl": "http://example.com/product1.png"
        },
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    mock2 = {
        "id": str(uuid4()),
        "customerId": str(uuid4()),
        "quantity": 2,
        "price": 200.0,
        "status": "shipped",
        "address": {
            "addressLine": "456 Elm St",
            "city": "Gotham",
            "country": "Wonderland",
            "cityCode": 67890
        },
        "product": {
            "id": str(uuid4()),
            "name": "Product2",
            "imageUrl": "http://example.com/product2.png"
        },
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }
    mock_find = MagicMock()
    mock_find.to_list = AsyncMock(return_value=[
        mock1,
        mock2
    ])
    mock_mongodb["orders"].find.return_value = mock_find

    response = client.get("/order/")

    assert response.status_code == 200

    # Check that the returned order list matches the mock data
    response_data = response.json()
    assert len(response_data) == 2
    
    # Verify that the specific fields match the mock data
    assert response_data[0]["quantity"] == mock1["quantity"]
    assert response_data[0]["price"] == mock1["price"]
    assert response_data[0]["status"] == mock1["status"]
    assert response_data[0]["address"]["city"] == mock1["address"]["city"]
    assert response_data[0]["product"]["name"] == mock1["product"]["name"]
    
    assert response_data[1]["quantity"] == mock2["quantity"]
    assert response_data[1]["price"] == mock2["price"]
    assert response_data[1]["status"] == mock2["status"]
    assert response_data[1]["address"]["city"] == mock2["address"]["city"]
    assert response_data[1]["product"]["name"] == mock2["product"]["name"]

    # Ensure find and to_list methods were called correctly
    mock_mongodb["orders"].find.assert_called_once_with({}, {"_id": 0})
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
    mock_mongodb["customers"].find.assert_called_once_with({}, {"_id": 0})
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
        },
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
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
    assert "createdAt" in response_data
    assert "updatedAt" in response_data

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

#################VALİDATE##################
# Test the customer validation route for a case where the customer exists
def test_validate_customer_exists(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find_one operation to simulate that the customer exists
    mock_mongodb["customers"].find_one = AsyncMock(return_value={
        "id": Binary.from_uuid(customer_id),
        "name": "John Doe",
        "email": "johndoe@example.com"
    })

    response = client.get(f"/customer/validate/{customer_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(customer_id)}, {"_id": 0}
    )

# Test the customer validation route for a case where the customer does not exist
def test_validate_customer_not_exists(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find_one operation to simulate that the customer does not exist
    mock_mongodb["customers"].find_one = AsyncMock(return_value=None)

    response = client.get(f"/customer/validate/{customer_id}")

    assert response.status_code == 200
    assert response.json() is False

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(customer_id)}, {"_id": 0}
    )
##########################################
"""