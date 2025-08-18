import time
from src import static_scan

def test_load_scanners_discovers_modules():
    scanners = static_scan._load_scanners()
    names = {name for name, _ in scanners}
    # Ensure common scan modules are discovered
    assert {'ports', 'os_banner'}.issubset(names)

def test_run_all_executes_scanners_concurrently(monkeypatch):
    """Scans should run in parallel to reduce total execution time."""

    def make_slow(name):
        def slow_scan():
            time.sleep(1)
            return {"category": name, "score": 1, "details": {}}
        return slow_scan

    monkeypatch.setattr(
        static_scan,
        "_load_scanners",
        lambda: [("slow1", make_slow("slow1")), ("slow2", make_slow("slow2"))],
    )

    start = time.perf_counter()
    result = static_scan.run_all()
    elapsed = time.perf_counter() - start

    # Would take ~2s sequentially; concurrent run should be significantly faster
    assert elapsed < 1.8
    assert result["risk_score"] == 2
    categories = [item["category"] for item in result["findings"]]
    assert {"slow1", "slow2"} == set(categories)


def test_run_all_handles_no_scanners(monkeypatch):
    """When no scanners are discovered, run_all should return empty results."""
    monkeypatch.setattr(static_scan, "_load_scanners", lambda: [])
    result = static_scan.run_all()
    assert result["findings"] == []
    assert result["risk_score"] == 0
