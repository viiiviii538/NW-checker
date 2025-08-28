import asyncio
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import capture, analyze, storage, scheduler

pytestmark = pytest.mark.fastapi


def test_dynamic_scan_start_stop(monkeypatch, tmp_path):
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    # start_scan 内で新たな Storage() が生成されても同じものを使用させる
    monkeypatch.setattr(storage, "Storage", lambda *args, **kwargs: store)

    def dummy_capture(interface=None, duration=None):
        return asyncio.Queue(), asyncio.create_task(asyncio.sleep(0))

    async def dummy_analyse(queue, storage_obj, approved_macs=None):
        return

    monkeypatch.setattr(capture, "capture_packets", dummy_capture)
    monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

    resp = client.post("/scan/dynamic/start", json={"duration": 0})
    assert resp.status_code == 200
    assert resp.json()["status"] == "scheduled"

    resp2 = client.post("/scan/dynamic/stop")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "stopped"

    asyncio.run(
        api.scan_scheduler.storage.save_result(
            {"protocol": "ftp", "src_ip": "1.1.1.1", "dangerous_protocol": True}
        )
    )
    resp3 = client.get("/scan/dynamic/results")
    body = resp3.json()
    assert body["risk_score"] == 1
    assert body["categories"][0]["issues"] == ["ftp"]


def test_dynamic_scan_websocket_broadcast(tmp_path):
    client = TestClient(api.app)
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    api.scan_scheduler.storage = storage.Storage(tmp_path / "res.db")

    with client.websocket_connect("/ws/scan/dynamic") as websocket:
        # 保存すると WebSocket へプッシュされることを確認
        asyncio.run(api.scan_scheduler.storage.save_result({"foo": "bar"}))
        message = websocket.receive_json()
        assert message["foo"] == "bar"
