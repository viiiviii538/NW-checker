import asyncio
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import scheduler, storage, capture, analyze


def test_dynamic_scan_start_stop_alias(monkeypatch, tmp_path):
    # 認証トークンが設定されていると 401 になるため無効化
    monkeypatch.setattr(api, "API_TOKEN", None, raising=False)
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    monkeypatch.setattr(storage, "Storage", lambda *args, **kwargs: store)

    def dummy_capture(interface=None, duration=None):
        return asyncio.Queue(), asyncio.create_task(asyncio.sleep(0))

    async def dummy_analyse(queue, storage_obj, approved_macs=None):
        return

    monkeypatch.setattr(capture, "capture_packets", dummy_capture)
    monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

    # start aliases behave identically
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    resp_old = client.post("/scan/dynamic/start", json={"duration": 0})
    asyncio.run(api.scan_scheduler.stop())

    api.scan_scheduler = scheduler.DynamicScanScheduler()
    resp_new = client.post("/dynamic-scan/start", json={"duration": 0})
    assert resp_old.status_code == resp_new.status_code == 200
    assert resp_old.json() == resp_new.json() == {"status": "scheduled"}
    asyncio.run(api.scan_scheduler.stop())

    # stop aliases behave identically
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    client.post("/scan/dynamic/start", json={"duration": 0})
    resp_old_stop = client.post("/scan/dynamic/stop")

    api.scan_scheduler = scheduler.DynamicScanScheduler()
    client.post("/dynamic-scan/start", json={"duration": 0})
    resp_new_stop = client.post("/dynamic-scan/stop")
    assert resp_old_stop.status_code == resp_new_stop.status_code == 200
    assert resp_old_stop.json() == resp_new_stop.json() == {"status": "stopped"}


def test_dynamic_scan_results_alias(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "API_TOKEN", None, raising=False)
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
    monkeypatch.setattr(api, "API_TOKEN", None, raising=False)
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
