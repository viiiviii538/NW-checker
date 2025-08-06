"""OS banner grabbing using nmap."""

import nmap


def scan(target: str) -> dict:
    """Attempt to detect OS information for the target.

    Args:
        target: Host to fingerprint.

    Returns:
        dict: {"category": "os_banner", "score": int, "details": {"os": str}}
    """
    scanner = nmap.PortScanner()
    try:
        result = scanner.scan(target, arguments="-O")
        os_matches = result.get("scan", {}).get(target, {}).get("osmatch", [])
        os_name = os_matches[0]["name"] if os_matches else "unknown"
        score = 0 if os_matches else -10
        return {"category": "os_banner", "score": score, "details": {"os": os_name}}
    except Exception as exc:
        return {"category": "os_banner", "score": 0, "details": {"error": str(exc)}}
