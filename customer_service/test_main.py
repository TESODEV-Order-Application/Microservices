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
    
    # Validate that the response is a UUID string
    response_uuid = response.json()
    try:
        UUID(response_uuid, version=4)
        is_valid_uuid = True
    except ValueError:
        is_valid_uuid = False
    
    assert is_valid_uuid, "The response is not a valid UUID"
    assert mock_mongodb["customers"].insert_one.called