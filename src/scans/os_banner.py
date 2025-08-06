"""Static scan for OS banner detection."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy OS banner data."""
    severity = "low"
    message = "No OS banners captured."
    return ScanResult.from_severity(category="os_banner", message=message, severity=severity)
