"""Detect ARP spoofing attempts."""

from scapy.all import sniff, ARP  # type: ignore


def scan(interface: str | None = None) -> dict:
    """Listen for suspicious ARP replies."""
    try:
        _ = (sniff, ARP)  # 実装は後日
        details = {"alerts": []}
        return {"category": "arp_spoof", "score": 0, "details": details}
    except Exception as exc:
        return {"category": "arp_spoof", "score": 0, "details": {"error": str(exc)}}
