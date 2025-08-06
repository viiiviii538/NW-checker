"""Port scan analysis returning unified result."""

import nmap


def scan(target: str) -> dict:
    """Scan open ports on a target host.

    Args:
        target: IP or hostname to scan.

    Returns:
        dict: {"category": "ports", "score": int, "details": {"open_ports": list}}
    """
    scanner = nmap.PortScanner()
    try:
        scan_data = scanner.scan(target, arguments="-F")
        open_ports: list[int] = []
        host_info = scan_data.get("scan", {}).get(target, {})
        for proto, ports in host_info.items():
            if proto not in {"tcp", "udp"}:
                continue
            for port, info in ports.items():
                if info.get("state") == "open":
                    open_ports.append(port)
        score = -len(open_ports)
        return {"category": "ports", "score": score, "details": {"open_ports": open_ports}}
    except Exception as exc:  # スキャン失敗時
        return {"category": "ports", "score": 0, "details": {"error": str(exc)}}
