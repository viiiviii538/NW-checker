import types
from datetime import datetime, timedelta, timezone

import pytest

from src.scans import (
    arp_spoof,
    dhcp,
    dns,
    os_banner,
    ports,
    smb_netbios,
    ssl_cert,
    upnp,
)


def ok_ports(mp):
    class Dummy:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_conn(addr, timeout=0.5):
        if addr[1] == 22:
            return Dummy()
        raise OSError("closed")

    mp.setattr(ports.socket, "create_connection", fake_conn)


def ok_os_banner(mp):
    class MockScanner:
        def scan(self, target, arguments=None):  # noqa: D401
            return {
                "scan": {
                    target: {
                        "tcp": {"22": {"name": "ssh", "version": "7.9"}},
                        "osmatch": [{"name": "Linux"}],
                    }
                }
            }

    mp.setattr(os_banner.nmap, "PortScanner", lambda: MockScanner())


def ok_smb_netbios(mp):
    class DummyNB:
        def queryIPForName(self, target, timeout=2):  # noqa: D401
            return ["HOST"]

        def close(self):  # noqa: D401
            pass

    class DummyConn:
        def __init__(self, *args, **kwargs):
            pass

        def getDialect(self):  # noqa: D401
            return 0x0000

        def logoff(self):  # noqa: D401
            pass

    mp.setattr(smb_netbios, "NetBIOS", lambda: DummyNB())
    mp.setattr(smb_netbios, "SMBConnection", DummyConn)


def ok_upnp(mp):
    response = types.SimpleNamespace(
        src="1.2.3.4", load=b"HTTP/1.1 200 OK\r\nSERVER: upnp\r\n\r\n"
    )
    mp.setattr(upnp, "sr1", lambda *_, **__: response)


def ok_arp_spoof(mp):
    tables = [{}, {arp_spoof.FAKE_IP: arp_spoof.FAKE_MAC}]
    mp.setattr(arp_spoof, "_get_arp_table", lambda: tables.pop(0))
    mp.setattr(arp_spoof, "send", lambda *_, **__: None)
    mp.setattr(arp_spoof.time, "sleep", lambda _: None)


def ok_dhcp(mp):
    class FakePkt:
        def __contains__(self, layer):  # noqa: D401
            return True

        def __getitem__(self, layer):  # noqa: D401
            return types.SimpleNamespace(src="1.2.3.4")

    mp.setattr(dhcp, "srp", lambda *_, **__: ([(None, FakePkt())], None))


def ok_dns(mp):
    class FakeResp:
        ancount = 1
        arcount = 0
        ad = 1

        def __getitem__(self, item):  # noqa: D401
            return self

        def haslayer(self, layer):  # noqa: D401
            return True

    mp.setattr(dns, "_get_nameservers", lambda path="/etc/resolv.conf": ["8.8.8.8"])
    mp.setattr(dns, "sr1", lambda *_, **__: FakeResp())


def ok_ssl_cert(mp):
    future = datetime.now(timezone.utc) + timedelta(days=60)
    not_after = future.strftime("%b %d %H:%M:%S %Y GMT")

    class DummySock:
        def __init__(self, cert=None):
            self.cert = cert or {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # noqa: D401
            return False

        def getpeercert(self):  # noqa: D401
            return self.cert

    class DummyContext:
        def wrap_socket(self, sock, server_hostname=None):  # noqa: D401, ARG002
            return DummySock(
                {
                    "notAfter": not_after,
                    "issuer": ((("commonName", "Let's Encrypt"),),),
                }
            )

    mp.setattr(ssl_cert.ssl, "create_default_context", lambda: DummyContext())
    mp.setattr(ssl_cert.socket, "create_connection", lambda *_, **__: DummySock())


SUCCESS_CASES = [
    ("ports", ports, ok_ports, ("host",), 1),
    ("os_banner", os_banner, ok_os_banner, ("host",), 2),
    ("smb_netbios", smb_netbios, ok_smb_netbios, ("host",), 5),
    ("upnp", upnp, ok_upnp, (), 1),
    ("arp_spoof", arp_spoof, ok_arp_spoof, (0,), 5),
    ("dhcp", dhcp, ok_dhcp, (), 1),
    ("dns", dns, ok_dns, (), 1),
    ("ssl_cert", ssl_cert, ok_ssl_cert, ("example.com",), 0),
]


@pytest.mark.parametrize("name, module, apply_patch, args, expected", SUCCESS_CASES)
def test_scan_module_success(name, module, apply_patch, args, expected, monkeypatch):
    apply_patch(monkeypatch)
    result = module.scan(*args)
    assert result["category"] == name
    assert result["score"] == expected
    assert "error" not in result["details"]
