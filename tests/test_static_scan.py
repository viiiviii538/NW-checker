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
from src.models import ScanResult, compute_total, compute_score
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
        assert isinstance(data, ScanResult)
        assert data.category == category
        assert isinstance(data.score, int)
        assert isinstance(data.message, str)
        assert isinstance(data.severity, str)


def test_run_all_propagates_scanner_exception(monkeypatch):
    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(static_scan, "SCANNERS", [boom])

    with pytest.raises(RuntimeError):
        static_scan.run_all()


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
def test_individual_scans_return_scanresult(module, category):
    result = module.scan()
    assert isinstance(result, ScanResult)
    assert result.category == category
    assert isinstance(result.score, int)
    assert isinstance(result.severity, str)


def test_helper_functions_compute_scores_and_total():
    low = compute_score("low")
    high = compute_score("high")
    assert high > low
    results = [
        ScanResult("a", "", low, "low"),
        ScanResult("b", "", high, "high"),
    ]
    assert compute_total(results) == low + high


def test_scanresult_factory_computes_score():
    result = ScanResult.from_severity("cat", "msg", "medium")
    assert result.score == compute_score("medium")
    assert result.category == "cat"
    assert result.message == "msg"
    assert result.severity == "medium"
