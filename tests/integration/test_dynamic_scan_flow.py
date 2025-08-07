import asyncio
import tracemalloc
from contextlib import suppress
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from src import api
from src.dynamic_scan import analyze, capture, storage


class DummyPacket:
    src_ip = "1.1.1.1"
    dst_ip = "2.2.2.2"
    protocol = "TELNET"
    src_mac = "00:11:22:33:44:55"
    size = 100
    timestamp = 0.0


@pytest.mark.benchmark
def test_dynamic_scan_full_flow(monkeypatch, tmp_path, benchmark):
    async def fake_capture(queue: asyncio.Queue, interface=None, duration=None) -> None:
        for _ in range(5):
            queue.put_nowait(DummyPacket())
        await asyncio.sleep(0)

    monkeypatch.setattr(capture, "capture_packets", fake_capture)
    async def run_flow(db_name: str) -> tuple[int, storage.Storage]:
        local_store = storage.Storage(tmp_path / db_name)
        queue: asyncio.Queue = asyncio.Queue()
        capture_task = asyncio.create_task(capture.capture_packets(queue))
        analyse_task = asyncio.create_task(analyze.analyse_packets(queue, local_store))
        await capture_task
        await asyncio.wait_for(queue.join(), timeout=5)
        analyse_task.cancel()
        with suppress(asyncio.CancelledError):
            await analyse_task
        return queue.qsize(), local_store

    tracemalloc.start()
    benchmark(lambda: asyncio.run(run_flow("bench.db")))
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    qsize, store = asyncio.run(run_flow("res.db"))
    assert qsize == 0
    assert current < 1_000_000  # 約1MB未満に収まることを期待

    api.scan_scheduler.storage = store
    prev_token = api.API_TOKEN
    api.API_TOKEN = "testtoken"
    client = TestClient(api.app)
    resp = client.get("/scan/dynamic/results", headers={"Authorization": "Bearer testtoken"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_score"] == 5
    assert body["categories"][0]["issues"] == ["telnet"]
    api.API_TOKEN = prev_token
