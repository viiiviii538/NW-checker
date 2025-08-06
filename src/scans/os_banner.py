"""Static scan for service banners using nmap."""

import nmap


def scan(target: str = "127.0.0.1") -> dict:
    """Attempt to grab service banners from *target*.

    Returns a result dictionary containing discovered banners. The score is the
    number of distinct banners captured.
    """

    scanner = nmap.PortScanner()
    banners: dict[int, str] = {}
    try:
        result = scanner.scan(target, arguments="-sV --top-ports 10")
        tcp_info = result.get("scan", {}).get(target, {}).get("tcp", {})
        for port, data in tcp_info.items():
            banner = " ".join(filter(None, [data.get("name"), data.get("version")])).strip()
            if banner:
                banners[int(port)] = banner
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "os_banner",
        "score": len(banners),
        "details": {"target": target, "banners": banners},
    }

