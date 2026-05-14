from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import platform
import datetime
import httpx
import asyncio

app = FastAPI(title="Multi-Service Status Dashboard")

APP_VERSION = "3.0.0"
START_TIME = datetime.datetime.now()

SERVICES = {
    "azure": {
        "name": "Azure Cloud",
        "url": "https://azure.microsoft.com",
        "threshold_ms": 800
    },
    "github": {
        "name": "GitHub",
        "url": "https://github.com",
        "threshold_ms": 600
    },
    "google": {
        "name": "Google APIs",
        "url": "https://www.google.com",
        "threshold_ms": 400
    },
    "cloudflare": {
        "name": "Cloudflare DNS",
        "url": "https://1.1.1.1",
        "threshold_ms": 300
    },
    "microsoft": {
        "name": "Microsoft 365",
        "url": "https://www.microsoft.com",
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
        if elapsed > svc["threshold_ms"]:
            status = "degraded"
        else:
            status = "healthy"
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
        "checked_at": datetime.datetime.now().isoformat(),
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