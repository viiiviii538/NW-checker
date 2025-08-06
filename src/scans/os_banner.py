"""Static scan for OS banners."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy OS banner data."""
    # 実際のOS判別は未実装
    return {"category": "os_banner", "score": 0, "details": {"banners": []}}
