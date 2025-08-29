import asyncio
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import capture, analyze, storage, scheduler

pytestmark = pytest.mark.fastapi


@pytest.mark.parametrize("base", ["/scan/dynamic", "/dynamic-scan"])
def test_dynamic_scan_endpoints(monkeypatch, tmp_path, base):
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    api.scan_scheduler = scheduler.DynamicScanScheduler()
    # start_scan 内で Storage() が呼ばれても同じインスタンスを返すようにする
    monkeypatch.setattr(storage, "Storage", lambda *args, **kwargs: store)

    def dummy_capture(interface=None, duration=None):
        return asyncio.Queue(), asyncio.create_task(asyncio.sleep(0))

    async def dummy_analyse(queue, storage_obj, approved_macs=None):
        return

    monkeypatch.setattr(capture, "capture_packets", dummy_capture)
    monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

    resp = client.post(f"{base}/start", json={"duration": 0})
    assert resp.status_code == 200
    assert resp.json() == {"status": "scheduled"}

    resp2 = client.post(f"{base}/stop")
    assert resp2.status_code == 200
    assert resp2.json() == {"status": "stopped"}

    # ストレージに異なるデータを保存し履歴 API のフィルタを検証
    asyncio.run(
        api.scan_scheduler.storage.save_result(
            {
                "key": "value",
                "src_ip": "1.1.1.1",
                "protocol": "http",
                "dangerous_protocol": False,
            }
        )
    )
    asyncio.run(
        api.scan_scheduler.storage.save_result(
            {
                "key": "other",
                "src_ip": "2.2.2.2",
                "protocol": "ftp",
                "dangerous_protocol": True,
            }
        )
    )
    asyncio.run(
        api.scan_scheduler.storage.save_result(
            {
                "key": "third",
                "src_ip": "3.3.3.3",
                "protocol": None,
                "dangerous_protocol": True,
            }
        )
    )
    asyncio.run(
        api.scan_scheduler.storage.save_result(
            {
                "src_ip": "4.4.4.4",
                "traffic_anomaly": True,
            }
        )
    )

    resp3 = client.get(f"{base}/results")
    assert resp3.status_code == 200
    body = resp3.json()
    assert body["risk_score"] == 3
    categories = {c["name"]: c for c in body["categories"]}
    assert categories["protocols"]["issues"] == ["ftp", "unknown"]
    assert categories["traffic"]["issues"] == ["4.4.4.4"]

    resp4 = client.get(
        f"{base}/history",
        params={"start": "1970-01-01", "end": "2100-01-01", "device": "2.2.2.2"},
    )
    assert resp4.status_code == 200
    hist = resp4.json()["results"]
    assert len(hist) == 1
    assert hist[0]["src_ip"] == "2.2.2.2"

    resp5 = client.get(
        f"{base}/history",
        params={"start": "1970-01-01", "end": "2100-01-01", "protocol": "ftp"},
    )
    assert resp5.status_code == 200
    hist2 = resp5.json()["results"]
    assert len(hist2) == 1
    assert hist2[0]["protocol"] == "ftp"
