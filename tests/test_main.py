import pytest
from fastapi.testclient import TestClient
from scrollintel.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_placeholder():
    assert 1 + 1 == 2 