"""Static scan for DNS records."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy DNS data."""
    # 実際のDNS解析は未実装
    return {"category": "dns", "score": 0, "details": {"records": []}}
