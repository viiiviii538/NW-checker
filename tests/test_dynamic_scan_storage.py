import asyncio

from datetime import datetime, timedelta

from src.dynamic_scan.storage import Storage


def test_storage_save_and_fetch(tmp_path):
    store = Storage(tmp_path / "res.db")
    q = asyncio.Queue()
    store.add_listener(q)

    asyncio.run(store.save_result({"foo": "bar"}))
    first = store.get_all()[0]
    assert first["foo"] == "bar"
    assert q.get_nowait()["foo"] == "bar"

    store.remove_listener(q)
    asyncio.run(store.save_result({"baz": "qux"}))
    assert len(store.get_all()) == 2
    assert q.empty()

    today = datetime.utcnow().date()
    start = (today - timedelta(days=1)).isoformat()
    end = (today + timedelta(days=1)).isoformat()
    history = store.fetch_results(start, end)
    assert len(history) == 2


def test_storage_fetch_out_of_range(tmp_path):
    store = Storage(tmp_path / "res.db")
    # 保存された結果の日付より後ろの期間を指定
    asyncio.run(store.save_result({"foo": "bar"}))
    today = datetime.utcnow().date()
    start = (today + timedelta(days=1)).isoformat()
    end = (today + timedelta(days=2)).isoformat()
    history = store.fetch_results(start, end)
    assert history == []
