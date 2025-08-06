"""Static scan for open ports."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy port scan data."""
    # 実際のポートスキャンは未実装
    return {"category": "ports", "score": 0, "details": {"open_ports": []}}
