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


def test_os_banner_scan_handles_no_results(monkeypatch):
    class MockScanner:
        def scan(self, target, arguments=""):
            return {"scan": {target: {"tcp": {}, "osmatch": []}}}

    monkeypatch.setattr(os_banner.nmap, "PortScanner", lambda: MockScanner())
    result = os_banner.scan("host")
    assert result["score"] == 0
    assert result["details"]["banners"] == {}
    assert result["details"]["os"] == ""


def test_smb_netbios_scan_detects_smb1(monkeypatch):
    class DummyNB:
        def queryIPForName(self, target, timeout=2):  # noqa: D401, ARG002
            return ["HOST"]

        def close(self):
            pass

    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            pass

        def getDialect(self):
            return 0x0000  # SMBv1

        def logoff(self):
            pass

    monkeypatch.setattr(smb_netbios, "NetBIOS", lambda: DummyNB())
    monkeypatch.setattr(smb_netbios, "SMBConnection", DummyConn)

    result = smb_netbios.scan("host")
    assert result["score"] == 5
    assert result["details"]["smb1_enabled"] is True
    assert result["details"]["netbios_names"] == ["HOST"]


# --- scapy based scans ---------------------------------------------------


def test_upnp_scan_flags_open_service(monkeypatch):
    response = SimpleNamespace(
        src="1.2.3.4", load=b"HTTP/1.1 200 OK\r\nSERVER: upnp\r\n\r\n"
    )
    monkeypatch.setattr(upnp, "sr1", lambda *_, **__: response)
    result = upnp.scan()
    assert result["score"] == 1
    assert result["details"]["responders"] == ["1.2.3.4"]
    assert "1.2.3.4" in result["details"]["warnings"][0]


def test_upnp_scan_flags_misconfigured(monkeypatch):
    response = SimpleNamespace(src="5.6.7.8", load=b"BAD RESPONSE")
    monkeypatch.setattr(upnp, "sr1", lambda *_, **__: response)
    result = upnp.scan()
    assert result["score"] == 1
    assert result["details"]["responders"] == ["5.6.7.8"]
    assert "Misconfigured" in result["details"]["warnings"][0]


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
