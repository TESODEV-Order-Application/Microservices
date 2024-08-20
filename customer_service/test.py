
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
from app.models import UpdateCustomer

client = TestClient(app)

@pytest.mark.asyncio
async def test_create_customer():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a sample customer data
        customer_data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "address": "123 Main Street"
        }
        
        # Send a POST request to create a new customer
        response = await ac.post("/customer/", json=customer_data)
        
        # Assert that the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Assert that the response contains a valid UUID
        customer_id = response.json()
        assert isinstance(customer_id, str)
        assert len(customer_id) == 36  # UUID is 36 characters long

        # Here you can add more assertions to verify that the customer
        # was correctly inserted into the database (mocking DB interaction).
