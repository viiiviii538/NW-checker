import asyncio
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import capture, analyze, storage


def test_dynamic_scan_endpoints(monkeypatch, tmp_path):
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    api.storage_obj = store
    # start_scan 内で Storage() が呼ばれても同じインスタンスを返すようにする
    monkeypatch.setattr(storage, "Storage", lambda *args, **kwargs: store)

    async def dummy_capture(queue, interface=None, duration=None):
        return

    async def dummy_analyse(queue, storage_obj, approved_macs=None):
        return

    monkeypatch.setattr(capture, "capture_packets", dummy_capture)
    monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

    resp = client.post("/scan/dynamic/start", json={"duration": 0})
    assert resp.status_code == 200
    assert resp.json() == {"status": "started"}

    resp2 = client.post("/scan/dynamic/stop")
    assert resp2.status_code == 200
    assert resp2.json() == {"status": "stopped"}

    asyncio.run(api.storage_obj.save_result({"key": "value"}))
    resp3 = client.get("/scan/dynamic/results")
    assert resp3.status_code == 200
    assert resp3.json()["results"][0]["key"] == "value"

    resp4 = client.get("/scan/dynamic/history", params={"from": "1970-01-01", "to": "2100-01-01"})
    assert resp4.status_code == 200
    assert resp4.json()["results"][0]["key"] == "value"
