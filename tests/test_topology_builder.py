"""Tests for building topology paths."""

import json

from src.topology_builder import build_paths, build_topology, build_topology_for_subnet


def _traceroute_output(ip: str) -> str:
    return (
        f"traceroute to {ip} ({ip}), 30 hops max\n"
        "1  192.168.0.1  1.0 ms\n"
        f"2  {ip}  2.0 ms\n"
    )


def test_build_paths_basic(monkeypatch):
    """Hop IPs are converted to generic labels when SNMP is disabled."""

    def fake_check_output(cmd, text=True):
        return _traceroute_output(cmd[-1])

    monkeypatch.setattr("src.topology_builder.subprocess.check_output", fake_check_output)

    result = build_paths(["192.168.0.10"])
    assert result == {
        "paths": [{"ip": "192.168.0.10", "path": ["LAN", "Router", "Host"]}]
    }


def test_build_paths_with_snmp(monkeypatch):
    """SNMP neighbor names replace router labels when requested."""

    def fake_check_output(cmd, text=True):
        return _traceroute_output(cmd[-1])

    def fake_neighbors(ip, community="public"):
        return ["SwitchA"] if ip == "192.168.0.1" else []

    monkeypatch.setattr("src.topology_builder.subprocess.check_output", fake_check_output)
    monkeypatch.setattr("src.topology_builder._get_lldp_neighbors", fake_neighbors)
    monkeypatch.setattr("src.topology_builder.nextCmd", object())

    result = build_paths(["192.168.0.20"], use_snmp=True)
    assert result == {
        "paths": [{"ip": "192.168.0.20", "path": ["LAN", "SwitchA", "Host"]}]
    }


def test_build_paths_snmp_unavailable(monkeypatch):
    """Paths stay generic when pysnmp is missing."""

    def fake_check_output(cmd, text=True):
        return _traceroute_output(cmd[-1])

    monkeypatch.setattr("src.topology_builder.subprocess.check_output", fake_check_output)
    monkeypatch.setattr("src.topology_builder.nextCmd", None)

    result = build_paths(["192.168.0.30"], use_snmp=True)
    assert result["paths"][0]["path"] == ["LAN", "Router", "Host"]


def test_build_topology_wrapper(monkeypatch):
    """JSON wrapper returns only path arrays."""

    def fake_check_output(cmd, text=True):
        return _traceroute_output(cmd[-1])

    monkeypatch.setattr("src.topology_builder.subprocess.check_output", fake_check_output)

    data = json.loads(build_topology(["192.168.0.40", "192.168.0.41"]))
    assert data == {"paths": [["LAN", "Router", "Host"], ["LAN", "Router", "Host"]]}


def test_build_topology_for_subnet(monkeypatch):
    """Hosts are discovered before building topology."""

    def fake_discover(subnet):
        assert subnet == "192.168.0.0/24"
        return [{"ip": "192.168.0.50"}, {"ip": "192.168.0.51"}]

    def fake_check_output(cmd, text=True):
        return _traceroute_output(cmd[-1])

    monkeypatch.setattr("src.discover_hosts.discover_hosts", fake_discover)
    monkeypatch.setattr("src.topology_builder.subprocess.check_output", fake_check_output)

    data = json.loads(build_topology_for_subnet("192.168.0.0/24"))
    assert data == {"paths": [["LAN", "Router", "Host"], ["LAN", "Router", "Host"]]}

