from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "5.0.0"

def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "DevOps Status Monitor" in response.text

def test_services():
    response = client.get("/api/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data["services"]) == 6

def test_incident_log():
    response = client.post("/api/incident/github?note=Test incident")
    assert response.status_code == 200
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["incidents"]) >= 1