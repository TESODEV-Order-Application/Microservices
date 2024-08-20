import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID
from bson import Binary
from datetime import datetime
from main import app

client = TestClient(app)

@pytest.fixture
def mock_mongodb():
    with patch("app.routes.mongodb.collections") as mock_db:
        mock_db["customers"].find_one = AsyncMock()
        mock_db["orders"].insert_one = AsyncMock()
        mock_db["orders"].update_one = AsyncMock()
        mock_db["orders"].delete_one = AsyncMock()
        mock_db["orders"].find = AsyncMock()
        yield mock_db
"""
@patch("app.routes.RabbitMQ.publishMessage")
def test_create_order(mock_publish_message, mock_mongodb):
    customer_id = uuid4()
    product_id = uuid4()

    # Mock the MongoDB find_one response for the customer lookup
    mock_mongodb["customers"].find_one.return_value = {
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        }
    }

    # Sample UpdateOrder payload
    order_payload = {
        "customerId": str(customer_id),
        "product": {
            "id": str(product_id),
            "name": "Sample Product",
            "quantity": 1,
            "price": 100.0
        },
        "status": "Pending"
    }

    response = client.post("/order/", json=order_payload)

    assert response.status_code == 200
    response_uuid = response.json()

    # Validate that the response is a valid UUID
    try:
        UUID(response_uuid, version=4)
        is_valid_uuid = True
    except ValueError:
        is_valid_uuid = False
    
    assert is_valid_uuid, "The response is not a valid UUID"

    # Check that MongoDB operations were called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(customer_id)},
        {"address": 1}
    )
    mock_mongodb["orders"].insert_one.assert_called_once()
    
    # Check that publishMessage was called with the correct parameters
    mock_publish_message.assert_called_once_with(mock_mongodb["orders"].insert_one.call_args[0][0])

    # Validate the inserted order fields
    inserted_order = mock_mongodb["orders"].insert_one.call_args[0][0]
    assert inserted_order["customerId"] == Binary.from_uuid(customer_id)
    assert inserted_order["product"]["id"] == Binary.from_uuid(product_id)
    assert "createdAt" in inserted_order
    assert "updatedAt" in inserted_order
"""

"""
##################UPDATE##################
# Test the order update route with a successful update
def test_update_order_success(mock_mongodb):
    order_id = uuid4()

    # Mock the update_one operation to simulate a successful update
    mock_mongodb["orders"].update_one.return_value = AsyncMock(matched_count=1)

    # Sample UpdateOrder payload
    order_payload = {
        "customerId": str(uuid4()),  # New customer ID
        "product": {
            "id": str(uuid4()),
            "name": "Updated Product",
            "quantity": 2,
            "price": 150.0
        },
        "status": "Shipped"
    }

    response = client.put(f"/order/{order_id}", json=order_payload)

    assert response.status_code == 200
    assert response.json() is True

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)},
        {"$set": order_payload | {"updatedAt": datetime.utcnow()}}
    )

# Test the order update route with no orders found to update
def test_update_order_not_found(mock_mongodb):
    order_id = uuid4()

    # Mock the update_one operation to simulate no orders found to update
    mock_mongodb["orders"].update_one.return_value = AsyncMock(matched_count=0)

    # Sample UpdateOrder payload
    order_payload = {
        "customerId": str(uuid4()),
        "product": {
            "id": str(uuid4()),
            "name": "Updated Product",
            "quantity": 2,
            "price": 150.0
        },
        "status": "Shipped"
    }

    response = client.put(f"/order/{order_id}", json=order_payload)

    assert response.status_code == 200
    assert response.json() is False

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)},
        {"$set": order_payload | {"updatedAt": datetime.utcnow()}}
    )
##########################################
"""

##################DELETE##################
# Test the order delete route with a successful deletion
def test_delete_order_success(mock_mongodb):
    order_id = uuid4()

    # Mock the delete_one operation to simulate a successful deletion
    mock_mongodb["orders"].delete_one.return_value = AsyncMock(deleted_count=1)

    response = client.delete(f"/order/{order_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure delete_one was called with the correct parameters
    mock_mongodb["orders"].delete_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}
    )

# Test the order delete route with no orders found to delete
def test_delete_order_not_found(mock_mongodb):
    order_id = uuid4()

    # Mock the delete_one operation to simulate a deletion where no documents were deleted
    mock_mongodb["orders"].delete_one.return_value = AsyncMock(deleted_count=0)

    response = client.delete(f"/order/{order_id}")

    assert response.status_code == 200
    assert response.json() is False

    # Ensure delete_one was called with the correct parameters
    mock_mongodb["orders"].delete_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}
    )
##########################################

##################GETALL##################
def test_get_all_orders(mock_mongodb):
    # Mock the find operation to return a list of orders
    mock_mongodb["orders"].find.return_value.to_list = AsyncMock(return_value=[
        {
            "id": str(uuid4()),
            "customerId": str(uuid4()),
            "product": {
                "id": str(uuid4()),
                "name": "Product 1",
                "quantity": 1,
                "price": 100.0
            },
            "status": "Pending",
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid4()),
            "customerId": str(uuid4()),
            "product": {
                "id": str(uuid4()),
                "name": "Product 2",
                "quantity": 2,
                "price": 150.0
            },
            "status": "Shipped",
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat()
        }
    ])

    response = client.get("/order/")

    assert response.status_code == 200

    # Check that the returned order list matches the mock data
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["product"]["name"] == "Product 1"
    assert response_data[1]["product"]["name"] == "Product 2"

    # Ensure find was called correctly
    mock_mongodb["orders"].find.assert_called_once_with({})
    mock_mongodb["orders"].find.return_value.to_list.assert_called_once_with(length=None)
##########################################