import pytest
from fastapi.testclient import TestClient
from main import app
from app.routes import router

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

"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
from app.models import UpdateCustomer

client = TestClient(app)


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
"""