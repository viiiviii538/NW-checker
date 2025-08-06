import asyncio

from src.dynamic_scan.storage import Storage


def test_storage_save_and_listeners(tmp_path):
    store = Storage(tmp_path / "res.json")
    q = asyncio.Queue()
    store.add_listener(q)

    asyncio.run(store.save({"foo": "bar"}))
    assert store.get_all() == [{"foo": "bar"}]
    assert q.get_nowait() == {"foo": "bar"}

    store.remove_listener(q)
    asyncio.run(store.save({"baz": "qux"}))
    assert store.get_all() == [{"foo": "bar"}, {"baz": "qux"}]
    assert q.empty()
