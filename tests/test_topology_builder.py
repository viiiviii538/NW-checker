"""Tests for building topology paths."""

import json

from src.topology_builder import (
    build_paths,
    build_topology,
    build_topology_for_subnet,
    traceroute,
)


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
    monkeypatch.setattr("src.topology_builder.nextCmd", object())

    result = build_paths(["192.168.0.20"], use_snmp=True)
    assert result == {
        "paths": [{"ip": "192.168.0.20", "path": ["LAN", "SwitchA", "Host"]}]
    }


def test_build_paths_snmp_unavailable(monkeypatch):
    """When pysnmp is missing, SNMP augmentation is skipped."""

    def fake_traceroute(ip):  # pragma: no cover - simple stub
        return ["192.168.0.1", ip]

    called = {"flag": False}

    def fake_augment(hops, path, community="public"):
        called["flag"] = True

    monkeypatch.setattr("src.topology_builder.traceroute", fake_traceroute)
    monkeypatch.setattr("src.topology_builder._augment_with_snmp", fake_augment)
    monkeypatch.setattr("src.topology_builder.nextCmd", None)

    result = build_paths(["192.168.0.30"], use_snmp=True)
    assert result == {
        "paths": [{"ip": "192.168.0.30", "path": ["LAN", "Router", "Host"]}]
    }
    assert not called["flag"]


def test_build_topology_wrapper(monkeypatch):
    """``build_topology`` wraps ``build_paths`` and outputs JSON."""

    def fake_build_paths(hosts, use_snmp=False, community="public"):
        assert hosts == ["192.168.0.30"]
        assert use_snmp
        assert community == "private"
        return {
            "paths": [
                {"ip": "192.168.0.30", "path": ["LAN", "Router", "Host"]}
            ]
        }

    monkeypatch.setattr("src.topology_builder.build_paths", fake_build_paths)

    result = build_topology(["192.168.0.30"], use_snmp=True, community="private")
    assert json.loads(result) == {"paths": [["LAN", "Router", "Host"]]}


def test_build_topology_for_subnet(monkeypatch):
    """Subnet wrapper discovers hosts then forwards to ``build_topology``."""

    def fake_discover_hosts(subnet):
        assert subnet == "192.168.0.0/24"
        return [{"ip": "192.168.0.40"}, {"ip": "192.168.0.41"}]

    captured = {}

    def fake_build_topology(hosts, use_snmp=False, community="public"):
        captured["hosts"] = hosts
        captured["use_snmp"] = use_snmp
        captured["community"] = community
        return "JSON"

    import sys, types

    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace())
    monkeypatch.setattr(
        "src.discover_hosts.discover_hosts", fake_discover_hosts
    )
    monkeypatch.setattr("src.topology_builder.build_topology", fake_build_topology)

    result = build_topology_for_subnet(
        "192.168.0.0/24", use_snmp=True, community="private"
    )
    assert result == "JSON"
    assert captured == {
        "hosts": ["192.168.0.40", "192.168.0.41"],
        "use_snmp": True,
        "community": "private",
    }

