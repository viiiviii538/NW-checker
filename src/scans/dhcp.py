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

    Returns a mapping with the list of responding server IPs and warnings
    if multiple servers answer which can indicate configuration conflicts.
    """

    servers = set()
    warnings = []
    error = ""
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
                # サーバーIPは重複を除外する
                servers.add(pkt[IP].src)
    except Exception as exc:  # pragma: no cover - 実行環境による
        error = str(exc)

    server_list = sorted(servers)
    if len(server_list) > 1:
        warnings.append(
            "Multiple DHCP servers detected: " + ", ".join(server_list)
        )

    details = {"servers": server_list, "warnings": warnings}
    if error:
        details["error"] = error
    return {
        "category": "dhcp",
        "score": 0 if error else len(server_list),
        "details": details,
    }

