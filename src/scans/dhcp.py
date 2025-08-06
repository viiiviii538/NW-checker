"""Static scan for rogue DHCP servers using scapy."""

from scapy.all import (  # type: ignore
    Ether,
    IP,
    UDP,
    BOOTP,
    DHCP,
    srp,
)


def scan(timeout: int = 2) -> dict:
    """Broadcast a DHCP discover and return responding servers."""

    servers = []
    try:
        discover = (
            Ether(dst="ff:ff:ff:ff:ff:ff")
            / IP(src="0.0.0.0", dst="255.255.255.255")
            / UDP(sport=68, dport=67)
            / BOOTP(chaddr=b"\x00" * 6)
            / DHCP(options=[("message-type", "discover"), "end"])
        )
        ans, _ = srp(discover, timeout=timeout, verbose=False)
        for _, pkt in ans:
            if DHCP in pkt:
                servers.append(pkt[IP].src)
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "dhcp",
        "score": len(servers),
        "details": {"servers": servers},
    }

