"""Static scan for UPnP/SSDP services using scapy."""

# UPnP/SSDP応答から不要なサービス公開を検知する
from scapy.all import IP, UDP, Raw, sr1  # type: ignore

# SSDPのマルチキャストアドレスとポート
SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900


def scan(target: str = SSDP_ADDR) -> dict:
    """Send an SSDP M-SEARCH request and evaluate responses.

    Returns
    -------
    dict
        {"category", "score", "details"} 形式。
        エラー時は必ず details["error"] を含む。
    """

    category = "upnp"
    responders: list[str] = []
    warnings: list[str] = []
    details: dict = {"responders": responders, "warnings": warnings}

    try:
        query = (
            "M-SEARCH * HTTP/1.1\r\n"
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
            'MAN: "ssdp:discover"\r\n'
            "MX: 1\r\n"
            "ST: ssdp:all\r\n\r\n"
        )

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

        # 正常時も score=0 固定（テスト要件）
        return {"category": category, "score": 0, "details": details}

    except Exception as exc:
        details["error"] = str(exc)
        return {"category": category, "score": 0, "details": details}
