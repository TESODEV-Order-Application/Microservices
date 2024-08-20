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
        mock_db["customers"].insert_one = AsyncMock()
        yield mock_db


##################CREATE##################

##########################################



