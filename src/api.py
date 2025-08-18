from __future__ import annotations

import asyncio
import os
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .dynamic_scan import scheduler, analyze

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
        # ✅ /health は常に許可（外形監視・LB用のため）
        if request.url.path == "/health":
            return await call_next(request)

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


# 新形式のエンドポイント (/dynamic-scan/*) へのエイリアス
@app.post("/dynamic-scan/start")
async def start_scan_v2(params: StartParams):
    """動的スキャン開始エイリアス

    旧エンドポイント `/scan/dynamic/start` と同様にスケジュール登録を行う。
    """
    return await start_scan(params)


@app.post("/dynamic-scan/stop")
async def stop_scan_v2():
    """動的スキャン停止エイリアス

    旧エンドポイント `/scan/dynamic/stop` と同じ処理を実行する。
    """
    return await stop_scan()


def _aggregate_results(records: list[dict]) -> dict:
    """Aggregate scan records into a unified report.

    現在は危険プロトコルの検出数を単純にリスクスコアとする。
    危険プロトコルが存在する場合、その名称を issues に列挙する。
    """

    dangerous_list = [
        r.get("protocol", "").lower()
        for r in records
        if r.get("protocol", "").lower() in analyze.DANGEROUS_PROTOCOLS
    ]
    score = len(dangerous_list)
    dangerous = set(dangerous_list)
    categories: list[dict] = []
    if dangerous:
        categories.append({
            "name": "protocols",
            "severity": "high",
            "issues": sorted(dangerous),
        })
    return {"risk_score": score, "categories": categories}


@app.get("/scan/dynamic/results")
async def get_results():
    records = scan_scheduler.storage.get_all()
    return _aggregate_results(records)


@app.get("/dynamic-scan/results")
async def get_results_v2():
    """動的スキャン結果取得エイリアス

    `/scan/dynamic/results` と同じ集計結果を返す。
    """
    return await get_results()

# アンダースコア形式のエンドポイント (/dynamic_scan/*) へのエイリアス
@app.post("/dynamic_scan/start")
async def start_scan_v3(params: StartParams):
    """動的スキャン開始エイリアス（アンダースコア形式）"""
    return await start_scan_v2(params)


@app.post("/dynamic_scan/stop")
async def stop_scan_v3():
    """動的スキャン停止エイリアス（アンダースコア形式）"""
    return await stop_scan_v2()


@app.get("/dynamic_scan/results")
async def get_results_v3():
    """動的スキャン結果取得エイリアス（アンダースコア形式）"""
    return await get_results_v2()


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


@app.get("/dynamic-scan/history")
async def get_history_v2(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    device: Optional[str] = None,
    protocol: Optional[str] = None,
):
    """動的スキャン履歴取得エイリアス"""
    return await get_history(start, end, device, protocol)


@app.websocket("/ws/scan/dynamic")
@app.websocket("/ws/dynamic-scan")
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

@app.get("/health", tags=["meta"], include_in_schema=False)
def health():
    return {"status": "ok"}

