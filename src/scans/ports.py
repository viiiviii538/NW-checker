"""Static scan for open ports."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy port scan data."""
    severity = "low"
    message = "No open ports detected."
    return ScanResult.from_severity(category="ports", message=message, severity=severity)
