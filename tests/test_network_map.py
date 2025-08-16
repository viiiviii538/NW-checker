"""Tests for :mod:`network_map`."""

import json

import pytest

from src import network_map


def test_network_map_delegates(monkeypatch):
    """network_map() delegates to discover_hosts."""

    calls = {}

    def fake_discover(subnet):
        calls["subnet"] = subnet
        return ["10.0.0.1"]

    monkeypatch.setattr(network_map, "discover_hosts", fake_discover)
    result = network_map.network_map("10.0.0.0/24")
    assert result == ["10.0.0.1"]
    assert calls["subnet"] == "10.0.0.0/24"


def test_network_map_success(monkeypatch, capsys):
    """JSON output and success log are emitted on success."""

    monkeypatch.setattr(network_map, "discover_hosts", lambda subnet: ["192.168.0.10"])
    exit_code = network_map.main(["192.168.0.0/24"])
    captured = capsys.readouterr()
    assert exit_code == 0
    out_lines = captured.out.strip().splitlines()
    assert json.loads(out_lines[0]) == ["192.168.0.10"]
    assert "succeeded" in out_lines[1]
    assert captured.err == ""


def test_network_map_failure(monkeypatch, capsys):
    """Errors are reported to stderr and non-zero exit code is returned."""

    def boom(subnet):
        raise RuntimeError("boom")

    monkeypatch.setattr(network_map, "discover_hosts", boom)
    exit_code = network_map.main(["192.168.0.0/24"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "boom" in captured.err


def test_main_requires_subnet_arg(capsys):
    """Missing subnet argument triggers usage message and exit code 2."""

    with pytest.raises(SystemExit) as exc:
        network_map.main([])
    captured = capsys.readouterr()
    assert exc.value.code == 2
    assert captured.out == ""
    assert "usage" in captured.err.lower()
