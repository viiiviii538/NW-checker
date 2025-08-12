"""Static scan for rogue DHCP servers using scapy."""

from scapy.all import (  # type: ignore
    BOOTP,
    DHCP,
    Ether,
    IP,
    UDP,
    srp,
)


def scan(timeout: int = 2) -> dict:
    """Broadcast a DHCP discover and evaluate responses."""

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
    except Exception as exc:  # pragma: no cover - 環境依存のため
        warnings.append(str(exc))

    # 重複除去し、複数サーバーが存在すれば警告を追加
    unique_servers = list(dict.fromkeys(servers))
    if len(unique_servers) > 1:
        warnings.append("Multiple DHCP servers detected")

    return {
        "category": "dhcp",
        "score": len(unique_servers),
        "details": {"servers": unique_servers, "warnings": warnings},
    }

