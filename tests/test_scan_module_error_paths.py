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


def fail_ports(mp):
    def bad_conn(addr, timeout=0.5):
        raise RuntimeError("boom")
    mp.setattr(ports.socket, "create_connection", bad_conn)


def fail_os_banner(mp):
    class BoomScanner:
        def scan(self, *_, **__):  # noqa: D401
            raise RuntimeError("boom")
    mp.setattr(os_banner.nmap, "PortScanner", lambda: BoomScanner())


def fail_smb_netbios(mp):
    class DummyNB:
        def queryIPForName(self, target, timeout=2):  # noqa: D401, ARG002
            return []
        def close(self):  # noqa: D401
            pass
    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            pass
        def getDialect(self):  # noqa: D401
            return 0x0000
        def logoff(self):  # noqa: D401
            pass
    mp.setattr(smb_netbios, "NetBIOS", lambda: DummyNB())
    mp.setattr(smb_netbios, "SMBConnection", DummyConn)
    def bad_lookup(target):  # noqa: D401
        raise RuntimeError("boom")
    mp.setattr(smb_netbios, "_nmblookup_names", bad_lookup)


def fail_upnp(mp):
    def boom(*_, **__):
        raise RuntimeError("boom")
    mp.setattr(upnp, "sr1", boom)


def fail_arp_spoof(mp):
    mp.setattr(arp_spoof, "_get_arp_table", lambda: {})
    def boom(*_, **__):
        raise RuntimeError("boom")
    mp.setattr(arp_spoof, "send", boom)
    mp.setattr(arp_spoof.time, "sleep", lambda *_: None)


def fail_dhcp(mp):
    def boom(*_, **__):
        raise RuntimeError("boom")
    mp.setattr(dhcp, "srp", boom)


def fail_dns(mp):
    mp.setattr(dns, "_get_nameservers", lambda: ["8.8.8.8"])
    def boom(*_, **__):
        raise RuntimeError("boom")
    mp.setattr(dns, "sr1", boom)


def fail_ssl_cert(mp):
    def boom(*_, **__):
        raise RuntimeError("boom")
    mp.setattr(ssl_cert.ssl, "create_default_context", boom)


FAIL_CASES = [
    ("ports", ports, fail_ports, ("host",)),
    ("os_banner", os_banner, fail_os_banner, ("host",)),
    ("smb_netbios", smb_netbios, fail_smb_netbios, ("host",)),
    ("upnp", upnp, fail_upnp, ()),
    ("arp_spoof", arp_spoof, fail_arp_spoof, (0,)),
    ("dhcp", dhcp, fail_dhcp, ()),
    ("dns", dns, fail_dns, ()),
    ("ssl_cert", ssl_cert, fail_ssl_cert, ("example.com",)),
]


@pytest.mark.parametrize("name, module, apply_patch, args", FAIL_CASES)
def test_scan_module_error(name, module, apply_patch, args, monkeypatch):
    apply_patch(monkeypatch)
    result = module.scan(*args)
    assert result["category"] == name
    assert result["score"] == 0
    assert "error" in result["details"]
