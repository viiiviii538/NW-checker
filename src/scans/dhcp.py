"""Static scan for DHCP configuration."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy DHCP data."""
    # 実際のDHCP解析は未実装
    return {"category": "dhcp", "score": 0, "details": {"servers": []}}
