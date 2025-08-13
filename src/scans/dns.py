"""DNS設定の静的スキャン。

現在のDNSサーバーにクエリを実行し、外部サーバーの利用や
DNSSECが無効な場合に警告を返す。"""

from ipaddress import ip_address, ip_network
from typing import List

from scapy.all import IP, UDP, DNS, DNSQR, sr1  # type: ignore

# プライベートアドレス空間
_PRIVATE_NETS = [
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
]


def _get_nameservers(path: str = "/etc/resolv.conf") -> List[str]:
    """resolv.conf から名前解決サーバー一覧を取得。"""
    servers: List[str] = []
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("nameserver"):
                    parts = line.split()
                    if len(parts) >= 2:
                        servers.append(parts[1])
    except OSError:
        pass
    return servers or ["8.8.8.8"]


def _is_private(ip: str) -> bool:
    try:
        addr = ip_address(ip)
        return addr.is_private or addr.is_loopback
    except ValueError:
        return False


def scan() -> dict:
    """DNS設定を検査し、問題があれば警告を返す。"""

    servers = _get_nameservers()
    external = [ip for ip in servers if not _is_private(ip)]

    warnings: List[str] = []
    details = {"servers": servers}

    if external:
        warnings.append("外部DNSが検出されました: " + ", ".join(external))
        details["external_servers"] = external

    dnssec_enabled: bool | None = None
    try:
        pkt = (
            IP(dst=servers[0])
            / UDP(dport=53)
            / DNS(rd=1, qd=DNSQR(qname="example.com"), ad=1)
        )
        resp = sr1(pkt, timeout=2, verbose=False)
        if resp and resp.haslayer(DNS):
            dnssec_enabled = bool(getattr(resp[DNS], "ad", 0))
    except Exception as exc:  # pragma: no cover
        details["error"] = str(exc)

    details["dnssec_enabled"] = dnssec_enabled
    if dnssec_enabled is False:
        warnings.append("DNSSECが無効です")

    details["warnings"] = warnings
    score = len(warnings)
    return {
        "category": "dns",
        "score": score,
        "details": details,
    }
