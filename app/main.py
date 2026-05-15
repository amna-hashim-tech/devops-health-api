from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import platform
import datetime
import httpx
import asyncio

app = FastAPI(title="DevOps Status Monitor")

APP_VERSION = "5.0.0"
START_TIME = datetime.datetime.now()

SERVICES = {
    "github": {
        "name": "GitHub",
        "url": "https://github.com",
        "threshold_ms": 600
    },
    "dockerhub": {
        "name": "Docker Hub",
        "url": "https://hub.docker.com",
        "threshold_ms": 800
    },
    "azure": {
        "name": "Azure Cloud",
        "url": "https://azure.microsoft.com",
        "threshold_ms": 800
    },
    "cloudflare": {
        "name": "Cloudflare",
        "url": "https://1.1.1.1",
        "threshold_ms": 300
    },
    "googlecloud": {
        "name": "Google Cloud",
        "url": "https://cloud.google.com",
        "threshold_ms": 700
    },
    "aws": {
        "name": "AWS",
        "url": "https://aws.amazon.com",
        "threshold_ms": 700
    },
}

incident_log = []

async def check_service(svc_id: str, svc: dict) -> dict:
    start = datetime.datetime.now()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get(svc["url"])
        elapsed = int(
            (datetime.datetime.now() - start).total_seconds() * 1000
        )
        status = "degraded" if elapsed > svc["threshold_ms"] else "healthy"
    except Exception:
        elapsed = -1
        status = "down"

    return {
        "id": svc_id,
        "name": svc["name"],
        "url": svc["url"],
        "status": status,
        "response_ms": elapsed,
        "threshold_ms": svc["threshold_ms"],
    }

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
async def get_services():
    tasks = [
        check_service(svc_id, svc)
        for svc_id, svc in SERVICES.items()
    ]
    results = await asyncio.gather(*tasks)
    return {"services": list(results)}

@app.post("/api/incident/{service_id}")
def log_incident(service_id: str, note: str = "Manual incident"):
    incident_log.append({
        "service": service_id,
        "note": note,
        "timestamp": datetime.datetime.now().isoformat(),
    })
    return {"message": "Incident logged"}

@app.get("/api/incidents")
def get_incidents():
    return {"incidents": list(reversed(incident_log[-20:]))}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_path = os.path.join(
        os.path.dirname(__file__), "dashboard.html"
    )
    with open(html_path, "r") as f:
        return f.read()