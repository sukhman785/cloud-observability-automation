from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.storage import Storage

app = FastAPI(title="Cloud Observability API", version="0.2.0")
storage = Storage(db_path=os.getenv("DB_PATH", "data/observability.db"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "healthy" if storage.healthcheck() else "unhealthy"}


@app.get("/alerts")
def get_alerts(limit: int = Query(default=100, ge=1, le=1000)) -> dict:
    return {"items": storage.get_alerts(limit=limit)}


@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str) -> Dict[str, Any]:
    updated = storage.update_alert_status(alert_id=alert_id, status="ACKNOWLEDGED")
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"item": updated}


@app.post("/alerts/{alert_id}/suppress")
def suppress_alert(alert_id: str) -> Dict[str, Any]:
    updated = storage.update_alert_status(alert_id=alert_id, status="SUPPRESSED")
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"item": updated}


@app.get("/logs")
def get_logs(limit: int = Query(default=200, ge=1, le=2000)) -> dict:
    return {"items": storage.get_logs(limit=limit)}


@app.get("/metrics/summary")
def get_metrics_summary() -> dict:
    return storage.get_metrics_summary()


@app.websocket("/ws/alerts")
async def alerts_ws(websocket: WebSocket):
    await websocket.accept()
    last_seen_id = storage.get_latest_alert_row_id()

    # Send initial snapshot so UI has deterministic startup state.
    await websocket.send_json({"type": "snapshot", "items": storage.get_alerts(limit=100)})

    try:
        while True:
            latest_id = storage.get_latest_alert_row_id()
            if latest_id > last_seen_id:
                items = storage.get_alerts_since_id(after_id=last_seen_id, limit=200)
                if items:
                    await websocket.send_json({"type": "delta", "items": items})
                    last_seen_id = items[-1]["id"]

            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
