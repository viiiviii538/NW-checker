"""Static scan for UPnP services."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy UPnP data."""
    # 実際のUPnP検出は未実装
    return {"category": "upnp", "score": 0, "details": {"services": []}}
