import asyncio

import asyncio
from datetime import datetime, timedelta

from src.dynamic_scan.storage import Storage


def test_storage_save_and_fetch(tmp_path):
    store = Storage(tmp_path / "res.db")
    q = asyncio.Queue()
    store.add_listener(q)

    asyncio.run(store.save_result({"foo": "bar", "src_ip": "1.1.1.1", "protocol": "http"}))
    first = store.get_all()[0]
    assert first["foo"] == "bar"
    assert q.get_nowait()["foo"] == "bar"

    store.remove_listener(q)
    asyncio.run(store.save_result({"baz": "qux", "src_ip": "2.2.2.2", "protocol": "ftp"}))
    assert len(store.get_all()) == 2
    assert q.empty()

    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=1)).isoformat()
    end = (now + timedelta(days=1)).isoformat()
    history = store.fetch_history({"start": start, "end": end})
    assert len(history) == 2

    ftp_only = store.fetch_history({"start": start, "end": end, "protocol": "ftp"})
    assert len(ftp_only) == 1
    assert ftp_only[0]["protocol"] == "ftp"

    device_only = store.fetch_history({"start": start, "end": end, "device": "2.2.2.2"})
    assert len(device_only) == 1
    assert device_only[0]["src_ip"] == "2.2.2.2"


def test_storage_fetch_out_of_range(tmp_path):
    store = Storage(tmp_path / "res.db")
    # 保存された結果の日付より後ろの期間を指定
    asyncio.run(store.save_result({"foo": "bar"}))
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    start = (now + timedelta(days=1)).isoformat()
    end = (now + timedelta(days=2)).isoformat()
    history = store.fetch_history({"start": start, "end": end})
    assert history == []


def test_fetch_results_range(tmp_path):
    store = Storage(tmp_path / "res.db")
    asyncio.run(store.save_result({"id": 1}))
    asyncio.run(store.save_result({"id": 2}))

    today = datetime.now().date().isoformat()
    results = store.fetch_results(today, today)
    ids = [r["id"] for r in results]
    assert ids == [1, 2]


def test_recent_limit(tmp_path):
    store = Storage(tmp_path / "res.db", max_recent=2)
    asyncio.run(store.save_result({"id": 1}))
    asyncio.run(store.save_result({"id": 2}))
    asyncio.run(store.save_result({"id": 3}))
    ids = [r["id"] for r in store.get_all()]
    assert ids == [2, 3]


def test_dns_history_save_and_fetch(tmp_path):
    store = Storage(tmp_path / "dns.db")
    store.save_dns_record("1.1.1.1", "example.com")
    store.save_dns_record("2.2.2.2", "malicious.example")
    today = datetime.now().date().isoformat()
    history = store.fetch_dns_history(today, today)
    entries = {(h["ip"], h["hostname"]) for h in history}
    assert ("1.1.1.1", "example.com") in entries
    assert ("2.2.2.2", "malicious.example") in entries
