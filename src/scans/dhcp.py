"""Static scan for DHCP servers."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy DHCP data."""
    severity = "low"
    message = "No rogue DHCP servers found."
    return ScanResult.from_severity(category="dhcp", message=message, severity=severity)
