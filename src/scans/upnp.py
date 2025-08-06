"""UPnP discovery using SSDP."""

from scapy.all import IP, UDP, Raw, sr1  # type: ignore


def scan(target: str = "239.255.255.250") -> dict:
    """Discover UPnP devices via SSDP broadcast."""
    try:
        _ = (IP, UDP, Raw, sr1)  # 実際の処理は未実装
        details = {"devices": []}
        return {"category": "upnp", "score": 0, "details": details}
    except Exception as exc:
        return {"category": "upnp", "score": 0, "details": {"error": str(exc)}}
