import asyncio
from datetime import datetime

from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import storage


def test_history_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "hist.db")
    storage._init_db()

    async def runner():
        await storage.save_result({"id": 1, "timestamp": "2024-01-05T00:00:00"})
        await storage.save_result({"id": 2, "timestamp": "2024-01-20T00:00:00"})

    asyncio.run(runner())

    client = TestClient(api.app)
    resp = client.get(
        "/scan/dynamic/history",
        params={"from": "2024-01-10", "to": "2024-01-30"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1 and data[0]["id"] == 2


def test_history_endpoint_invalid_date():
    client = TestClient(api.app)
    resp = client.get(
        "/scan/dynamic/history",
        params={"from": "2024-13-01", "to": "2024-01-10"},
    )
    assert resp.status_code == 400
