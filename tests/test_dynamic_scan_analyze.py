from collections import defaultdict
from datetime import datetime
import json
import sys
import types
import asyncio
import httpx

from src.dynamic_scan import geoip

import pytest

from src.dynamic_scan import analyze, dns_analyzer, protocol_detector


@pytest.fixture
def sample_blacklist(monkeypatch):
    """load_blacklist をモックして既知のドメイン集合を返す"""
    monkeypatch.setattr(
        dns_analyzer, "load_blacklist", lambda path="data/dns_blacklist.txt": {"malicious.example"}
    )
    dns_analyzer.DOMAIN_BLACKLIST = dns_analyzer.load_blacklist()
    yield
    dns_analyzer.DOMAIN_BLACKLIST.clear()

def test_geoip_lookup(monkeypatch):
    class FakeResp:
        status_code = 200

        def json(self):  # pragma: no cover - 単純な dict 返却
            return {"country_name": "Wonderland"}

    class DummyReader:
        def __init__(self, path):
            raise OSError("db missing")

    fake_geoip2 = types.SimpleNamespace(
        database=types.SimpleNamespace(Reader=DummyReader)
    )
    monkeypatch.setitem(sys.modules, "geoip2", fake_geoip2)
    monkeypatch.setitem(sys.modules, "geoip2.database", fake_geoip2.database)

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            return FakeResp()

    monkeypatch.setattr(analyze.httpx, "AsyncClient", lambda *a, **k: FakeClient())
    res = asyncio.run(analyze.geoip_lookup("203.0.113.1"))
    assert res == {
        "country": "Wonderland",
        "ip": "203.0.113.1",
    }


def test_get_country_local_db(monkeypatch):
    class FakeReader:
        def __init__(self, path):
            pass

        def country(self, ip):
            return types.SimpleNamespace(country=types.SimpleNamespace(iso_code="JP"))

        def close(self):
            pass

    fake_geoip2 = types.SimpleNamespace(database=types.SimpleNamespace(Reader=FakeReader))
    monkeypatch.setitem(sys.modules, "geoip2", fake_geoip2)
    monkeypatch.setitem(sys.modules, "geoip2.database", fake_geoip2.database)
    assert geoip.get_country("203.0.113.1") == "JP"


def test_get_country_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, "geoip2", None)
    monkeypatch.setitem(sys.modules, "geoip2.database", None)

    class Resp:
        status_code = 200
        text = "US"

    monkeypatch.setattr(geoip.httpx, "get", lambda url, timeout=5: Resp())
    assert geoip.get_country("203.0.113.1") == "US"


def test_get_country_api_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "geoip2", None)
    monkeypatch.setitem(sys.modules, "geoip2.database", None)

    class Resp:
        status_code = 404
        text = ""

    monkeypatch.setattr(geoip.httpx, "get", lambda url, timeout=5: Resp())
    assert geoip.get_country("203.0.113.1") is None


def test_get_country_http_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "geoip2", None)
    monkeypatch.setitem(sys.modules, "geoip2.database", None)

    def boom(url, timeout=5):  # pragma: no cover - 例外発生のテスト
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(geoip.httpx, "get", boom)
    assert geoip.get_country("203.0.113.1") is None


def test_get_country_lowercase(monkeypatch):
    monkeypatch.setitem(sys.modules, "geoip2", None)
    monkeypatch.setitem(sys.modules, "geoip2.database", None)

    class Resp:
        status_code = 200
        text = "jp"

    monkeypatch.setattr(geoip.httpx, "get", lambda url, timeout=5: Resp())
    assert geoip.get_country("203.0.113.1") == "JP"


def test_geoip_lookup_local_db(monkeypatch):
    class FakeReader:
        def __init__(self, path):
            pass

        def country(self, ip):
            return types.SimpleNamespace(
                country=types.SimpleNamespace(name="Wonderland")
            )

        def close(self):
            pass

    class FailClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            pytest.fail("API called")

    monkeypatch.setattr(analyze.httpx, "AsyncClient", lambda *a, **k: FailClient())
    fake_geoip2 = types.SimpleNamespace(
        database=types.SimpleNamespace(Reader=FakeReader)
    )
    monkeypatch.setitem(sys.modules, "geoip2", fake_geoip2)
    monkeypatch.setitem(sys.modules, "geoip2.database", fake_geoip2.database)
    res = asyncio.run(analyze.geoip_lookup("203.0.113.1"))
    assert res == {
        "country": "Wonderland",
        "ip": "203.0.113.1",
    }


