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
    
    # Mock the return value of the find_one operation to simulate that the order exists with a valid address
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

##################UPDATE##################
# Test the order update route for a successful case
def test_update_order_success(mock_mongodb):
    order_id = uuid4()
    customer_id = uuid4()
    product_id = uuid4()

    # Mock the return value of the find_one operation to simulate that the customer exists with a valid address
    mock_mongodb["customers"].find_one = AsyncMock(return_value={
        "address": {
            "addressLine": "123 Main St",
            "city": "Metropolis",
            "country": "Wonderland",
            "cityCode": 12345
        }
    })

    # Mock the return value of the update_one operation to simulate a successful update
    mock_mongodb["orders"].update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

    # The data to update the order
    update_data = {
        "customerId": str(customer_id),
        "quantity": 2,
        "price": 150.0,
        "status": "processing",
        "product": {
            "id": str(product_id),
            "name": "Product2",
            "imageUrl": "http://example.com/product2.png"
        }
    }

    response = client.put(f"/order/{order_id}", json=update_data)

    assert response.status_code == 200
    assert response.json() is True

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with({"id": Binary.from_uuid(customer_id)}, {"address": 1})

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once()
    updated_order = mock_mongodb["orders"].update_one.call_args[0][1]["$set"]
    assert updated_order["quantity"] == 2
    assert updated_order["price"] == 150.0
    assert updated_order["status"] == "processing"
    assert updated_order["address"]["city"] == "Metropolis"
    assert updated_order["product"]["id"] == Binary.from_uuid(product_id)

# Test the order update route for a case where the customer is not found
def test_update_order_customer_not_found(mock_mongodb):
    order_id = uuid4()
    customer_id = uuid4()
    product_id = uuid4()

    # Mock the return value of the find_one operation to simulate customer not found
    mock_mongodb["customers"].find_one = AsyncMock(return_value=None)

    # The data to update the order
    update_data = {
        "customerId": str(customer_id),
        "quantity": 2,
        "price": 150.0,
        "status": "processing",
        "product": {
            "id": str(product_id),
            "name": "Product2",
            "imageUrl": "http://example.com/product2.png"
        }
    }

    response = client.put(f"/order/{order_id}", json=update_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Customer not found"}

    # Ensure find_one was called with the correct parameters
    mock_mongodb["customers"].find_one.assert_called_once_with({"id": Binary.from_uuid(customer_id)}, {"address": 1})

    # Ensure update_one was not called since the customer was not found
    mock_mongodb["orders"].update_one.assert_not_called()
##########################################

##################DELETE##################
# Test the order delete route
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


# Test the getAll orders route for a case where no orders are found
def test_get_all_orders_empty(mock_mongodb):
    # Mock the return value of the find operation to return an empty list
    mock_mongodb["orders"].find.return_value.to_list = AsyncMock(return_value=[])

    response = client.get("/order/")

    assert response.status_code == 200

    # Check that the returned order list is empty
    response_data = response.json()
    assert response_data == []

    # Ensure find and to_list methods were called correctly
    mock_mongodb["orders"].find.assert_called_once_with({}, {"_id": 0})
    mock_mongodb["orders"].find().to_list.assert_called_once_with(length=None)
##########################################

################GETBYORDER################
# Test the order retrieval route By Order ID for a successful case
def test_get_order_success(mock_mongodb):
    order_id = uuid4()

    # Mock the return value of the find_one operation
    mock_mongodb["orders"].find_one = AsyncMock(return_value={
        "id": Binary.from_uuid(order_id),
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
    })

    response = client.get(f"/order/getByOrder/{order_id}")

    assert response.status_code == 200

    # Check that the returned order data matches the mock data
    response_data = response.json()
    assert response_data["id"] == str(order_id)
    assert response_data["customerId"]
    assert response_data["quantity"] == 1
    assert response_data["price"] == 100.0
    assert response_data["status"] == "pending"
    assert response_data["address"]["addressLine"] == "123 Main St"
    assert response_data["address"]["city"] == "Metropolis"
    assert response_data["product"]["name"] == "Product1"
    assert "createdAt" in response_data
    assert "updatedAt" in response_data

    # Ensure find_one was called with the correct parameters
    mock_mongodb["orders"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}, {"_id": 0}
    )

