"""Detect rogue DHCP servers."""

from scapy.all import DHCP, sniff  # type: ignore


def scan(interface: str | None = None) -> dict:
    """Look for multiple DHCP offers."""
    try:
        _ = (DHCP, sniff)  # Placeholder
        details = {"servers": []}
        return {"category": "dhcp", "score": 0, "details": details}
    except Exception as exc:
        return {"category": "dhcp", "score": 0, "details": {"error": str(exc)}}
