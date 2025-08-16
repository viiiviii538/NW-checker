import asyncio
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import scheduler, storage


def test_dynamic_scan_results_alias(monkeypatch, tmp_path):
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    monkeypatch.setattr(storage, "Storage", lambda *args, **kwargs: store)

    asyncio.run(api.scan_scheduler.storage.save_result({"protocol": "ftp"}))

    resp_old = client.get("/scan/dynamic/results")
    resp_new = client.get("/dynamic-scan/results")

    assert resp_old.status_code == 200
    assert resp_new.status_code == 200
    assert resp_old.json() == resp_new.json()


def test_dynamic_scan_ws_alias(monkeypatch):
    client = TestClient(api.app)
    holder: dict[str, asyncio.Queue] = {}

    def add_listener(queue):
        holder["q"] = queue

    def remove_listener(queue):
        pass

    monkeypatch.setattr(api.scan_scheduler.storage, "add_listener", add_listener)
    monkeypatch.setattr(api.scan_scheduler.storage, "remove_listener", remove_listener)

    with client.websocket_connect("/ws/dynamic-scan") as ws:
        holder["q"].put_nowait({"foo": "bar"})
        assert ws.receive_json() == {"foo": "bar"}
