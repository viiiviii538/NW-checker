"""Static scan for open ports using nmap."""

import nmap


def scan(target: str = "127.0.0.1") -> dict:
    """Scan top ports on *target* and return a unified result dict.

    The scan is best-effort; if ``nmap`` is unavailable or fails, the
    function falls back to reporting no open ports.
    """

    scanner = nmap.PortScanner()
    open_ports = []
    try:
        result = scanner.scan(target, arguments="-T4 --top-ports 10")
        tcp_info = result.get("scan", {}).get(target, {}).get("tcp", {})
        open_ports = [int(p) for p, data in tcp_info.items() if data.get("state") == "open"]
    except Exception:  # pragma: no cover - nmap failures are non-fatal
        pass

    return {
        "category": "ports",
        "score": len(open_ports),
        "details": {"target": target, "open_ports": open_ports},
    }

