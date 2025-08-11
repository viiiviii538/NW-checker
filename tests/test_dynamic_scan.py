import asyncio
from datetime import datetime
import contextlib
from types import SimpleNamespace
from collections import defaultdict

import pytest

from src.dynamic_scan import analyze, capture, storage


def test_geoip_lookup(monkeypatch):
    class FakeResp:
        ok = True

        def json(self):
            return {"country_name": "Wonderland"}

    monkeypatch.setattr(analyze.requests, "get", lambda url, timeout=5: FakeResp())
    assert analyze.geoip_lookup("203.0.113.1") == {"country": "Wonderland", "ip": "203.0.113.1"}


def test_reverse_dns_lookup(monkeypatch):
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    assert analyze.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_is_dangerous_protocol():
    assert analyze.is_dangerous_protocol("telnet")
    assert not analyze.is_dangerous_protocol("http")
    assert not analyze.is_dangerous_protocol(None)


def test_detect_dangerous_protocols_none():
    pkt = SimpleNamespace(protocol=None)
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is False


def test_is_unapproved_device():
    assert analyze.is_unapproved_device("00:aa", {"00:bb"})
    assert not analyze.is_unapproved_device("00:aa", {"00:aa"})


def test_detect_traffic_anomaly():
    stats = defaultdict(int)
    assert analyze.detect_traffic_anomaly(stats, "host", 500_000, threshold=1_000_000) is False
    assert analyze.detect_traffic_anomaly(stats, "host", 600_000, threshold=1_000_000) is True


def test_is_night_traffic():
    night_ts = datetime(2024, 1, 1, 3, 0).timestamp()
    day_ts = datetime(2024, 1, 1, 7, 0).timestamp()
    assert analyze.is_night_traffic(night_ts)
    assert not analyze.is_night_traffic(day_ts)


def test_capture_packets_enqueue(monkeypatch):
    class FakeSniffer:
        def __init__(self, iface=None, prn=None):
            self.prn = prn

        def start(self):
            self.prn("pkt")

        def stop(self):
            pass

    monkeypatch.setattr(capture, "AsyncSniffer", FakeSniffer)
    queue: asyncio.Queue = asyncio.Queue()
    asyncio.run(capture.capture_packets(queue, duration=0))
    assert queue.get_nowait() == "pkt"


def test_storage_save_and_get(tmp_path):
    async def runner():
        store = storage.Storage(tmp_path / "r.db")
        await store.save_result({"a": 1})
        await store.save_result({"b": 2})
        assert len(store.get_all()) == 2

    asyncio.run(runner())


def test_analyse_packets_pipeline(tmp_path, monkeypatch):
    async def runner():
        store = storage.Storage(tmp_path / "results.json")
        monkeypatch.setattr(analyze, "geoip_lookup", lambda ip: {"country": "Testland", "ip": ip})
        monkeypatch.setattr(analyze, "reverse_dns_lookup", lambda ip: "example.com")
        queue: asyncio.Queue = asyncio.Queue()
        task = asyncio.create_task(
            analyze.analyse_packets(
                queue,
                store,
                approved_macs={"00:11:22:33:44:55"},
                schedule=(9, 17),
            )
        )
        pkt = SimpleNamespace(
            src_ip="8.8.8.8",
            dst_ip="1.1.1.1",
            src_mac="00:11:22:33:44:66",
            protocol="TELNET",
            size=2_000_000,
            timestamp=datetime(2024, 1, 1, 2, 0, 0).timestamp(),
        )
        await queue.put(pkt)
        await queue.join()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        data = store.get_all()
        assert data[0]["dangerous_protocol"] is True
        assert data[0]["unapproved_device"] is True
        assert data[0]["traffic_anomaly"] is True
        assert data[0]["out_of_hours"] is True
        assert data[0]["new_device"] is True
        assert data[0]["geoip"]["country"] == "Testland"
        assert data[0]["reverse_dns"] == "example.com"

    asyncio.run(runner())
