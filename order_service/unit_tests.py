import pytest
from uuid import uuid4
from bson import Binary
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Mock the MongoDB client
@pytest.fixture
def mock_mongodb(monkeypatch):
    mock_db = {
        "orders": AsyncMock(),
        "customers": AsyncMock()
    }
    monkeypatch.setattr("app.MongoDB.mongodb.collections", mock_db)
    return mock_db

########################## CREATE ORDER ##########################
# Test the create order route for a case where the customer exists
def test_create_order_customer_exists(mock_mongodb):
    customer_id = uuid4()
    order_id = uuid4()

    # Mock the return value of the find_one operation to simulate that the customer exists
    mock_mongodb["customers"].find_one = AsyncMock(return_value={"address": "123 Main St"})

    # Mock the insert_one operation to simulate successful order creation
    mock_mongodb["orders"].insert_one = AsyncMock()

    response = client.post("/order/", json={
        "customerId": str(customer_id),
        "product": {"id": str(uuid4()), "name": "Product1"},
        "quantity": 1,
        "status": "pending",  # Assuming status is required
        "totalPrice": 100.0   # Assuming totalPrice is required
    })

    assert response.status_code == 200
    assert isinstance(response.json(), str)  # Should return the order UUID as a string

    # Ensure find_one and insert_one were called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with({"id": Binary.from_uuid(customer_id)}, {"address": 1})
    mock_mongodb["orders"].insert_one.assert_called_once()

# Test the create order route for a case where the customer does not exist
def test_create_order_customer_not_exists(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find_one operation to simulate that the customer does not exist
    mock_mongodb["customers"].find_one = AsyncMock(return_value=None)

    response = client.post("/order/", json={
        "customerId": str(customer_id),
        "product": {"id": str(uuid4()), "name": "Product1"},
        "quantity": 1
    })

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with({"id": Binary.from_uuid(customer_id)}, {"address": 1})

########################## UPDATE ORDER ##########################
def test_update_order(mock_mongodb):
    order_id = uuid4()

    # Mock the update_one operation to simulate a successful update
    mock_mongodb["orders"].update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

    response = client.put(f"/order/{order_id}", json={
        "customerId": str(uuid4()),
        "product": {"id": str(uuid4()), "name": "Product1"},
        "quantity": 2
    })

    assert response.status_code == 200
    assert response.json() is True

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once()

########################## DELETE ORDER ##########################
def test_delete_order(mock_mongodb):
    order_id = uuid4()

    # Mock the delete_one operation to simulate a successful deletion
    mock_mongodb["orders"].delete_one = AsyncMock(return_value=AsyncMock(deleted_count=1))

    response = client.delete(f"/order/{order_id}")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure delete_one was called with the correct parameters
    mock_mongodb["orders"].delete_one.assert_called_once_with({"id": Binary.from_uuid(order_id)})

########################## GET ALL ORDERS ##########################
def test_get_all_orders(mock_mongodb):
    # Mock the find operation to return a list of orders
    mock_mongodb["orders"].find = AsyncMock(return_value=[{"id": str(uuid4()), "product": {"id": str(uuid4()), "name": "Product1"}, "quantity": 1}])

    response = client.get("/order/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Should return a list of orders

    # Ensure find was called
    mock_mongodb["orders"].find.assert_called_once_with({}, {"_id": 0})

########################## GET ORDERS BY CUSTOMER ##########################
def test_get_orders_by_customer(mock_mongodb):
    customer_id = uuid4()

    # Mock the find operation to return a list of orders for the customer
    mock_mongodb["orders"].find = AsyncMock(return_value=[{"id": str(uuid4()), "product": {"id": str(uuid4()), "name": "Product1"}, "quantity": 1}])

    response = client.get(f"/order/getByCustomer/{customer_id}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Should return a list of orders

    # Ensure find was called with the correct parameters
    mock_mongodb["orders"].find.assert_called_once_with({"customerId": Binary.from_uuid(customer_id)}, {"_id": 0})

########################## GET ORDER BY ORDER ID ##########################
def test_get_order_by_order_id(mock_mongodb):
    order_id = uuid4()

    # Mock the find_one operation to simulate that the order exists
    mock_mongodb["orders"].find_one = AsyncMock(return_value={"id": str(order_id), "product": {"id": str(uuid4()), "name": "Product1"}, "quantity": 1})

    response = client.get(f"/order/getByOrder/{order_id}")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)  # Should return the order as a dictionary

    # Ensure find_one was called with the correct parameters
    mock_mongodb["orders"].find_one.assert_called_once_with({"id": Binary.from_uuid(order_id)}, {"_id": 0})

########################## CHANGE ORDER STATUS ##########################
def test_change_order_status(mock_mongodb):
    order_id = uuid4()

    # Mock the update_one operation to simulate a successful status update
    mock_mongodb["orders"].update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

    response = client.put(f"/order/changeStatus/{order_id}", json="shipped")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}, {"$set": {"status": "shipped"}}, upsert=False
    )