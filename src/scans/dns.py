"""Static scan for DNS records."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy DNS data."""
    severity = "low"
    message = "No suspicious DNS records."
    return ScanResult.from_severity(category="dns", message=message, severity=severity)
