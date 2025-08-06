import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import capture, analyze, storage


def test_dynamic_scan_start_stop(monkeypatch, tmp_path):
    client = TestClient(api.app)

    class TmpStorage(storage.Storage):
        def __init__(self, file_path: str | Path | None = None):
            super().__init__(tmp_path / "res.json")

    monkeypatch.setattr(storage, "Storage", TmpStorage)
    api.storage_obj = storage.Storage()

    async def dummy_capture(queue, interface=None, duration=None):
        return

    async def dummy_analyse(queue, storage_obj, approved_macs=None):
        return

    monkeypatch.setattr(capture, "capture_packets", dummy_capture)
    monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

    resp = client.post("/scan/dynamic/start", json={"duration": 0})
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"

    resp2 = client.post("/scan/dynamic/stop")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "stopped"

    asyncio.run(api.storage_obj.save({"key": "value"}))
    resp3 = client.get("/scan/dynamic/results")
    assert resp3.json()["results"] == [{"key": "value"}]


def test_dynamic_history_endpoint(tmp_path, monkeypatch):
    client = TestClient(api.app)
    db = tmp_path / "hist.db"
    monkeypatch.setattr(storage, "DB_FILE", db)
    storage._init_db()
    storage.save_result({"timestamp": "2024-01-01T00:00:00", "v": 1})
    storage.save_result({"timestamp": "2024-01-02T00:00:00", "v": 2})
    resp = client.get(
        "/scan/dynamic/history",
        params={"from": "2024-01-01", "to": "2024-01-01"},
    )
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1


def test_dynamic_scan_websocket_broadcast(tmp_path):
    client = TestClient(api.app)
    api.storage_obj = storage.Storage(tmp_path / "res.json")

    with client.websocket_connect("/ws/scan/dynamic") as websocket:
        # 保存すると WebSocket へプッシュされることを確認
        asyncio.run(api.storage_obj.save({"foo": "bar"}))
        message = websocket.receive_json()
        assert message == {"foo": "bar"}
