"""Static scan for SMB/NetBIOS services using nmap."""

import nmap


def scan(target: str = "127.0.0.1") -> dict:
    """Check for open SMB-related ports on *target*.

    Ports 137-139 and 445 are inspected. The score equals the number of open
    SMB/NetBIOS ports detected.
    """

    scanner = nmap.PortScanner()
    open_ports = []
    try:
        result = scanner.scan(target, arguments="-p 137,138,139,445 -sU -sT")
        host_info = result.get("scan", {}).get(target, {})
        for proto in ("tcp", "udp"):
            for port, data in host_info.get(proto, {}).items():
                if data.get("state") == "open":
                    open_ports.append(int(port))
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "smb_netbios",
        "score": len(open_ports),
        "details": {"target": target, "open_ports": open_ports},
    }

