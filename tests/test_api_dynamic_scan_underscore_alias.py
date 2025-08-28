import asyncio
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import scheduler, storage, capture, analyze

pytestmark = pytest.mark.fastapi


def test_dynamic_scan_start_stop_underscore_alias(monkeypatch, tmp_path):
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
    resp_hyphen = client.post("/dynamic-scan/start", json={"duration": 0})
    asyncio.run(api.scan_scheduler.stop())

    api.scan_scheduler = scheduler.DynamicScanScheduler()
    resp_underscore = client.post("/dynamic_scan/start", json={"duration": 0})
    assert resp_hyphen.status_code == resp_underscore.status_code == 200
    assert resp_hyphen.json() == resp_underscore.json() == {"status": "scheduled"}
    asyncio.run(api.scan_scheduler.stop())

    # stop aliases behave identically
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    client.post("/dynamic-scan/start", json={"duration": 0})
    resp_hyphen_stop = client.post("/dynamic-scan/stop")

    api.scan_scheduler = scheduler.DynamicScanScheduler()
    client.post("/dynamic_scan/start", json={"duration": 0})
    resp_underscore_stop = client.post("/dynamic_scan/stop")
    assert resp_hyphen_stop.status_code == resp_underscore_stop.status_code == 200
    assert resp_hyphen_stop.json() == resp_underscore_stop.json() == {"status": "stopped"}


def test_dynamic_scan_results_underscore_alias(monkeypatch, tmp_path):
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    monkeypatch.setattr(storage, "Storage", lambda *args, **kwargs: store)

    asyncio.run(api.scan_scheduler.storage.save_result({"protocol": "ftp"}))

    resp_hyphen = client.get("/dynamic-scan/results")
    resp_underscore = client.get("/dynamic_scan/results")

    assert resp_hyphen.status_code == 200
    assert resp_underscore.status_code == 200
    assert resp_hyphen.json() == resp_underscore.json()
