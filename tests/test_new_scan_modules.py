import types
from datetime import datetime, timedelta, timezone

import pytest

from src.scans import dns, dhcp, ssl_cert, arp_spoof


def test_dns_scan_success(monkeypatch):
    class FakeResp:
        ancount = 1
        arcount = 0
        ad = 1

        def __getitem__(self, item):
            return self

    monkeypatch.setattr(dns, "_get_nameservers", lambda path="/etc/resolv.conf": ["8.8.8.8"])
    monkeypatch.setattr(dns, "sr1", lambda *_, **__: FakeResp())
    result = dns.scan()
    assert result["score"] >= 0
    assert result["details"]["servers"] == ["8.8.8.8"]


def test_dns_scan_error(monkeypatch):
    monkeypatch.setattr(dns, "sr1", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("boom")))
    result = dns.scan()
    assert result["score"] == 0
    assert "boom" in result["details"]["error"]


def test_dhcp_scan_success(monkeypatch):
    class FakePkt:
        def __contains__(self, layer):  # noqa: D401
            return True

        def __getitem__(self, layer):  # noqa: D401
            return types.SimpleNamespace(src="1.2.3.4")

    monkeypatch.setattr(dhcp, "srp", lambda *_, **__: ([(None, FakePkt())], None))
    result = dhcp.scan()
    assert result["score"] == 1
    assert result["details"]["servers"] == ["1.2.3.4"]


def test_dhcp_scan_error(monkeypatch):
    monkeypatch.setattr(dhcp, "srp", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("dhcp fail")))
    result = dhcp.scan()
    assert result["score"] == 0
    assert "dhcp fail" in result["details"]["error"]


class DummySock:
    def __init__(self, cert=None):
        self.cert = cert or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: D401, ARG002
        return False

    def getpeercert(self):
        return self.cert


@pytest.fixture
def _ssl_context(monkeypatch):
    future = datetime.now(timezone.utc) + timedelta(days=60)
    not_after = future.strftime("%b %d %H:%M:%S %Y GMT")

    class DummyContext:
        def wrap_socket(self, sock, server_hostname=None):
            return DummySock({
                "notAfter": not_after,
                "issuer": ((("commonName", "Let's Encrypt"),),),
            })

    monkeypatch.setattr(ssl_cert.ssl, "create_default_context", lambda: DummyContext())
    monkeypatch.setattr(ssl_cert.socket, "create_connection", lambda *_, **__: DummySock())


def test_ssl_cert_scan_success(_ssl_context):
    result = ssl_cert.scan("example.com")
    assert result["score"] == 0
    assert result["details"]["issuer"] == "Let's Encrypt"


def test_ssl_cert_scan_error(monkeypatch):
    def boom(*args, **kwargs):  # noqa: D401, ARG001, ARG002
        raise OSError("connect fail")

    monkeypatch.setattr(ssl_cert.socket, "create_connection", boom)
    result = ssl_cert.scan("example.com")
    assert result["score"] == 0
    assert "connect fail" in result["details"]["error"]


def test_arp_spoof_scan_success(monkeypatch):
    tables = [{}, {arp_spoof.FAKE_IP: arp_spoof.FAKE_MAC}]
    monkeypatch.setattr(arp_spoof, "_get_arp_table", lambda: tables.pop(0))
    monkeypatch.setattr(arp_spoof, "send", lambda *_, **__: None)
    monkeypatch.setattr(arp_spoof.time, "sleep", lambda _: None)
    result = arp_spoof.scan(wait=0)
    assert result["score"] == 5
    assert result["details"]["vulnerable"] is True


def test_arp_spoof_scan_error(monkeypatch):
    monkeypatch.setattr(arp_spoof, "_get_arp_table", lambda: (_ for _ in ()).throw(RuntimeError("table fail")))
    result = arp_spoof.scan(wait=0)
    assert result["score"] == 0
    assert "table fail" in result["details"]["error"]
