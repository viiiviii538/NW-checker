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
import time


def test_run_all_returns_all_categories():
    data = static_scan.run_all()
    categories = {item["category"] for item in data["findings"]}
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
    assert categories == expected
    assert data["risk_score"] == sum(item["score"] for item in data["findings"])


def test_run_all_handles_scanner_exception(monkeypatch):
    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(static_scan, "_discover_scanners", lambda: [("boom", boom)])

    data = static_scan.run_all()
    assert data["risk_score"] == 0
    assert len(data["findings"]) == 1
    item = data["findings"][0]
    assert item["category"] == "boom"
    assert item["severity"] == "error"
    assert "boom" in item["message"]


def test_run_all_handles_timeout(monkeypatch):
    def slow():
        time.sleep(0.2)
        return ScanResult.from_severity("slow", "done", "low")

    monkeypatch.setattr(static_scan, "_discover_scanners", lambda: [("slow", slow)])

    data = static_scan.run_all(timeout=0.05)
    assert len(data["findings"]) == 1
    item = data["findings"][0]
    assert item["category"] == "slow"
    assert item["severity"] == "error"
    assert "timeout" in item["message"]


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
