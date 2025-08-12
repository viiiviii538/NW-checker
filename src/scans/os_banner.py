"""Static scan for OS and service banners using nmap."""

import nmap


def scan(target: str = "127.0.0.1") -> dict:
    """Attempt to grab OS and service banners from *target*.

    Returns a result dictionary containing discovered information. The score is
    the number of distinct banners plus one if the OS could be identified.
    """

    scanner = nmap.PortScanner()
    banners: dict[int, str] = {}
    os_name = ""
    error = ""
    try:
        result = scanner.scan(target, arguments="-O -sV --top-ports 10")
        host_info = result.get("scan", {}).get(target, {})

        # サービスバナー取得
        tcp_info = host_info.get("tcp", {})
        for port, data in tcp_info.items():
            banner = " ".join(
                filter(None, [data.get("name"), data.get("version")])
            ).strip()
            if banner:
                banners[int(port)] = banner

        # OS情報取得
        os_match = host_info.get("osmatch", [])
        if os_match:
            os_name = os_match[0].get("name", "")
    except Exception as exc:  # pragma: no cover - 外部コマンド失敗時は無視
        error = str(exc)

    score = len(banners) + (1 if os_name else 0)
    details = {"target": target, "os": os_name, "banners": banners}
    if error:
        details["error"] = error
    return {"category": "os_banner", "score": score, "details": details}

