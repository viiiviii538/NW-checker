"""Static scan for SSL certificate validation."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy SSL certificate data."""
    # 実際のSSL証明書検証は未実装
    return {"category": "ssl_cert", "score": 0, "details": {"certificates": []}}
