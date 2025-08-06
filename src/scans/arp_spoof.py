"""Static scan for ARP spoofing detection."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy ARP spoofing data."""
    # 実際のARPスプーフィング検出は未実装
    return {"category": "arp_spoof", "score": 0, "details": {"alerts": []}}
