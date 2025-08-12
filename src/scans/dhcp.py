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
    """Broadcast a DHCP discover and return responding servers.

    Returns a mapping with the list of responding server IPs and warnings
    if multiple servers answer which can indicate configuration conflicts.
    """

    servers = []
    warnings = []
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
    except Exception:  # pragma: no cover - 実行環境による
        pass

    if len(servers) > 1:
        warnings.append(
            "Multiple DHCP servers detected: " + ", ".join(sorted(servers))
        )

    return {
        "category": "dhcp",
        "score": len(servers),
        "details": {"servers": servers, "warnings": warnings},
    }

