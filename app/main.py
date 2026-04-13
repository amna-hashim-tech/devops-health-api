from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import platform
import datetime
import random

app = FastAPI(title="Multi-Service Status Dashboard")

APP_VERSION = "2.0.0"
START_TIME = datetime.datetime.now()

SERVICES = {
    "api-gateway": {"name": "API Gateway", "base_ms": 45},
    "database": {"name": "PostgreSQL Database", "base_ms": 12},
    "storage": {"name": "Blob Storage", "base_ms": 30},
    "auth-service": {"name": "Auth Service", "base_ms": 25},
    "payment": {"name": "Payment Gateway", "base_ms": 60},
}

incidents = {}

@app.get("/health")
def health_check():
    uptime = datetime.datetime.now() - START_TIME
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "environment": os.getenv("ENVIRONMENT", "local"),
        "hostname": platform.node(),
        "git_commit": os.getenv("GIT_COMMIT", "unknown"),
        "uptime_seconds": int(uptime.total_seconds()),
    }

@app.get("/api/services")
def get_services():
    result = []
    for svc_id, svc in SERVICES.items():
        if svc_id in incidents:
            status = incidents[svc_id]
            response_ms = random.randint(800, 3000) if status == "degraded" else -1
            uptime = 94.5 if status == "degraded" else 0.0
        else:
            status = "healthy"
            response_ms = svc["base_ms"] + random.randint(-5, 15)
            uptime = round(random.uniform(99.5, 99.99), 2)
        result.append({
            "id": svc_id,
            "name": svc["name"],
            "status": status,
            "response_ms": response_ms,
            "uptime_pct": uptime,
        })
    return {"services": result}

@app.post("/api/incident/{service_id}/{status}")
def set_incident(service_id: str, status: str):
    if service_id not in SERVICES:
        return {"error": "Service not found"}
    if status == "healthy":
        incidents.pop(service_id, None)
    else:
        incidents[service_id] = status
    return {"message": f"{service_id} set to {status}"}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_path = os.path.join(
        os.path.dirname(__file__), "dashboard.html"
    )
    with open(html_path, "r") as f:
        return f.read()