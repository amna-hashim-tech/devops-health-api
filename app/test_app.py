from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"

def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Service Status Dashboard" in response.text

def test_services():
    response = client.get("/api/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data["services"]) == 5
    for svc in data["services"]:
        assert svc["status"] == "healthy"

def test_incident():
    response = client.post("/api/incident/database/down")
    assert response.status_code == 200
    services = client.get("/api/services").json()
    db = [s for s in services["services"] if s["id"] == "database"][0]
    assert db["status"] == "down"
    client.post("/api/incident/database/healthy")