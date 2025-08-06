"""Aggregate multiple static network scan modules."""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from .models import ScanResult
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


def run_all() -> Dict[str, ScanResult]:
    """Run all static scans concurrently and aggregate their results."""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(scanner) for scanner in SCANNERS]
        results = [future.result() for future in futures]

    combined: Dict[str, ScanResult] = {res.category: res for res in results}
    return combined
