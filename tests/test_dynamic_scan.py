import asyncio
from datetime import datetime, timedelta
import contextlib
from types import SimpleNamespace
from collections import defaultdict


from src.dynamic_scan import (
    analyze,
    capture,
    storage,
    geoip,
    protocol_detector,
    device_tracker,
    traffic_anomaly,
)


def test_geoip_lookup(monkeypatch):
    class FakeResp:
        status_code = 200

        def json(self):
            return {"country_name": "Wonderland"}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            return FakeResp()

    monkeypatch.setattr(analyze.httpx, "AsyncClient", lambda *a, **k: FakeClient())
    res = asyncio.run(analyze.geoip_lookup("203.0.113.1"))
    assert res == {"country": "Wonderland", "ip": "203.0.113.1"}


def test_reverse_dns_lookup(monkeypatch):
    analyze.dns_analyzer._dns_cache.clear()
    monkeypatch.setattr(
        analyze.socket, "gethostbyaddr", lambda ip: ("host.example", [], [])
    )
    assert analyze.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_is_dangerous_protocol():
    assert protocol_detector.is_dangerous_protocol(23, 1000)
    assert protocol_detector.is_dangerous_protocol(5900, None)
    assert not protocol_detector.is_dangerous_protocol(80, 8080)
    assert not protocol_detector.is_dangerous_protocol(None, None)


def test_is_dangerous_protocol_winrm():
    assert protocol_detector.is_dangerous_protocol(5985, 80)


def test_detect_dangerous_protocols_safe_ports():
    pkt = SimpleNamespace(protocol="HTTP", src_port=80, dst_port=8080)
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is False


def test_detect_dangerous_protocols_dst_port():
    pkt = SimpleNamespace(protocol="RDP", src_port=80, dst_port=3389)
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is True


def test_detect_dangerous_protocols_src_port():
    pkt = SimpleNamespace(protocol="SMB", src_port=445, dst_port=1234)
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is True


def test_is_unapproved_device():
    assert analyze.is_unapproved_device("00:aa", {"00:bb"})
    assert not analyze.is_unapproved_device("00:aa", {"00:aa"})


def test_detect_traffic_anomaly(monkeypatch):
    stats = defaultdict(int)
    traffic_anomaly._stats.clear()
    monkeypatch.setattr(traffic_anomaly, "SPIKE_THRESHOLD", 100_000)
    analyze.detect_traffic_anomaly(stats, "host", 50_000)
    assert analyze.detect_traffic_anomaly(stats, "host", 200_000) is True


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

    monkeypatch.setattr(capture.parser, "parse_packet", lambda pkt: pkt)
    monkeypatch.setattr(capture, "AsyncSniffer", FakeSniffer)

    async def runner():
        queue, task = capture.capture_packets(duration=0)
        await task
        return queue

    queue = asyncio.run(runner())
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

        async def fake_geoip(ip):
            return {"country": "Testland", "ip": ip}

        monkeypatch.setattr(analyze, "geoip_lookup", fake_geoip)
        monkeypatch.setattr(geoip, "get_country", lambda ip: "CN")
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
            src_port=23,
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
        assert data[0]["country_code"] == "CN"
        assert data[0]["dangerous_country"] is True
        start = (datetime.now() - timedelta(days=1)).date().isoformat()
        end = (datetime.now() + timedelta(days=1)).date().isoformat()
        dns_hist = store.fetch_dns_history(start, end)
        assert dns_hist[0]["ip"] == "8.8.8.8"
        assert dns_hist[0]["hostname"] == "example.com"
        assert dns_hist[0]["blacklisted"] is False

    asyncio.run(runner())


def test_analyse_packets_pipeline_in_hours(tmp_path, monkeypatch):
    async def runner():
        device_tracker._known_devices.clear()
        store = storage.Storage(tmp_path / "results.json")

        async def fake_geoip(ip):
            return {"country": "Testland", "ip": ip}

        monkeypatch.setattr(analyze, "geoip_lookup", fake_geoip)
        monkeypatch.setattr(geoip, "get_country", lambda ip: "US")
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
            src_mac="00:11:22:33:44:77",
            protocol="TELNET",
            src_port=23,
            size=2_000_000,
            timestamp=datetime(2024, 1, 1, 10, 0, 0).timestamp(),
        )
        await queue.put(pkt)
        await queue.join()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        data = store.get_all()
        assert data[0]["out_of_hours"] is False
        assert data[0]["country_code"] == "US"
        assert data[0]["dangerous_country"] is False

    asyncio.run(runner())
