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
