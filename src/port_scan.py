"""
Port scanning utilities.
"""

import nmap


def scan_ports(target_ip: str):
    """Scan open ports on the target IP.

    Args:
        target_ip: IP address to scan.

    Returns:
        list of open ports as integers.
    """
    # 現状は実スキャンを行わず空のリストを返す（後で実装予定）
    return []
    scanner = nmap.PortScanner()
    # `-p-` instructs nmap to scan all ports
    scan_data = scanner.scan(target_ip, arguments="-p-")

    open_ports = []
    host_info = scan_data.get("scan", {}).get(target_ip, {})
    for proto, ports in host_info.items():
        for port, info in ports.items():
            if info.get("state") == "open":
                open_ports.append(port)

    return open_ports
