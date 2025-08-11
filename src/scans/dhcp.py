"""Static scan for rogue DHCP servers using scapy."""

import os

from scapy.all import (  # type: ignore
    BOOTP,
    DHCP,
    Ether,
    IP,
    UDP,
    srp,
)


def scan(timeout: int = 2) -> dict:
    """Broadcast a DHCP discover and return responding servers."""

    servers: set[str] = set()
    warnings: list[str] = []
    try:
        discover = (
            Ether(dst="ff:ff:ff:ff:ff:ff")
            / IP(src="0.0.0.0", dst="255.255.255.255")
            / UDP(sport=68, dport=67)
            / BOOTP(chaddr=os.urandom(6))
            / DHCP(options=[("message-type", "discover"), "end"])
        )
        ans, _ = srp(discover, timeout=timeout, verbose=False)
        for _, pkt in ans:
            if DHCP in pkt and IP in pkt:
                servers.add(pkt[IP].src)
    except Exception:  # pragma: no cover
        pass

    servers_list = sorted(servers)
    if len(servers_list) > 1:
        warnings.append(
            "Multiple DHCP servers detected: " + ", ".join(servers_list)
        )

    return {
        "category": "dhcp",
        "score": len(servers_list),
        "details": {"servers": servers_list, "warnings": warnings},
    }

