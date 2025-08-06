"""Aggregate multiple static network scan modules."""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from .scans import (
    ports,
    os_banner,
    smb_netbios,
    upnp,
    arp_spoof,
    dhcp,
    dns,
    ssl_cert,
)

SCANNERS = [
    ports.scan,
    os_banner.scan,
    smb_netbios.scan,
    upnp.scan,
    arp_spoof.scan,
    dhcp.scan,
    dns.scan,
    ssl_cert.scan,
]


def run_all() -> Dict[str, Dict]:
    """Run all static scans concurrently and aggregate their results.

    Returns a dictionary with ``findings`` mapping categories to result dicts and
    ``risk_score`` representing the total score across all scans.
    """

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(scanner) for scanner in SCANNERS]
        results = [future.result() for future in futures]

    findings: Dict[str, Dict] = {res["category"]: res for res in results}
    total = sum(res.get("score", 0) for res in results)

    return {"findings": findings, "risk_score": total}

