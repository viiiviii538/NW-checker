import types
from types import SimpleNamespace

import pytest

from src.scans import (
    ports,
    os_banner,
    smb_netbios,
    upnp,
    arp_spoof,
    dhcp,
    dns,
    ssl_cert,
)


class DummySock:
    """Context manager returning a dummy socket with optional cert."""

    def __init__(self, cert=None):
        self.cert = cert or {"notAfter": "Jun  1 00:00:00 2020 GMT"}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    # SSL wrapped socket exposes getpeercert
    def getpeercert(self):
        return self.cert


# --- nmap based scans ----------------------------------------------------


def test_ports_scan_counts_open_ports(monkeypatch):
    def fake_create_connection(addr, timeout=0.5):  # noqa: ARG001
        if addr[1] == 22:
            class Dummy:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):  # noqa: D401, ARG002
                    return False

            return Dummy()
        raise OSError

    monkeypatch.setattr(ports.socket, "create_connection", fake_create_connection)
    result = ports.scan("host")
    assert result["score"] == 1
    assert result["details"]["open_ports"] == [22]


def test_ports_scan_no_open_ports(monkeypatch):
    monkeypatch.setattr(
        ports.socket,
        "create_connection",
        lambda *_, **__: (_ for _ in ()).throw(OSError()),
    )
    result = ports.scan("host")
    assert result["score"] == 0
    assert result["details"]["open_ports"] == []


def test_os_banner_scan_collects_os_and_banners(monkeypatch):
    class MockScanner:
        def scan(self, target, arguments=""):
            return {
                "scan": {
                    target: {
                        "tcp": {"80": {"name": "http", "version": "Apache"}},
                        "osmatch": [{"name": "Linux"}],
                    }
                }
            }

    monkeypatch.setattr(os_banner.nmap, "PortScanner", lambda: MockScanner())
    result = os_banner.scan("host")
    assert result["score"] == 2
    assert result["details"]["banners"] == {80: "http Apache"}
    assert result["details"]["os"] == "Linux"


def test_smb_netbios_scan_lists_open_ports(monkeypatch):
    class MockScanner:
        def scan(self, target, arguments=""):
            return {
                "scan": {
                    target: {
                        "tcp": {"445": {"state": "open"}},
                        "udp": {"137": {"state": "open"}, "138": {"state": "closed"}},
                    }
                }
            }

    monkeypatch.setattr(smb_netbios.nmap, "PortScanner", lambda: MockScanner())
    result = smb_netbios.scan("host")
    assert result["score"] == 2
    assert set(result["details"]["open_ports"]) == {445, 137}


# --- scapy based scans ---------------------------------------------------

def test_upnp_scan_records_responder(monkeypatch):
    monkeypatch.setattr(upnp, "sr1", lambda *_, **__: SimpleNamespace(src="1.2.3.4"))
    result = upnp.scan()
    assert result["score"] == 1
    assert result["details"]["responders"] == ["1.2.3.4"]


def test_dns_scan_collects_answers(monkeypatch):
    class FakeAnswer:
        def __init__(self, rdata):
            self.rdata = rdata

    class FakeDNSLayer:
        def __init__(self):
            self.ancount = 1
            self.an = [FakeAnswer("1.2.3.4")]

    class FakeResp:
        def haslayer(self, layer):
            return True

        def __getitem__(self, layer):
            return FakeDNSLayer()

    monkeypatch.setattr(dns, "sr1", lambda *_, **__: FakeResp())
    result = dns.scan()
    assert result["score"] == 1
    assert result["details"]["answers"] == ["1.2.3.4"]


def test_dhcp_scan_detects_servers(monkeypatch):
    class FakePkt:
        def __contains__(self, item):
            return True

        def __getitem__(self, layer):
            return SimpleNamespace(src="10.0.0.1")

    monkeypatch.setattr(dhcp, "srp", lambda *_, **__: ([(None, FakePkt())], None))
    result = dhcp.scan()
    assert result["score"] == 1
    assert result["details"]["servers"] == ["10.0.0.1"]


def test_arp_spoof_scan_finds_conflicts(monkeypatch):
    class FakePkt:
        def __init__(self, ip, mac):
            self.ip = ip
            self.mac = mac

        def __contains__(self, item):
            return True

        def __getitem__(self, layer):
            return SimpleNamespace(op=2, psrc=self.ip, hwsrc=self.mac)

    packets = [FakePkt("1.1.1.1", "aa:aa"), FakePkt("1.1.1.1", "bb:bb")]
    monkeypatch.setattr(arp_spoof, "sniff", lambda *_, **__: packets)
    result = arp_spoof.scan()
    assert result["score"] == 1
    assert result["details"]["suspects"] == ["1.1.1.1"]


# --- SSL certificate -----------------------------------------------------

def test_ssl_cert_scan_flags_expired(monkeypatch):
    class DummyContext:
        def wrap_socket(self, sock, server_hostname=None):
            return DummySock()

    monkeypatch.setattr(ssl_cert.ssl, "create_default_context", lambda: DummyContext())
    monkeypatch.setattr(ssl_cert.socket, "create_connection", lambda *_, **__: DummySock())
    result = ssl_cert.scan("example.com")
    assert result["score"] == 1
    assert result["details"]["expired"] is True
