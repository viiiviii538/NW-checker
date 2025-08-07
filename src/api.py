from __future__ import annotations

import asyncio
import os
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .dynamic_scan import scheduler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_TOKEN = os.getenv("API_TOKEN")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if API_TOKEN:
            auth = request.headers.get("Authorization")
            if auth != f"Bearer {API_TOKEN}":
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)


app.add_middleware(AuthMiddleware)


class StartParams(BaseModel):
    interface: Optional[str] = None
    duration: Optional[int] = None
    approved_macs: Optional[list[str]] = None
    interval: Optional[int] = None


scan_scheduler = scheduler.DynamicScanScheduler()


@app.post("/scan/dynamic/start")
async def start_scan(params: StartParams):
    if scan_scheduler.job:
        return {"status": "already_running"}
    scan_scheduler.start(
        interface=params.interface,
        duration=params.duration,
        approved_macs=params.approved_macs or [],
        interval=params.interval or 3600,
    )
    return {"status": "scheduled"}


@app.post("/scan/dynamic/stop")
async def stop_scan():
    await scan_scheduler.stop()
    return {"status": "stopped"}


@app.get("/scan/dynamic/results")
async def get_results():
    return {"results": scan_scheduler.storage.get_all()}


@app.get("/scan/dynamic/history")
async def get_history(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    device: Optional[str] = None,
    protocol: Optional[str] = None,
):
    filters = {"start": start, "end": end, "device": device, "protocol": protocol}
    filters = {k: v for k, v in filters.items() if v is not None}
    return {"results": scan_scheduler.storage.fetch_history(filters)}


@app.websocket("/ws/scan/dynamic")
async def ws_dynamic_scan(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    scan_scheduler.storage.add_listener(queue)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        pass
    finally:
        scan_scheduler.storage.remove_listener(queue)

