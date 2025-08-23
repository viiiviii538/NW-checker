"""Tests for building topology paths."""

from src.topology_builder import build_paths


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

