"""Static scan for UPnP/SSDP services using scapy."""

from scapy.all import IP, UDP, Raw, sr1  # type: ignore


def scan(target: str = "239.255.255.250") -> dict:
    """Send an SSDP M-SEARCH and record any response.

    The function gracefully handles environments where raw sockets are not
    permitted by returning an empty result.
    """

    query = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 1\r\n"
        "ST: ssdp:all\r\n\r\n"
    )
    responders = []
    try:
        pkt = IP(dst=target) / UDP(sport=1900, dport=1900) / Raw(load=query)
        ans = sr1(pkt, timeout=1, verbose=False)
        if ans:
            responders.append(ans.src)
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "upnp",
        "score": len(responders),
        "details": {"responders": responders},
    }

