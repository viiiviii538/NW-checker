"""Run all static scan modules concurrently with fault tolerance."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from importlib import import_module
from pkgutil import iter_modules
from typing import Dict, List, Tuple

from . import scans


def _load_scanners() -> List[Tuple[str, callable]]:
    """Discover scan functions under :mod:`src.scans`.

    Returns a list of ``(module_name, scan_callable)`` tuples.
    """

    scanners: List[Tuple[str, callable]] = []
    for mod_info in iter_modules(scans.__path__):
        if mod_info.name.startswith("_"):
            continue
        module = import_module(f"{scans.__name__}.{mod_info.name}")
        scan_func = getattr(module, "scan", None)
        if callable(scan_func):
            scanners.append((mod_info.name, scan_func))
    return scanners


def run_all(timeout: float = 5.0) -> Dict[str, List[Dict]]:
    """静的スキャンモジュールを並列実行し結果を集約する。"""

    scanners = _load_scanners()

    # ポートスキャンを最優先、次に OS 情報を取得するモジュールを実行
    priority = ["ports", "os_banner"]
    scanners.sort(key=lambda x: priority.index(x[0]) if x[0] in priority else len(priority))

    findings: List[Dict] = []
    with ThreadPoolExecutor() as pool:
        future_list = [(name, pool.submit(scan)) for name, scan in scanners]
        for name, future in future_list:
            try:
                result = future.result(timeout=timeout)
            except TimeoutError:
                result = {
                    "category": name,
                    "score": 0,
                    "details": {"error": "timeout"},
                }
            except Exception as exc:  # noqa: BLE001 - スキャン失敗も結果に反映
                result = {
                    "category": name,
                    "score": 0,
                    "details": {"error": str(exc)},
                }
            else:
                # 必須フィールドの欠損を補完
                result.setdefault("category", name)
                result.setdefault("score", 0)
                result.setdefault("details", {})

            findings.append(result)

    risk_score = sum(item.get("score", 0) for item in findings)
    return {"findings": findings, "risk_score": risk_score}
