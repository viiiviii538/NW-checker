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
    """Execute all static scanners in parallel and aggregate their results.

    Parameters
    ----------
    timeout:
        Maximum time (in seconds) to wait for each individual scanner.

    Returns
    -------
    dict
        A mapping containing a ``findings`` list with each scanner's result and
        the aggregated ``risk_score``.
    """

    # Discover available scanners then prioritise important ones.
    scanners = _load_scanners()
    priority = ["ports", "os_banner"]
    scanners.sort(key=lambda x: priority.index(x[0]) if x[0] in priority else len(priority))

    findings: List[Dict] = []
    risk_score = 0

    # Run all scanners concurrently while keeping the execution order defined
    # above so that tests can rely on deterministic output positions.
    with ThreadPoolExecutor() as pool:
        futures = [(name, pool.submit(scan)) for name, scan in scanners]
        for name, future in futures:
            try:
                result = future.result(timeout=timeout)
            except TimeoutError:
                result = {"category": name, "score": 0, "details": {"error": "timeout"}}
            except Exception as exc:  # noqa: BLE001 - surface scan errors
                result = {"category": name, "score": 0, "details": {"error": str(exc)}}
            else:
                # Ensure mandatory fields exist even if the scanner omitted them.
                result.setdefault("category", name)
                result.setdefault("score", 0)
                result.setdefault("details", {})

            findings.append(result)
            risk_score += result.get("score", 0)

    return {"findings": findings, "risk_score": risk_score}
