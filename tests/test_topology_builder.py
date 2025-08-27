"""Tests for building topology paths."""

from src.topology_builder import build_paths, traceroute


def test_traceroute_parses_hops(monkeypatch):
    """Raw traceroute output is parsed into hop IP addresses."""

    def fake_check_output(cmd, text=True):  # pragma: no cover - called via traceroute
        return (
            "traceroute to 8.8.8.8 (8.8.8.8), 30 hops max\n"
            "1  192.168.0.1  1.0 ms\n"
            "2  8.8.8.8  2.0 ms\n"
        )

    monkeypatch.setattr("src.topology_builder.subprocess.check_output", fake_check_output)

    assert traceroute("8.8.8.8") == ["192.168.0.1", "8.8.8.8"]


def test_build_paths_basic(monkeypatch):
    """Hop IPs are converted to generic labels when SNMP is disabled."""

    def fake_traceroute(ip):  # pragma: no cover - simple stub
        return ["192.168.0.1", ip]

    called = {"flag": False}

    def fake_augment(hops, path, community="public"):
        called["flag"] = True

    monkeypatch.setattr("src.topology_builder.traceroute", fake_traceroute)
    monkeypatch.setattr("src.topology_builder._augment_with_snmp", fake_augment)

    result = build_paths(["192.168.0.10"])
    assert result == {
        "paths": [{"ip": "192.168.0.10", "path": ["LAN", "Router", "Host"]}]
    }
    assert not called["flag"]


def test_build_paths_with_snmp(monkeypatch):
    """SNMP neighbor names replace router labels when requested."""

    def fake_traceroute(ip):  # pragma: no cover - simple stub
        return ["192.168.0.1", ip]

    def fake_augment(hops, path, community="public"):
        path[1] = "SwitchA"

    monkeypatch.setattr("src.topology_builder.traceroute", fake_traceroute)
    monkeypatch.setattr("src.topology_builder._augment_with_snmp", fake_augment)

    result = build_paths(["192.168.0.20"], use_snmp=True)
    assert result == {
        "paths": [{"ip": "192.168.0.20", "path": ["LAN", "SwitchA", "Host"]}]
    }

