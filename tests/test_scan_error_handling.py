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

# helper patch functions for each module


def patch_ports(mp):
    mp.setattr(
        ports.socket,
        "create_connection",
        lambda *_, **__: (_ for _ in ()).throw(OSError("boom")),
    )


def patch_os_banner(mp):
    def fail():
        raise os_banner.nmap.PortScannerError("boom")

    mp.setattr(os_banner.nmap, "PortScanner", fail)


def patch_smb_netbios(mp):
    class DummyNB:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("nb fail")

    mp.setattr(smb_netbios, "NetBIOS", DummyNB)

    class DummySMB:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("smb fail")

    mp.setattr(smb_netbios, "SMBConnection", DummySMB)


def patch_upnp(mp):
    mp.setattr(
        upnp, "sr1", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("boom"))
    )


def patch_arp_spoof(mp):
    mp.setattr(
        arp_spoof,
        "_get_arp_table",
        lambda *_, **__: (_ for _ in ()).throw(RuntimeError("boom")),
    )


def patch_dhcp(mp):
    mp.setattr(
        dhcp, "srp", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("boom"))
    )


def patch_dns(mp):
    mp.setattr(dns, "sr1", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("boom")))


def patch_ssl_cert(mp):
    mp.setattr(
        ssl_cert.socket,
        "create_connection",
        lambda *_, **__: (_ for _ in ()).throw(OSError("boom")),
    )


CASES = [
    ("ports", ports, patch_ports, ("host",)),
    ("os_banner", os_banner, patch_os_banner, ("host",)),
    ("smb_netbios", smb_netbios, patch_smb_netbios, ("host",)),
    ("upnp", upnp, patch_upnp, ()),
    ("arp_spoof", arp_spoof, patch_arp_spoof, (0,)),
    ("dhcp", dhcp, patch_dhcp, ()),
    ("dns", dns, patch_dns, ()),
    ("ssl_cert", ssl_cert, patch_ssl_cert, ("example.com",)),
]


@pytest.mark.parametrize("name, module, apply_patch, args", CASES)
def test_scan_handles_errors_and_returns_structure(
    name, module, apply_patch, args, monkeypatch
):
    apply_patch(monkeypatch)
    result = module.scan(*args)
    assert result["category"] == name
    assert result["score"] == 0
    assert "details" in result and isinstance(result["details"], dict)
    assert "error" in result["details"]