def test_geoip_lookup_custom_db_path(monkeypatch):
    """渡した DB パスが Reader に渡されることを確認"""

    used_paths = []

    class FakeReader:
        def __init__(self, path):
            used_paths.append(path)

        def country(self, ip):
            return types.SimpleNamespace(
                country=types.SimpleNamespace(name="Wonderland")
            )

        def close(self):
            pass

    class FailClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            pytest.fail("API called")

    monkeypatch.setattr(analyze.httpx, "AsyncClient", lambda *a, **k: FailClient())
    fake_geoip2 = types.SimpleNamespace(
        database=types.SimpleNamespace(Reader=FakeReader)
    )
    monkeypatch.setitem(sys.modules, "geoip2", fake_geoip2)
    monkeypatch.setitem(sys.modules, "geoip2.database", fake_geoip2.database)
    res = asyncio.run(analyze.geoip_lookup("203.0.113.1", db_path="/custom/path.mmdb"))
    assert used_paths == ["/custom/path.mmdb"]
    assert res == {"country": "Wonderland", "ip": "203.0.113.1"}


def test_geoip_lookup_failure(monkeypatch):
    class FailResp:
        status_code = 500

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            return FailResp()

    monkeypatch.setattr(analyze.httpx, "AsyncClient", lambda *a, **k: FakeClient())
    assert asyncio.run(analyze.geoip_lookup("203.0.113.1")) == {}


def test_geoip_lookup_request_error(monkeypatch):
    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):  # pragma: no cover - network error path
            raise httpx.RequestError("boom")

    monkeypatch.setattr(analyze.httpx, "AsyncClient", lambda *a, **k: FakeClient())
    assert asyncio.run(analyze.geoip_lookup("203.0.113.1")) == {}


def test_reverse_dns_lookup(monkeypatch):
    analyze._dns_history.clear()
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    assert analyze.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_load_dangerous_countries(tmp_path):
    cfg = tmp_path / "dangerous.json"
    cfg.write_text('["jp", "cn"]', encoding="utf-8")
    result = analyze.load_dangerous_countries(str(cfg))
    assert result == {"JP", "CN"}


def test_load_dangerous_countries_missing(tmp_path):
    missing = tmp_path / "nope.json"
    assert analyze.load_dangerous_countries(str(missing)) == set()


def test_reverse_dns_lookup_cached(monkeypatch):
    analyze._dns_history.clear()
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    analyze.reverse_dns_lookup("1.1.1.1")
    # キャッシュが使われるため、以降のソケット呼び出しは発生しない
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: (_ for _ in ()).throw(AssertionError))
    assert analyze.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_is_dangerous_protocol():
    assert protocol_detector.is_dangerous_protocol(21, 80)
    assert not protocol_detector.is_dangerous_protocol(80, 8080)
    assert not protocol_detector.is_dangerous_protocol(None, None)


def test_analyze_packet_helper():
    pkt = type("Pkt", (), {"src_port": 445, "dst_port": 1})
    assert protocol_detector.analyze_packet(pkt) is True


def test_analyze_packet_helper_safe():
    pkt = type("Pkt", (), {"src_port": 80, "dst_port": 8080})
    assert protocol_detector.analyze_packet(pkt) is False


def test_is_unapproved_device():
    assert analyze.is_unapproved_device("00:aa", {"00:bb"})
    assert not analyze.is_unapproved_device("00:aa", {"00:aa"})


def test_detect_traffic_anomaly():
    stats = defaultdict(int)
    assert analyze.detect_traffic_anomaly(stats, "host", 500_000, threshold=1_000_000) is False
    assert analyze.detect_traffic_anomaly(stats, "host", 600_000, threshold=1_000_000) is True


def test_detect_traffic_anomaly_from_config(tmp_path, monkeypatch):
    stats = defaultdict(int)
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"traffic_threshold": 700_000}))
    monkeypatch.setattr(analyze, "CONFIG_PATH", cfg)
    assert analyze.detect_traffic_anomaly(stats, "host", 400_000) is False
    assert analyze.detect_traffic_anomaly(stats, "host", 400_000) is True


def test_load_threshold_from_file(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"traffic_threshold": 123_456}))
    assert analyze.load_threshold(cfg, default=1) == 123_456


def test_load_threshold_default_when_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.json"
    monkeypatch.setattr(analyze, "CONFIG_PATH", missing)
    assert analyze.load_threshold(default=654_321) == 654_321


def test_load_blacklist(tmp_path):
    blk = tmp_path / "dns_blacklist.txt"
    blk.write_text("# comment\nfoo.example\n\nbar.example\n")
    result = analyze.load_blacklist(blk)
    assert result == {"foo.example", "bar.example"}


