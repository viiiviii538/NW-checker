"""Static scan for ARP spoofing attempts using scapy."""

from scapy.all import sniff, ARP  # type: ignore


def scan(timeout: int = 2) -> dict:
    """Sniff ARP replies briefly and look for conflicting MAC addresses."""

    suspects = set()
    try:
        packets = sniff(filter="arp", timeout=timeout)
        seen = {}
        for pkt in packets:
            if ARP in pkt and pkt[ARP].op == 2:  # is-at
                ip = pkt[ARP].psrc
                mac = pkt[ARP].hwsrc
                if ip in seen and seen[ip] != mac:
                    suspects.add(ip)
                else:
                    seen[ip] = mac
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "arp_spoof",
        "score": len(suspects),
        "details": {"suspects": list(suspects)},
    }

