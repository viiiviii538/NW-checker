import asyncio
from fastapi.testclient import TestClient

from src import api
from src.dynamic_scan import scheduler, storage


def test_dns_history_endpoint(tmp_path):
    client = TestClient(api.app)
    store = storage.Storage(tmp_path / "res.db")
    sched = scheduler.DynamicScanScheduler()
    sched.storage = store
    api.scan_scheduler = sched

    asyncio.run(store.save_dns_history("1.1.1.1", "host.example", False))
    asyncio.run(store.save_dns_history("2.2.2.2", "bad.example", True))

    resp = client.get(
        "/dynamic-scan/dns-history",
        params={"start": "1970-01-01", "end": "2100-01-01"},
    )
    assert resp.status_code == 200
    data = resp.json()["history"]
    assert len(data) == 2
    assert data[0]["hostname"] == "host.example"
    assert data[1]["blacklisted"] is True