# Test the order retrieval route By Order ID for a case where the order is not found
def test_get_order_not_found(mock_mongodb):
    order_id = uuid4()

    # Mock the return value of the find_one operation to simulate not found
    mock_mongodb["orders"].find_one = AsyncMock(return_value=None)

    response = client.get(f"/order/getByOrder/{order_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}

    # Ensure find_one was called with the correct parameters
    mock_mongodb["orders"].find_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}, {"_id": 0}
    )

##########################################

################GETBYCUSTOMER################
# Test the order retrieval route By Customer ID for a successful case
def test_get_orders_by_customer_success(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find operation
    mock_order_1 = {
        "id": str(uuid4()),
        "customerId": str(customer_id),
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
    mock_order_2 = {
        "id": str(uuid4()),
        "customerId": str(customer_id),
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
        mock_order_1,
        mock_order_2
    ])
    mock_mongodb["orders"].find.return_value = mock_find

    response = client.get(f"/order/getByCustomer/{customer_id}")

    assert response.status_code == 200

    # Check that the returned order list matches the mock data
    response_data = response.json()
    assert len(response_data) == 2
    
    # Verify that the specific fields match the mock data
    assert response_data[0]["quantity"] == mock_order_1["quantity"]
    assert response_data[0]["price"] == mock_order_1["price"]
    assert response_data[0]["status"] == mock_order_1["status"]
    assert response_data[0]["address"]["city"] == mock_order_1["address"]["city"]
    assert response_data[0]["product"]["name"] == mock_order_1["product"]["name"]
    
    assert response_data[1]["quantity"] == mock_order_2["quantity"]
    assert response_data[1]["price"] == mock_order_2["price"]
    assert response_data[1]["status"] == mock_order_2["status"]
    assert response_data[1]["address"]["city"] == mock_order_2["address"]["city"]
    assert response_data[1]["product"]["name"] == mock_order_2["product"]["name"]

    # Ensure find and to_list methods were called correctly
    mock_mongodb["orders"].find.assert_called_once_with({"customerId": Binary.from_uuid(customer_id)}, {"_id": 0})
    mock_find.to_list.assert_called_once_with(length=None)

# Test the order retrieval route By Customer ID for a case where no orders are found
def test_get_orders_by_customer_not_found(mock_mongodb):
    customer_id = uuid4()

    # Mock the return value of the find operation to return an empty list
    mock_mongodb["orders"].find.return_value.to_list = AsyncMock(return_value=[])

    response = client.get(f"/order/getByCustomer/{customer_id}")

    assert response.status_code == 200

    # Check that the returned order list is empty
    response_data = response.json()
    assert response_data == []

    # Ensure find and to_list methods were called correctly
    mock_mongodb["orders"].find.assert_called_once_with({"customerId": Binary.from_uuid(customer_id)}, {"_id": 0})
    mock_mongodb["orders"].find().to_list.assert_called_once_with(length=None)

##########################################

#################CHANGESTATUS##################
# Test the order status change route for a successful case
def test_change_order_status_success(mock_mongodb):
    order_id = uuid4()
    new_status = "shipped"

    # Mock the return value of the update_one operation to simulate a successful update
    mock_mongodb["orders"].update_one = AsyncMock(return_value=AsyncMock(matched_count=1))

    response = client.put(f"/order/changeStatus/{order_id}?status={new_status}")

    assert response.status_code == 200
    assert response.json() is True

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}, {"$set": {"status": new_status}}, upsert=False
    )

# Test the order status change route for a case where the order is not found
def test_change_order_status_not_found(mock_mongodb):
    order_id = uuid4()
    new_status = "shipped"

    # Mock the return value of the update_one operation to simulate a failure (no matching order found)
    mock_mongodb["orders"].update_one = AsyncMock(return_value=AsyncMock(matched_count=0))

    response = client.put(f"/order/changeStatus/{order_id}?status={new_status}")

    assert response.status_code == 200
    assert response.json() is False

    # Ensure update_one was called with the correct parameters
    mock_mongodb["orders"].update_one.assert_called_once_with(
        {"id": Binary.from_uuid(order_id)}, {"$set": {"status": new_status}}, upsert=False
    )
##########################################
