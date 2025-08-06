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

    now = datetime.utcnow()
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
    now = datetime.utcnow()
    start = (now + timedelta(days=1)).isoformat()
    end = (now + timedelta(days=2)).isoformat()
    history = store.fetch_history({"start": start, "end": end})
    assert history == []
