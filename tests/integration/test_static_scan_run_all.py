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


def _stub(module, score=1):
    return lambda module=module: {
        "category": module.__name__.split(".")[-1],
        "score": score,
        "details": {},
    }


def test_run_all_aggregates_scores(monkeypatch):
    modules = [ports, os_banner, smb_netbios, upnp, arp_spoof, dhcp, dns, ssl_cert]
    for mod in modules:
        monkeypatch.setattr(mod, "scan", _stub(mod))

    results = static_scan.run_all()
    total = sum(item["score"] for item in results["findings"])
    assert results["risk_score"] == total
    categories = {f["category"] for f in results["findings"]}
    assert categories == {
        "ports",
        "os_banner",
        "smb_netbios",
        "upnp",
        "arp_spoof",
        "dhcp",
        "dns",
        "ssl_cert",
    }
    assert [f["category"] for f in results["findings"]][:2] == ["ports", "os_banner"]


def test_run_all_handles_module_errors(monkeypatch):
    modules = [ports, os_banner, smb_netbios, upnp, arp_spoof, dhcp, dns, ssl_cert]
    for mod in modules:
        monkeypatch.setattr(mod, "scan", _stub(mod))

    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(dns, "scan", boom)

    results = static_scan.run_all()
    by_cat = {r["category"]: r for r in results["findings"]}
    assert by_cat["dns"]["score"] == 0
    assert by_cat["dns"]["details"]["error"] == "boom"
    assert results["risk_score"] == len(modules) - 1
