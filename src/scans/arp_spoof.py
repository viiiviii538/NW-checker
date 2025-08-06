"""Static scan for ARP spoofing attempts."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy ARP spoofing data."""
    severity = "low"
    message = "No ARP spoofing detected."
    return ScanResult.from_severity(category="arp_spoof", message=message, severity=severity)
