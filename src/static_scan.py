"""Aggregate and run all static network scan modules."""

from __future__ import annotations

import importlib
import pkgutil
from concurrent.futures import ThreadPoolExecutor, wait
from typing import Any, Callable, Dict, Iterable, List, Tuple

from . import scans
from .models import ScanResult

DEFAULT_TIMEOUT = 5  # seconds


def _discover_scanners() -> List[Tuple[str, Callable[[], ScanResult]]]:
    """Return list of (module_name, scan_function) under :mod:`scans`."""
    scanners: List[Tuple[str, Callable[[], ScanResult]]] = []
    for info in pkgutil.iter_modules(scans.__path__):
        module = importlib.import_module(f"{scans.__name__}.{info.name}")
        scan = getattr(module, "scan", None)
        if callable(scan):
            scanners.append((info.name, scan))
    return scanners


def _result_to_dict(result: ScanResult) -> Dict[str, Any]:
    """Convert :class:`ScanResult` to plain dictionary."""
    return {
        "category": result.category,
        "message": result.message,
        "score": result.score,
        "severity": result.severity,
    }


def run_all(timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Run all static scans concurrently and return aggregated results.

    Parameters
    ----------
    timeout:
        Time limit in seconds for all scans. Scans still running after this
        period are marked as timed out.
    """

    scanners = _discover_scanners()
    results: List[Dict[str, Any]] = []

    with ThreadPoolExecutor() as executor:
        future_to_category = {executor.submit(scan): name for name, scan in scanners}
        done, not_done = wait(future_to_category, timeout=timeout)

        for future in done:
            category = future_to_category[future]
            try:
                res = future.result()
                results.append(_result_to_dict(res))
            except Exception as exc:  # pylint: disable=broad-except
                # エラーも結果として記録
                results.append(
                    {
                        "category": category,
                        "message": str(exc),
                        "severity": "error",
                        "score": 0,
                    }
                )

        for future in not_done:
            category = future_to_category[future]
            results.append(
                {
                    "category": category,
                    "message": "timeout",
                    "severity": "error",
                    "score": 0,
                }
            )
            future.cancel()

    risk_score = sum(item["score"] for item in results)
    return {"findings": results, "risk_score": risk_score}
