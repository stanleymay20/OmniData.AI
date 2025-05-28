from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_scroll_chat():
    response = client.post("/scroll-chat", json={"message": "test"})
    assert response.status_code == 200
    assert response.json() == {"reply": "Scroll Scribe received: test"} 