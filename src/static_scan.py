"""Run all static scan modules concurrently with fault tolerance."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from importlib import import_module
from pkgutil import iter_modules
from typing import Dict, List, Tuple

from . import scans


def _load_scanners() -> List[Tuple[str, callable]]:
    """Discover scan functions under :mod:`src.scans` with ordering.

    ``ports`` を最初、``os_banner`` を2番目に配置し、残りはアルファベット順。
    """

    available: Dict[str, callable] = {}
    for mod_info in iter_modules(scans.__path__):
        if mod_info.name.startswith("_"):
            continue
        module = import_module(f"{scans.__name__}.{mod_info.name}")
        scan_func = getattr(module, "scan", None)
        if callable(scan_func):
            available[mod_info.name] = scan_func

    order = ["ports", "os_banner"]
    remaining = sorted(name for name in available if name not in order)
    ordered = [name for name in order if name in available] + remaining
    return [(name, available[name]) for name in ordered]


def run_all(timeout: float = 5.0) -> Dict[str, List[Dict]]:
    """Execute all static scans and aggregate their results.

    Each scan runs in a thread. Failures or timeouts still produce a result
    entry with ``score`` 0 and an ``error`` message in ``details``.
    """

    findings: List[Dict] = []
    scanners = _load_scanners()

    with ThreadPoolExecutor() as executor:
        futures = [(executor.submit(scan), name) for name, scan in scanners]
        for future, name in futures:
            try:
                result = future.result(timeout=timeout)
                # フィールド欠損時のフォールバック
                result.setdefault("category", name)
                result.setdefault("score", 0)
                result.setdefault("details", {})
            except TimeoutError:
                result = {
                    "category": name,
                    "score": 0,
                    "details": {"error": "timeout"},
                }
            except Exception as exc:  # noqa: BLE001 - エラーも結果に含める
                result = {
                    "category": name,
                    "score": 0,
                    "details": {"error": str(exc)},
                }
            findings.append(result)

    total = sum(item.get("score", 0) for item in findings)
    return {"findings": findings, "risk_score": total}

