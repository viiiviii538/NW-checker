"""Static scan for SMB/NetBIOS hosts."""

from ..models import ScanResult


def scan() -> ScanResult:
    """Return dummy SMB/NetBIOS data."""
    severity = "low"
    message = "No SMB/NetBIOS hosts found."
    return ScanResult.from_severity(category="smb_netbios", message=message, severity=severity)
