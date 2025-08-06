"""Static scan for SMB/NetBIOS information."""

from typing import Dict, Any


def scan() -> Dict[str, Any]:
    """Return dummy SMB/NetBIOS data."""
    # 実際のSMB/NetBIOS検出は未実装
    return {"category": "smb_netbios", "score": 0, "details": {"hosts": []}}
