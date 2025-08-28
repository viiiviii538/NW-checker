"""Unit tests for topology builder utilities."""

from src import topology_builder as tb


def test_traceroute_parsing(monkeypatch):
    """Traceroute output is parsed into hop IPs."""

    def fake_check_output(cmd, text=True):  # pragma: no cover - simple mock
        return (
            "traceroute to 1.1.1.1 (1.1.1.1), 30 hops max\n"
            "1  192.168.0.1  1.0 ms\n"
            "2  1.1.1.1  2.0 ms\n"
        )

    monkeypatch.setattr(tb.subprocess, "check_output", fake_check_output)
    assert tb.traceroute("1.1.1.1") == ["192.168.0.1", "1.1.1.1"]


def test_build_paths_skips_snmp_when_unavailable(monkeypatch):
    """_augment_with_snmp is skipped if pysnmp is missing."""

    def fake_traceroute(ip):  # pragma: no cover - simple stub
        return ["192.168.0.1", ip]

    called = {"flag": False}

    def fake_augment(hops, path, community="public"):
        called["flag"] = True

    monkeypatch.setattr(tb, "traceroute", fake_traceroute)
    monkeypatch.setattr(tb, "_augment_with_snmp", fake_augment)
    monkeypatch.setattr(tb, "nextCmd", None)

    result = tb.build_paths(["192.168.0.5"], use_snmp=True)
    assert result == {
        "paths": [{"ip": "192.168.0.5", "path": ["LAN", "Router", "Host"]}]
    }
    assert not called["flag"]


def test_build_paths_calls_snmp_when_available(monkeypatch):
    """_augment_with_snmp is invoked when pysnmp is present."""

    def fake_traceroute(ip):  # pragma: no cover - simple stub
        return ["192.168.0.1", ip]

    def fake_augment(hops, path, community="public"):
        path[1] = "SwitchA"

    monkeypatch.setattr(tb, "traceroute", fake_traceroute)
    monkeypatch.setattr(tb, "_augment_with_snmp", fake_augment)
    monkeypatch.setattr(tb, "nextCmd", object())

    result = tb.build_paths(["192.168.0.6"], use_snmp=True)
    assert result == {
        "paths": [{"ip": "192.168.0.6", "path": ["LAN", "SwitchA", "Host"]}]
    }

