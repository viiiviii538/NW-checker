"""DNS resolution checks."""

from scapy.all import sr1, IP, UDP, DNS, DNSQR  # type: ignore


def scan(name: str, server: str = "8.8.8.8") -> dict:
    """Query DNS server for a record."""
    try:
        _ = (sr1, IP, UDP, DNS, DNSQR)  # Placeholder
        details = {"query": name, "answers": []}
        return {"category": "dns", "score": 0, "details": details}
    except Exception as exc:
        return {"category": "dns", "score": 0, "details": {"error": str(exc)}}
