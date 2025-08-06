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
    assert set(results["findings"].keys()) == expected
    assert isinstance(results["risk_score"], int)
    for category, data in results["findings"].items():
        assert data["category"] == category
        assert isinstance(data["score"], int)
        assert isinstance(data["details"], dict)


def test_run_all_totals_scores():
    results = static_scan.run_all()
    total = sum(item["score"] for item in results["findings"].values())
    assert results["risk_score"] == total


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
def test_individual_scans_return_dict(module, category):
    result = module.scan()
    assert result["category"] == category
    assert isinstance(result["score"], int)
    assert isinstance(result["details"], dict)
