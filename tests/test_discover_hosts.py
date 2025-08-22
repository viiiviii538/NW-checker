"""Tests for :func:`discover_hosts`."""

import socket
import subprocess
import urllib.request

from src.discover_hosts import discover_hosts


def test_discover_hosts_resolves_hostname(monkeypatch):
    """Ensure host discovery and hostname resolution work."""

    def fake_check_output(cmd, text=True):
        if cmd[:2] == ["nmap", "-sn"]:
            assert cmd == ["nmap", "-sn", "-oG", "-", "-R", "192.168.0.0/24"]
            return (
                "Host: 192.168.0.10 (printer) Status: Up MAC: 00:00:00:00:00:01\n"
                "Host: 192.168.0.20 Status: Up MAC: 00:00:00:00:00:02\n"
            )
        if cmd[0] == "nbtscan":
            assert cmd == ["nbtscan", "-q", "192.168.0.20"]
            return "192.168.0.20 host20\n"
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    def fake_urlopen(url, timeout=5):
        class Resp:
            def __init__(self, data: str):
                self.data = data

            def read(self):
                return self.data.encode()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        if "00:00:00:00:00:01" in url:
            return Resp("VendorA")
        if "00:00:00:00:00:02" in url:
            return Resp("VendorB")
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    class DummySocket:
        def __init__(self, *args, **kwargs):
            pass

        def settimeout(self, timeout):
            pass

        def connect(self, addr):
            pass

        def close(self):
            pass

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: DummySocket())

    result = discover_hosts("192.168.0.0/24")
    assert result == [
        {"ip": "192.168.0.10", "hostname": "printer", "vendor": "VendorA"},
        {"ip": "192.168.0.20", "hostname": "host20", "vendor": "VendorB"},
    ]


def test_discover_hosts_avahi_fallback(monkeypatch):
    """Fallback to ``avahi-resolve`` when ``nbtscan`` fails."""

    calls = []

    def fake_check_output(cmd, text=True):
        calls.append(cmd)
        if cmd[:2] == ["nmap", "-sn"]:
            assert cmd == ["nmap", "-sn", "-oG", "-", "-R", "192.168.0.0/24"]
            return "Host: 192.168.0.30 Status: Up MAC: 00:00:00:00:00:03\n"
        if cmd[0] == "nbtscan":
            assert cmd == ["nbtscan", "-q", "192.168.0.30"]
            raise subprocess.CalledProcessError(1, cmd)
        if cmd[0] == "avahi-resolve":
            assert cmd == ["avahi-resolve", "-a", "192.168.0.30"]
            return "192.168.0.30 host30\n"
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    def fake_urlopen(url, timeout=5):
        class Resp:
            def read(self):
                return b"VendorC"

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        assert "00:00:00:00:00:03" in url
        return Resp()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    class DummySocket:
        def __init__(self, *args, **kwargs):
            pass

        def settimeout(self, timeout):
            pass

        def connect(self, addr):
            pass

        def close(self):
            pass

    monkeypatch.setattr(socket, "socket", lambda *a, **kw: DummySocket())

    result = discover_hosts("192.168.0.0/24")
    assert result == [{"ip": "192.168.0.30", "hostname": "host30", "vendor": "VendorC"}]
    # ensure nbtscan was tried before avahi-resolve
    assert calls[1][0] == "nbtscan"
    assert calls[2][0] == "avahi-resolve"
