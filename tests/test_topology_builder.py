"""Tests for :mod:`topology_builder`."""

import json

from src.topology_builder import build_topology, build_topology_for_subnet


def test_build_topology_basic(monkeypatch):
    def fake_traceroute(ip):
        return (
            f"traceroute to {ip} ({ip}), 30 hops max\n"
            "1  192.168.0.1  1.0 ms\n"
            f"2  {ip}  2.0 ms\n"
        )

    monkeypatch.setattr("src.topology_builder._run_traceroute", lambda ip: fake_traceroute(ip))
    monkeypatch.setattr("src.topology_builder._get_lldp_neighbors", lambda ip, community="public": [])

    result = json.loads(build_topology(["192.168.0.10"]))
    assert result == {"paths": [["LAN", "Router", "Host"]]}


def test_build_topology_with_snmp(monkeypatch):
    def fake_traceroute(ip):
        return (
            f"traceroute to {ip} ({ip}), 30 hops max\n"
            "1  192.168.0.1  1.0 ms\n"
            f"2  {ip}  2.0 ms\n"
        )

    def fake_neighbors(ip, community="public"):
        return ["SwitchA"] if ip == "192.168.0.1" else []

    monkeypatch.setattr("src.topology_builder._run_traceroute", lambda ip: fake_traceroute(ip))
    monkeypatch.setattr("src.topology_builder._get_lldp_neighbors", fake_neighbors)

    result = json.loads(build_topology(["192.168.0.20"], use_snmp=True))
    assert result == {"paths": [["LAN", "SwitchA", "Host"]]}


def test_build_topology_for_subnet(monkeypatch):
    """`build_topology_for_subnet` uses discovery results."""

    # Fake discovery returning two hosts
    monkeypatch.setattr(
        "src.topology_builder.discover_hosts.discover_hosts", lambda subnet: ["10.0.0.1", "10.0.0.2"]
    )

    def fake_traceroute(ip):
        return (
            f"traceroute to {ip} ({ip}), 30 hops max\n"
            "1  192.168.0.1  1.0 ms\n"
            f"2  {ip}  2.0 ms\n"
        )

    monkeypatch.setattr("src.topology_builder._run_traceroute", lambda ip: fake_traceroute(ip))
    monkeypatch.setattr("src.topology_builder._get_lldp_neighbors", lambda ip, community="public": [])

    result = json.loads(build_topology_for_subnet("192.168.0.0/24"))
    assert result == {"paths": [["LAN", "Router", "Host"], ["LAN", "Router", "Host"]]}
