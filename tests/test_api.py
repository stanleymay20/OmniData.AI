import pytest
from fastapi.testclient import TestClient
from scrollintel.api.main import app
from scrollintel.core.auth import create_access_token

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_prophecy_endpoint():
    # Create test token
    token = create_access_token({"sub": "testuser", "role": "scroll-user"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/prophecy/chat",
        headers=headers,
        json={"message": "What will happen tomorrow?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "forecast" in data

def test_webhook_endpoints():
    # Create admin token
    token = create_access_token({"sub": "admin", "role": "scroll-admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test adding webhook
    webhook_data = {
        "url": "https://hooks.slack.com/test",
        "platform": "slack",
        "secret": "test-secret"
    }
    response = client.post("/webhook/add", headers=headers, json=webhook_data)
    assert response.status_code == 200
    
    # Test broadcasting
    message_data = {
        "content": "Test insight",
        "forecast": {
            "prediction": "Test prediction",
            "confidence": 85,
            "timeframe": "24h"
        },
        "timestamp": "2024-03-20T12:00:00Z"
    }
    response = client.post("/webhook/broadcast", headers=headers, json=message_data)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_auth_endpoints():
    # Test login
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    
    # Test token verification
    token = data["token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/verify", headers=headers)
    assert response.status_code == 200
    assert "user" in response.json()

def test_rate_limiting():
    # Create test token
    token = create_access_token({"sub": "testuser", "role": "scroll-user"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make multiple requests
    for _ in range(11):  # Assuming limit is 10
        response = client.post(
            "/prophecy/chat",
            headers=headers,
            json={"message": "Test message"}
        )
    
    # Last request should be rate limited
    assert response.status_code == 429 