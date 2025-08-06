"""Static scan for UPnP services."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy UPnP data."""
    severity = "low"
    message = "No UPnP services discovered."
    return ScanResult.from_severity(category="upnp", message=message, severity=severity)
