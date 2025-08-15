from src import static_scan
import pytest
import time
import json

STUB_SCANS = {
    "ports": lambda: {"category": "ports", "score": 1, "details": {}},
    "os_banner": lambda: {"category": "os_banner", "score": 1, "details": {}},
    "smb_netbios": lambda: {"category": "smb_netbios", "score": 1, "details": {}},
    "upnp": lambda: {"category": "upnp", "score": 1, "details": {}},
    "arp_spoof": lambda: {"category": "arp_spoof", "score": 1, "details": {}},
    "dhcp": lambda: {"category": "dhcp", "score": 1, "details": {}},
    "dns": lambda: {"category": "dns", "score": 1, "details": {}},
    "ssl_cert": lambda: {"category": "ssl_cert", "score": 1, "details": {}},
}


@pytest.fixture(autouse=True)
def mock_all_scans(monkeypatch):
    monkeypatch.setattr(
        static_scan,
        "_load_scanners",
        lambda: [(name, func) for name, func in STUB_SCANS.items()],
    )


def _findings_by_category(results):
    return {item["category"]: item for item in results["findings"]}


def test_run_all_returns_all_categories():
    results = static_scan.run_all()
    expected = set(STUB_SCANS.keys())
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

    monkeypatch.setitem(STUB_SCANS, "dns", boom)
    monkeypatch.setitem(STUB_SCANS, "os_banner", slow)

    results = static_scan.run_all(timeout=0.5)
    by_cat = _findings_by_category(results)

    assert by_cat["dns"]["details"]["error"] == "boom"
    assert by_cat["dns"]["score"] == 0
    assert by_cat["os_banner"]["details"]["error"] == "timeout"
    assert by_cat["os_banner"]["score"] == 0


def test_run_all_populates_missing_fields(monkeypatch):
    """スキャン結果の欠損フィールドを補完することを確認"""

    def incomplete():
        return {}

    monkeypatch.setitem(STUB_SCANS, "dhcp", incomplete)

    results = static_scan.run_all()
    by_cat = _findings_by_category(results)
    entry = by_cat["dhcp"]

    assert entry["category"] == "dhcp"
    assert entry["score"] == 0
    assert entry["details"] == {}


def test_run_all_includes_dhcp_details(monkeypatch):
    """DHCPスキャンの結果が集約に含まれることを確認"""

    def fake_dhcp():
        return {
            "category": "dhcp",
            "score": 2,
            "details": {
                "servers": ["1.1.1.1", "2.2.2.2"],
                "warnings": [
                    "Multiple DHCP servers detected: 1.1.1.1, 2.2.2.2"
                ],
            },
        }

    monkeypatch.setitem(STUB_SCANS, "dhcp", fake_dhcp)

    results = static_scan.run_all()
    by_cat = _findings_by_category(results)
    entry = by_cat["dhcp"]

    assert entry["score"] == 2
    assert entry["details"]["servers"] == ["1.1.1.1", "2.2.2.2"]
    assert "Multiple DHCP servers detected" in entry["details"]["warnings"][0]


def test_run_all_is_json_serializable():
    """run_all の返り値が JSON シリアル化可能であることを確認"""

    results = static_scan.run_all()
    json.dumps(results)  # 例外が発生しなければOK


@pytest.mark.parametrize("category", list(STUB_SCANS.keys()))
def test_individual_scans_return_dict(category):
    result = STUB_SCANS[category]()
    assert result["category"] == category
    assert isinstance(result["score"], int)
    assert isinstance(result["details"], dict)


def test_ports_result_is_first():
    results = static_scan.run_all()
    assert results["findings"][0]["category"] == "ports"


def test_os_banner_result_is_second():
    results = static_scan.run_all()
    assert results["findings"][1]["category"] == "os_banner"
