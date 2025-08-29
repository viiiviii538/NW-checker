"""Static scan for OS and service banners using nmap."""

# OSやサービスのバナー情報からバージョン漏洩を調べる
import nmap


def scan(target: str = "127.0.0.1") -> dict:
    """Attempt to grab OS and service banners from *target*.

    Returns a result dictionary containing discovered information.
    score = len(banners) + (1 if os_name else 0).
    """

    category = "os_banner"
    details: dict = {"target": target}

    try:
        scanner = nmap.PortScanner()
        banners: dict[int, str] = {}
        os_name = ""

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

        score = len(banners) + (1 if os_name else 0)
        details.update({"os": os_name, "banners": banners})
        return {"category": category, "score": score, "details": details}

    except Exception as exc:
        details.update({"os": "", "banners": {}, "error": str(exc)})
        return {"category": category, "score": 0, "details": details}
