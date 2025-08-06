"""Static scan for SSL certificates."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy SSL certificate data."""
    severity = "low"
    message = "No SSL certificate issues found."
    return ScanResult.from_severity(category="ssl_cert", message=message, severity=severity)
