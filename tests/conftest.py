import pytest
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client
    del client  # Ensure client is deleted after tests
    del app  # Ensure app is deleted after tests
