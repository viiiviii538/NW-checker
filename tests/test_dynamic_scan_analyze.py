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
