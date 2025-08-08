from collections import defaultdict
from datetime import datetime

import pytest

from src.dynamic_scan import analyze


def test_geoip_lookup(monkeypatch):
    class FakeResp:
        ok = True

        def json(self):  # pragma: no cover - 単純な dict 返却
            return {"country_name": "Wonderland"}

    monkeypatch.setattr(analyze.requests, "get", lambda url, timeout=5: FakeResp())
    assert analyze.geoip_lookup("203.0.113.1") == {
        "country": "Wonderland",
        "ip": "203.0.113.1",
    }


def test_reverse_dns_lookup(monkeypatch):
    monkeypatch.setattr(analyze.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    assert analyze.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_is_dangerous_protocol():
    assert analyze.is_dangerous_protocol("telnet")
    assert not analyze.is_dangerous_protocol("http")


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


def test_assign_geoip_info(monkeypatch):
    class FakeResp:
        ok = True

        def json(self):  # pragma: no cover - 単純な dict 返却
            return {"country_name": "Wonderland"}

    monkeypatch.setattr(analyze.requests, "get", lambda url, timeout=5: FakeResp())
    pkt = type("Pkt", (), {"src_ip": "203.0.113.1", "dst_ip": "1.1.1.1"})
    res = analyze.assign_geoip_info(pkt)
    assert res.geoip == {"country": "Wonderland", "ip": "203.0.113.1"}


def test_attach_geoip(monkeypatch):
    class FakeResp:
        ok = True

        def json(self):  # pragma: no cover - 単純な dict 返却
            return {"country_name": "Wonderland"}

    monkeypatch.setattr(analyze.requests, "get", lambda url, timeout=5: FakeResp())
    res = analyze.AnalysisResult()
    updated = analyze.attach_geoip(res, "203.0.113.1")
    assert updated.geoip == {"country": "Wonderland", "ip": "203.0.113.1"}
    assert updated.src_ip == "203.0.113.1"


def test_record_dns_history(monkeypatch):
    analyze._dns_history.clear()
    monkeypatch.setattr(analyze, "reverse_dns_lookup", lambda ip: "host.example")
    pkt = type("Pkt", (), {"src_ip": "1.1.1.1"})
    res = analyze.record_dns_history(pkt)
    assert res.reverse_dns == "host.example"
    assert analyze._dns_history["1.1.1.1"] == "host.example"


def test_detect_dangerous_protocols():
    pkt = type("Pkt", (), {"protocol": "TELNET"})
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
    res = analyze.detect_out_of_hours(pkt, (9, 17))
    assert res.out_of_hours is True

def test_record_dns_history_no_hostname(monkeypatch):
    analyze._dns_history.clear()
    monkeypatch.setattr(analyze, "reverse_dns_lookup", lambda ip: None)
    pkt = type("Pkt", (), {"src_ip": "1.1.1.1"})
    res = analyze.record_dns_history(pkt)
    assert res.reverse_dns is None
    assert analyze._dns_history == {}


def test_detect_dangerous_protocols_safe_protocol():
    pkt = type("Pkt", (), {"protocol": "HTTP"})
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
    res = analyze.detect_out_of_hours(pkt, (9, 17))
    assert res.out_of_hours is False


def test_analysis_result_merge_and_to_dict():
    a = analyze.AnalysisResult(src_ip="1.1.1.1", dangerous_protocol=True)
    b = analyze.AnalysisResult(dst_ip="2.2.2.2", new_device=False)
    merged = analyze.AnalysisResult.merge(a, b)
    assert merged.src_ip == "1.1.1.1"
    assert merged.dst_ip == "2.2.2.2"
    assert merged.dangerous_protocol is True
    assert merged.new_device is False
    assert "protocol" not in merged.to_dict()
