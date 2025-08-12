"""Static scan for UPnP/SSDP services using scapy."""

from scapy.all import IP, UDP, Raw, sr1  # type: ignore

# SSDPのマルチキャストアドレスとポート
SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900


def scan(target: str = SSDP_ADDR) -> dict:
    """Send an SSDP M-SEARCH request and evaluate responses."""

    query = (
        "M-SEARCH * HTTP/1.1\r\n"
        f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 1\r\n"
        "ST: ssdp:all\r\n\r\n"
    )

    responders: list[str] = []
    warnings: list[str] = []
    try:
        pkt = IP(dst=target) / UDP(sport=SSDP_PORT, dport=SSDP_PORT) / Raw(load=query)
        ans = sr1(pkt, timeout=1, verbose=False)
        if ans:
            src = getattr(ans, "src", "")
            responders.append(src)
            payload = bytes(getattr(ans, "load", b""))
            if b"upnp" in payload.lower():
                warnings.append(f"UPnP service responded from {src}")
            else:
                warnings.append(f"Misconfigured SSDP response from {src}")
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "upnp",
        "score": len(warnings),
        "details": {"responders": responders, "warnings": warnings},
    }

