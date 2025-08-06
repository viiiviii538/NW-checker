from src import static_scan
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
import pytest


def test_run_all_returns_all_categories():
    results = static_scan.run_all()
    expected = {
        "ports",
        "os_banner",
        "smb_netbios",
        "upnp",
        "arp_spoof",
        "dhcp",
        "dns",
        "ssl_cert",
    }
    assert set(results.keys()) == expected
    for category, data in results.items():
        assert data["category"] == category
        assert isinstance(data["score"], int)
        assert isinstance(data["details"], dict)


@pytest.mark.parametrize(
    "module,category",
    [
        (ports, "ports"),
        (os_banner, "os_banner"),
        (smb_netbios, "smb_netbios"),
        (upnp, "upnp"),
        (arp_spoof, "arp_spoof"),
        (dhcp, "dhcp"),
        (dns, "dns"),
        (ssl_cert, "ssl_cert"),
    ],
)
def test_individual_scans_return_structured_data(module, category):
    result = module.scan()
    assert result["category"] == category
    assert isinstance(result["score"], int)
    assert isinstance(result["details"], dict)