def test_load_blacklist_missing_file(tmp_path):
    missing = tmp_path / "no_such_file.txt"
    assert analyze.load_blacklist(missing) == set()


def test_load_blacklist_default_file():
    assert "malicious.example" in analyze.load_blacklist()


def test_is_night_traffic():
    night_ts = datetime(2024, 1, 1, 3, 0).timestamp()
    day_ts = datetime(2024, 1, 1, 7, 0).timestamp()
    assert analyze.is_night_traffic(night_ts)
    assert not analyze.is_night_traffic(day_ts)


def test_assign_geoip_info(monkeypatch):
    async def fake_geoip(ip):
        return {"country": "Wonderland", "ip": ip}

    monkeypatch.setattr(analyze, "geoip_lookup", fake_geoip)
    monkeypatch.setattr(geoip, "get_country", lambda ip: "CN")
    pkt = type("Pkt", (), {"src_ip": "203.0.113.1", "dst_ip": "1.1.1.1"})
    res = asyncio.run(analyze.assign_geoip_info(pkt))
    assert res.geoip == {"country": "Wonderland", "ip": "203.0.113.1"}
    assert res.country_code == "CN"
    assert res.dangerous_country is True


def test_attach_geoip(monkeypatch):
    async def fake_geoip(ip):
        return {"country": "Wonderland", "ip": ip}

    monkeypatch.setattr(analyze, "geoip_lookup", fake_geoip)
    monkeypatch.setattr(geoip, "get_country", lambda ip: "CN")
    res = analyze.AnalysisResult()
    updated = asyncio.run(analyze.attach_geoip(res, "203.0.113.1"))
    assert updated.geoip == {"country": "Wonderland", "ip": "203.0.113.1"}
    assert updated.src_ip == "203.0.113.1"
    assert updated.country_code == "CN"
    assert updated.dangerous_country is True


def test_attach_geoip_no_ip():
    res = analyze.AnalysisResult()
    updated = asyncio.run(analyze.attach_geoip(res, None))
    assert updated.geoip is None
    assert updated.src_ip is None


def test_attach_geoip_no_country(monkeypatch):
    async def fake_geoip(ip):
        return {"country": "Wonderland", "ip": ip}

    monkeypatch.setattr(analyze, "geoip_lookup", fake_geoip)
    monkeypatch.setattr(geoip, "get_country", lambda ip: None)
    res = analyze.AnalysisResult()
    updated = asyncio.run(analyze.attach_geoip(res, "203.0.113.1"))
    assert updated.geoip == {"country": "Wonderland", "ip": "203.0.113.1"}
    assert updated.country_code is None
    assert updated.dangerous_country is None


def test_assign_geoip_info_ip_src(monkeypatch):
    async def fake_geoip(ip):
        return {"country": "Wonderland", "ip": ip}

    monkeypatch.setattr(analyze, "geoip_lookup", fake_geoip)
    monkeypatch.setattr(geoip, "get_country", lambda ip: "US")
    pkt = type("Pkt", (), {"ip_src": "203.0.113.1", "ip_dst": "1.1.1.1"})
    res = asyncio.run(analyze.assign_geoip_info(pkt))
    assert res.src_ip == "203.0.113.1"
    assert res.dst_ip == "1.1.1.1"
    assert res.geoip == {"country": "Wonderland", "ip": "203.0.113.1"}
    assert res.country_code == "US"
    assert res.dangerous_country is False


def test_record_dns_history(monkeypatch):
    analyze._dns_history.clear()
    dns_analyzer.DOMAIN_BLACKLIST.clear()
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    pkt = type("Pkt", (), {"src_ip": "1.1.1.1"})
    res = analyze.record_dns_history(pkt)
    assert res.reverse_dns == "host.example"
    assert res.reverse_dns_blacklisted is False
    assert analyze._dns_history["1.1.1.1"][0] == "host.example"


def test_detect_dangerous_protocols():
    pkt = type("Pkt", (), {"protocol": "TELNET", "src_port": 23})
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is True


def test_track_new_devices():
    analyze._known_devices.clear()
    pkt = type("Pkt", (), {"src_mac": "00:11"})
    assert analyze.track_new_devices(pkt).new_device is True
    assert analyze.track_new_devices(pkt).new_device is False


def test_detect_traffic_anomalies():
    stats = defaultdict(int)
    pkt = type("Pkt", (), {"src_ip": "1.1.1.1", "size": 2_000_000})
    assert analyze.detect_traffic_anomalies(pkt, stats).traffic_anomaly is True


