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
import time


def _findings_by_category(results):
    return {item["category"]: item for item in results["findings"]}


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
    categories = {item["category"] for item in results["findings"]}
    assert categories == expected
    assert isinstance(results["risk_score"], int)
    for item in results["findings"]:
        assert isinstance(item["score"], int)
        assert isinstance(item["details"], dict)


def test_run_all_totals_scores():
    results = static_scan.run_all()
    total = sum(item["score"] for item in results["findings"])
    assert results["risk_score"] == total


def test_run_all_handles_exceptions_and_timeouts(monkeypatch):
    def boom():
        raise RuntimeError("boom")

    def slow():
        time.sleep(2)

    monkeypatch.setattr(dns, "scan", boom)
    monkeypatch.setattr(os_banner, "scan", slow)

    results = static_scan.run_all(timeout=0.5)
    by_cat = _findings_by_category(results)

    assert by_cat["dns"]["details"]["error"] == "boom"
    assert by_cat["dns"]["score"] == 0
    assert by_cat["os_banner"]["details"]["error"] == "timeout"
    assert by_cat["os_banner"]["score"] == 0


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
