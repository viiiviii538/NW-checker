"""Static scan for rogue DHCP servers using scapy.

This scan broadcasts a DHCP *discover* packet and counts how many
servers answer. The IP address of each responding server is recorded and
a warning is emitted when multiple servers respond, which may indicate a
configuration conflict in the network.
"""

# 不正DHCPサーバーの有無を調べる
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

    Returns
    -------
    dict
        {"category", "score", "details"} 形式。
        エラー時は必ず details["error"] を含む。
    """

    category = "dhcp"
    details: dict = {"servers": [], "warnings": []}

    try:
        servers = set()
        warnings = []

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
                servers.add(pkt[IP].src)

        server_list = sorted(servers)
        if len(server_list) > 1:
            warnings.append("Multiple DHCP servers detected: " + ", ".join(server_list))

        details.update({"servers": server_list, "warnings": warnings})
        return {"category": category, "score": 0, "details": details}

    except Exception as exc:
        details["error"] = str(exc)
        return {"category": category, "score": 0, "details": details}