def test_detect_out_of_hours():
    pkt = type(
        "Pkt", (), {"timestamp": datetime(2024, 1, 1, 3, 0).timestamp()}
    )
    res = analyze.detect_out_of_hours(pkt, 9, 17)
    assert res.out_of_hours is True

def test_record_dns_history_no_hostname(monkeypatch):
    analyze._dns_history.clear()
    monkeypatch.setattr(analyze, "reverse_dns_lookup", lambda ip: None)
    pkt = type("Pkt", (), {"src_ip": "1.1.1.1"})
    res = analyze.record_dns_history(pkt)
    assert res.reverse_dns is None
    assert res.reverse_dns_blacklisted is None
    assert analyze._dns_history == {}


def test_record_dns_history_uses_loaded_blacklist(monkeypatch, sample_blacklist):
    analyze._dns_history.clear()
    monkeypatch.setattr(
        analyze.socket, "gethostbyaddr", lambda ip: ("malicious.example", [], [])
    )
    pkt = type("Pkt", (), {"src_ip": "4.4.4.4"})
    res = analyze.record_dns_history(pkt)
    assert res.reverse_dns == "malicious.example"
    assert res.reverse_dns_blacklisted is True


def test_record_dns_history_blacklisted(monkeypatch):
    analyze._dns_history.clear()
    dns_analyzer.DOMAIN_BLACKLIST.clear()
    dns_analyzer.DOMAIN_BLACKLIST.add("bad.example")
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: ("bad.example", [], []))
    pkt = type("Pkt", (), {"src_ip": "2.2.2.2"})
    res = analyze.record_dns_history(pkt)
    assert res.reverse_dns == "bad.example"
    assert res.reverse_dns_blacklisted is True


def test_record_dns_history_blacklisted_cached(monkeypatch):
    analyze._dns_history.clear()
    dns_analyzer.DOMAIN_BLACKLIST.clear()
    dns_analyzer.DOMAIN_BLACKLIST.add("bad.example")

    # 1回目の呼び出しで DNS を解決して履歴に保存
    monkeypatch.setattr(
        analyze.socket, "gethostbyaddr", lambda ip: ("bad.example", [], [])
    )
    pkt = type("Pkt", (), {"src_ip": "3.3.3.3"})
    analyze.record_dns_history(pkt)

    # キャッシュされた結果を利用するため、ソケットは呼び出されない
    monkeypatch.setattr(
        analyze.socket,
        "gethostbyaddr",
        lambda ip: (_ for _ in ()).throw(AssertionError),
    )
    res_cached = analyze.record_dns_history(pkt)
    assert res_cached.reverse_dns == "bad.example"
    assert res_cached.reverse_dns_blacklisted is True


def test_detect_dangerous_protocols_safe_protocol():
    pkt = type("Pkt", (), {"protocol": "HTTP", "src_port": 80})
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is False


def test_detect_dangerous_protocols_none_protocol():
    pkt = type("Pkt", (), {})
    res = analyze.detect_dangerous_protocols(pkt)
    assert res.dangerous_protocol is False


def test_detect_traffic_anomalies_normal():
    stats = defaultdict(int)
    pkt = type("Pkt", (), {"src_ip": "1.1.1.1", "size": 500_000})
    assert analyze.detect_traffic_anomalies(pkt, stats).traffic_anomaly is False


def test_detect_out_of_hours_within_schedule():
    pkt = type(
        "Pkt", (), {"timestamp": datetime(2024, 1, 1, 10, 0).timestamp()}
    )
    res = analyze.detect_out_of_hours(pkt, 9, 17)
    assert res.out_of_hours is False


def test_detect_out_of_hours_at_start_hour():
    pkt = type(
        "Pkt", (), {"timestamp": datetime(2024, 1, 1, 9, 0).timestamp()}
    )
    res = analyze.detect_out_of_hours(pkt, 9, 17)
    assert res.out_of_hours is False


def test_detect_out_of_hours_at_end_hour():
    pkt = type(
        "Pkt", (), {"timestamp": datetime(2024, 1, 1, 17, 0).timestamp()}
    )
    res = analyze.detect_out_of_hours(pkt, 9, 17)
    assert res.out_of_hours is True


def test_analysis_result_merge_and_to_dict():
    a = analyze.AnalysisResult(src_ip="1.1.1.1", dangerous_protocol=True)
    b = analyze.AnalysisResult(dst_ip="2.2.2.2", new_device=False)
    merged = analyze.AnalysisResult.merge(a, b)
    assert merged.src_ip == "1.1.1.1"
    assert merged.dst_ip == "2.2.2.2"
    assert merged.dangerous_protocol is True
    assert merged.new_device is False
    assert "protocol" not in merged.to_dict()
