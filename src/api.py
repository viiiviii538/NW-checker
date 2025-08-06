from __future__ import annotations

import asyncio
import os
from contextlib import suppress
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .dynamic_scan import capture, analyze, storage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_TOKEN = os.getenv("API_TOKEN")


async def verify_token(authorization: str | None = Header(default=None)) -> None:
    if API_TOKEN and authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


class StartParams(BaseModel):
    interface: Optional[str] = None
    duration: Optional[int] = None
    approved_macs: Optional[list[str]] = None


scan_queue: asyncio.Queue | None = None
capture_task: asyncio.Task | None = None
analyse_task: asyncio.Task | None = None
storage_obj = storage.Storage()


@app.post("/scan/dynamic/start")
async def start_scan(params: StartParams, _: None = Depends(verify_token)):
    global scan_queue, capture_task, analyse_task, storage_obj
    if capture_task or analyse_task:
        return {"status": "already_running"}
    scan_queue = asyncio.Queue()
    storage_obj = storage.Storage()
    capture_task = asyncio.create_task(
        capture.capture_packets(
            scan_queue,
            interface=params.interface,
            duration=params.duration,
        )
    )
    analyse_task = asyncio.create_task(
        analyze.analyse_packets(
            scan_queue,
            storage_obj,
            approved_macs=params.approved_macs or [],
        )
    )
    return {"status": "started"}


@app.post("/scan/dynamic/stop")
async def stop_scan(_: None = Depends(verify_token)):
    global capture_task, analyse_task
    for task in (capture_task, analyse_task):
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    capture_task = analyse_task = None
    return {"status": "stopped"}


@app.get("/scan/dynamic/results")
async def get_results(_: None = Depends(verify_token)):
    return {"results": storage_obj.get_all()}


@app.websocket("/ws/scan/dynamic")
async def ws_dynamic_scan(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    storage_obj.add_listener(queue)
    try:
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        pass
    finally:
        storage_obj.remove_listener(queue)

