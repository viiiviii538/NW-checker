"""Static scan for OS and service banners using nmap."""

import nmap


def scan(target: str = "127.0.0.1") -> dict:
    """Attempt to grab service banners and detect OS from *target*.

    Returns a result dictionary containing discovered banners and the detected
    OS name (if any). The score is the number of distinct banners plus one when
    the OS is identified.
    """

    scanner = nmap.PortScanner()
    banners: dict[int, str] = {}
    os_name = ""
    try:
        # OS判別(-O)とサービスバナー取得(-sV)
        result = scanner.scan(target, arguments="-O -sV --top-ports 10")
        host_info = result.get("scan", {}).get(target, {})

        tcp_info = host_info.get("tcp", {})
        for port, data in tcp_info.items():
            banner = " ".join(
                filter(None, [data.get("name"), data.get("version")])
            ).strip()
            if banner:
                banners[int(port)] = banner

        matches = host_info.get("osmatch", [])
        if matches:
            os_name = matches[0].get("name", "")
    except Exception:  # pragma: no cover
        pass

    score = len(banners) + (1 if os_name else 0)
    return {
        "category": "os_banner",
        "score": score,
        "details": {"target": target, "banners": banners, "os": os_name},
    }

