"""Tests for :func:`discover_hosts`."""

import socket
import subprocess

import requests
from pathlib import Path

from src.discover_hosts import discover_hosts


def test_discover_hosts_resolves_hostname_and_vendor(monkeypatch):
    """Ensure host discovery returns hostnames and vendors."""

    def fake_check_output(cmd, text=True):
        if cmd[:2] == ["nmap", "-sn"]:
            assert cmd == ["nmap", "-sn", "-oG", "-", "-R", "192.168.0.0/24"]
            return (
                "Host: 192.168.0.10 (printer) Status: Up\n"
                "Host: 192.168.0.10 () MAC Address: 00:11:22:33:44:55\n"
                "Host: 192.168.0.20 Status: Up\n"
                "Host: 192.168.0.20 () MAC Address: 66:77:88:99:AA:BB\n"
            )
        if cmd[0] == "nbtscan":
            assert cmd == ["nbtscan", "-q", "192.168.0.20"]
            return "192.168.0.20 host20\n"
        if cmd[0] == "avahi-resolve":
            raise AssertionError("avahi-resolve should not be called when nbtscan succeeds")
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    api_calls = []

    def fake_get(url, timeout=5):
        api_calls.append(url)
        mac = url.rsplit("/", 1)[1]
        mapping = {
            "00:11:22:33:44:55": "VendorA",
            "66:77:88:99:AA:BB": "VendorB",
        }
        class Resp:
            status_code = 200
            text = mapping[mac]

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)

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
    assert set(api_calls) == {
        "https://api.macvendors.com/00:11:22:33:44:55",
        "https://api.macvendors.com/66:77:88:99:AA:BB",
    }


def test_discover_hosts_avahi_fallback(monkeypatch):
    """Fallback to ``avahi-resolve`` when ``nbtscan`` fails."""

    calls = []

    def fake_check_output(cmd, text=True):
        calls.append(cmd)
        if cmd[:2] == ["nmap", "-sn"]:
            assert cmd == ["nmap", "-sn", "-oG", "-", "-R", "192.168.0.0/24"]
            return (
                "Host: 192.168.0.30 Status: Up\n"
                "Host: 192.168.0.30 () MAC Address: AA:BB:CC:DD:EE:FF\n"
            )
        if cmd[0] == "nbtscan":
            assert cmd == ["nbtscan", "-q", "192.168.0.30"]
            raise subprocess.CalledProcessError(1, cmd)
        if cmd[0] == "avahi-resolve":
            assert cmd == ["avahi-resolve", "-a", "192.168.0.30"]
            return "192.168.0.30 host30\n"
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    def fake_get(url, timeout=5):
        assert url == "https://api.macvendors.com/AA:BB:CC:DD:EE:FF"
        class Resp:
            status_code = 200
            text = "VendorC"

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)

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


def test_discover_hosts_vendor_from_local_oui(monkeypatch):
    """Use local ``oui.txt`` instead of API when available."""

    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    oui_path = data_dir / "oui.txt"
    oui_path.write_text("00:11:22 VendorLocal\n")

    def fake_check_output(cmd, text=True):
        if cmd[:2] == ["nmap", "-sn"]:
            assert cmd == ["nmap", "-sn", "-oG", "-", "-R", "192.168.0.0/24"]
            return (
                "Host: 192.168.0.40 (host40) Status: Up\n"
                "Host: 192.168.0.40 () MAC Address: 00:11:22:AA:BB:CC\n"
            )
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    def fake_get(url, timeout=5):
        raise AssertionError("API should not be called when oui.txt exists")

    monkeypatch.setattr(requests, "get", fake_get)

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
    monkeypatch.addfinalizer(lambda: oui_path.unlink())

    result = discover_hosts("192.168.0.0/24")
    assert result == [{"ip": "192.168.0.40", "hostname": "host40", "vendor": "VendorLocal"}]
