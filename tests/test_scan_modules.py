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


def test_os_banner_scan_handles_exception(monkeypatch):
    class MockScanner:
        def scan(self, target, arguments=""):
            raise os_banner.nmap.PortScannerError("nmap error")

    monkeypatch.setattr(os_banner.nmap, "PortScanner", lambda: MockScanner())
    result = os_banner.scan("host")
    assert result["score"] == 0
    assert result["details"]["banners"] == {}
    assert result["details"]["os"] == ""
    assert "nmap error" in result["details"]["error"]


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


def test_smb_netbios_scan_no_smb1(monkeypatch):
    class DummyNB:
        def queryIPForName(self, target, timeout=2):  # noqa: D401, ARG002
            return []

        def close(self):
            pass

    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            pass

        def getDialect(self):
            return 0x0300  # SMB2

        def logoff(self):
            pass

    monkeypatch.setattr(smb_netbios, "NetBIOS", lambda: DummyNB())
    monkeypatch.setattr(smb_netbios, "SMBConnection", DummyConn)

    result = smb_netbios.scan("host")
    assert result["score"] == 0
    assert result["details"]["smb1_enabled"] is False
    assert result["details"]["netbios_names"] == []


def test_smb_netbios_scan_handles_errors(monkeypatch):
    def failing_nb():
        raise RuntimeError("nb fail")

    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            raise OSError("connection refused")

    monkeypatch.setattr(smb_netbios, "NetBIOS", failing_nb)
    monkeypatch.setattr(smb_netbios, "SMBConnection", DummyConn)

    result = smb_netbios.scan("host")
    assert result["score"] == 0
    assert result["details"]["smb1_enabled"] is False
    assert result["details"]["netbios_names"] == []
    assert "connection refused" in result["details"]["error"]


def test_smb_netbios_scan_uses_nmblookup(monkeypatch):
    """Fallback to ``nmblookup`` when impacket NetBIOS fails."""

    def failing_nb():
        raise RuntimeError("nb fail")

    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            raise OSError("conn fail")

    sample = """
Looking up status of 1.2.3.4
    HOSTNAME        <00> -         B
    MAC Address = 00-00-00-00-00-00
"""

    monkeypatch.setattr(smb_netbios, "NetBIOS", failing_nb)
    monkeypatch.setattr(smb_netbios, "SMBConnection", DummyConn)
    monkeypatch.setattr(smb_netbios.subprocess, "check_output", lambda *_, **__: sample)

    result = smb_netbios.scan("host")
    assert result["details"]["netbios_names"] == ["HOSTNAME"]


# Additional tests for NetBIOS helper

def test_nmblookup_names_parses_output(monkeypatch):
    sample = """\
Looking up status of 1.2.3.4
    HOST1          <00> -         B
    WORKGROUP      <00> - <GROUP>
    MAC Address = 00-00-00-00-00-00
"""
    monkeypatch.setattr(
        smb_netbios.subprocess, "check_output", lambda *_, **__: sample
    )
    assert smb_netbios._nmblookup_names("1.2.3.4") == ["HOST1", "WORKGROUP"]


def test_nmblookup_names_handles_failure(monkeypatch):
    def boom(*args, **kwargs):  # noqa: D401, ARG001, ARG002
        raise RuntimeError("boom")

    monkeypatch.setattr(smb_netbios.subprocess, "check_output", boom)
    assert smb_netbios._nmblookup_names("1.2.3.4") == []

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


def test_upnp_scan_handles_no_response(monkeypatch):
    """No responder should yield empty findings."""
    monkeypatch.setattr(upnp, "sr1", lambda *_, **__: None)
    result = upnp.scan()
    assert result["score"] == 0
    assert result["details"]["responders"] == []
    assert result["details"]["warnings"] == []


def test_upnp_scan_handles_errors(monkeypatch):
    """Exceptions from scapy should not crash the scan."""

    def boom(*_, **__):  # noqa: D401, ARG002
        raise RuntimeError("boom")

    monkeypatch.setattr(upnp, "sr1", boom)
    result = upnp.scan()
    assert result["score"] == 0
    assert result["details"]["responders"] == []
    assert result["details"]["warnings"] == []


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
    assert result["details"]["warnings"] == []


def test_dhcp_scan_warns_on_conflict(monkeypatch):
    class FakePkt:
        def __init__(self, src):
            self.src = src

        def __contains__(self, item):
            return True

        def __getitem__(self, layer):
            return SimpleNamespace(src=self.src)

    pkts = [(None, FakePkt("10.0.0.1")), (None, FakePkt("10.0.0.2"))]
    monkeypatch.setattr(dhcp, "srp", lambda *_, **__: (pkts, None))
    result = dhcp.scan()
    assert result["score"] == 2
    assert sorted(result["details"]["servers"]) == ["10.0.0.1", "10.0.0.2"]
    assert "Multiple DHCP servers detected" in result["details"]["warnings"][0]


