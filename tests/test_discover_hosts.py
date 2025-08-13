"""Tests for :func:`discover_hosts`."""

import socket
import subprocess

from src.discover_hosts import discover_hosts


def test_discover_hosts_monkeypatched(monkeypatch):
    """Ensure host discovery is independent from the external environment."""

    def fake_check_output(cmd, text=True):
        assert cmd == ["discover_hosts", "192.168.0.0/24"]
        # Pretend that the command discovered two hosts.
        return "192.168.0.10\n192.168.0.20\n"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    class DummySocket:
        def __init__(self, *args, **kwargs):
            pass

        def settimeout(self, timeout):
            pass

        def connect(self, addr):
            ip, _ = addr
            # Simulate that only the first IP responds.
            if ip != "192.168.0.10":
                raise OSError("unreachable")

        def close(self):
            pass

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: DummySocket())

    result = discover_hosts("192.168.0.0/24")
    assert result == ["192.168.0.10"]
