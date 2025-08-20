"""Run all static scan modules concurrently with fault tolerance."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from importlib import import_module
from pkgutil import iter_modules
from typing import Callable

from . import scans

# ``ports`` と ``os_banner`` は他の結果よりも重要なため優先表示する
_PRIORITY_ORDER = ("ports", "os_banner")


def _load_scanners() -> list[tuple[str, Callable]]:
    """Dynamically discover scan modules under :mod:`src.scans`."""

    scanners: list[tuple[str, Callable]] = []
    for mod_info in iter_modules(scans.__path__):
        if mod_info.name.startswith("_"):
            continue  # private module
        module = import_module(f"{scans.__name__}.{mod_info.name}")
        scan_func = getattr(module, "scan", None)
        if callable(scan_func):
            scanners.append((mod_info.name, scan_func))
    return scanners


def run_all(timeout: float = 5.0) -> dict:
    """Execute all discovered scanners concurrently and aggregate results."""

    scanners = _load_scanners()
    scanners.sort(
        key=lambda x: _PRIORITY_ORDER.index(x[0])
        if x[0] in _PRIORITY_ORDER
        else len(_PRIORITY_ORDER)
    )

    findings: list[dict] = []
    risk_score = 0

    # Run scans concurrently yet preserve the defined order for deterministic output
    with ThreadPoolExecutor() as pool:
        futures = [(name, pool.submit(scan)) for name, scan in scanners]
        for name, future in futures:
            try:
                result = future.result(timeout=timeout)
            except TimeoutError:
                result = {"category": name, "score": 0, "details": {"error": "timeout"}}
            except Exception as exc:  # noqa: BLE001 - bubble up scan errors
                result = {"category": name, "score": 0, "details": {"error": str(exc)}}
            else:
                result.setdefault("category", name)
                result.setdefault("score", 0)
                result.setdefault("details", {})

            findings.append(result)
            risk_score += result.get("score", 0)

    return {"findings": findings, "risk_score": risk_score}