def test_dhcp_scan_deduplicates_servers(monkeypatch):
    class FakePkt:
        def __init__(self, src):
            self.src = src

        def __contains__(self, item):
            return True

        def __getitem__(self, layer):
            return SimpleNamespace(src=self.src)

    pkts = [(None, FakePkt("10.0.0.1")), (None, FakePkt("10.0.0.1"))]
    monkeypatch.setattr(dhcp, "srp", lambda *_, **__: (pkts, None))
    result = dhcp.scan()
    assert result["score"] == 1
    assert result["details"]["servers"] == ["10.0.0.1"]


def test_arp_spoof_scan_detects_table_change(monkeypatch):
    tables = [
        {"1.2.3.4": "aa:aa"},
        {"1.2.3.4": arp_spoof.FAKE_MAC},
    ]
    monkeypatch.setattr(arp_spoof, "_get_arp_table", lambda: tables.pop(0))
    monkeypatch.setattr(arp_spoof, "send", lambda *_, **__: None)
    result = arp_spoof.scan(wait=0)
    assert result["category"] == "arp_spoof"
    assert result["score"] == 5
    assert result["details"] == {
        "vulnerable": True,
        "explanation": "ARP table updated with spoofed entry",
    }


def test_arp_spoof_scan_no_change(monkeypatch):
    monkeypatch.setattr(arp_spoof, "_get_arp_table", lambda: {"1.2.3.4": "aa:aa"})
    monkeypatch.setattr(arp_spoof, "send", lambda *_, **__: None)
    result = arp_spoof.scan(wait=0)
    assert result["category"] == "arp_spoof"
    assert result["score"] == 0
    assert result["details"] == {
        "vulnerable": False,
        "explanation": "No ARP poisoning detected",
    }


def test_arp_spoof_custom_ip_mac(monkeypatch):
    """Custom IP/MACを指定しても検出できること。"""
    tables = [
        {"5.6.7.8": "aa:aa"},
        {"5.6.7.8": "bb:bb"},
    ]
    monkeypatch.setattr(arp_spoof, "_get_arp_table", lambda: tables.pop(0))
    monkeypatch.setattr(arp_spoof, "send", lambda *_, **__: None)
    result = arp_spoof.scan(wait=0, fake_ip="5.6.7.8", fake_mac="bb:bb")
    assert result["category"] == "arp_spoof"
    assert result["score"] == 5
    assert result["details"] == {
        "vulnerable": True,
        "explanation": "ARP table updated with spoofed entry",
    }


import arp_spoof


@pytest.mark.parametrize("message", ["send fail", "send error"])
def test_arp_spoof_scan_handles_send_error(monkeypatch, message):
    """send() が失敗した場合は score=0 を返し、エラーメッセージに内容を含める。"""

    def boom(*args, **kwargs):  # noqa: D401, ARG001
        raise RuntimeError(message)

    monkeypatch.setattr(arp_spoof, "send", failing_send)
    result = arp_spoof.scan(wait=0)
    assert result["score"] == 0
    assert result["category"] == "arp_spoof"
    assert result["details"] == {"error": "send fail"}



def test_arp_spoof_scan_handles_table_error(monkeypatch):
    """ARPテーブル取得エラー時の挙動を確認。"""

    def boom():  # noqa: D401
        raise RuntimeError("table fail")

    monkeypatch.setattr(arp_spoof, "_get_arp_table", boom)
    result = arp_spoof.scan(wait=0)
    assert result == {
        "category": "arp_spoof",
        "score": 0,
        "details": {"error": "table fail"},
    }
    assert "vulnerable" not in result["details"]
    assert "explanation" not in result["details"]


def test_arp_spoof_scan_handles_table_error_after_send(monkeypatch):
    """send後のARPテーブル取得エラー時の挙動を確認。"""

    tables = [{"1.2.3.4": "aa:aa"}]

    def get_table():
        if tables:
            return tables.pop(0)
        raise RuntimeError("table fail")

    monkeypatch.setattr(arp_spoof, "_get_arp_table", get_table)
    monkeypatch.setattr(arp_spoof, "send", lambda *_, **__: None)
    result = arp_spoof.scan(wait=0)
    assert result == {
        "category": "arp_spoof",
        "score": 0,
        "details": {"error": "table fail"},
    }
    assert "vulnerable" not in result["details"]
    assert "explanation" not in result["details"]


def test_arp_spoof_scan_waits(monkeypatch):
    current = 0.0

    def fake_time() -> float:
        return current

    def fake_sleep(seconds: float) -> None:
        nonlocal current
        current += seconds

    monkeypatch.setattr(arp_spoof.time, "time", fake_time)
    monkeypatch.setattr(arp_spoof.time, "sleep", fake_sleep)
    monkeypatch.setattr(arp_spoof, "_get_arp_table", lambda: {})
    monkeypatch.setattr(arp_spoof, "send", lambda *_, **__: None)

    start = fake_time()
    arp_spoof.scan(wait=1.5)
    elapsed = fake_time() - start
    assert elapsed == pytest.approx(1.5, abs=0.2)


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
