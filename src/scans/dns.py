"""DNS設定の静的スキャン。

現在のDNSサーバーにクエリを実行し、外部サーバーの利用や
DNSSECが無効な場合に警告を返す。"""

# DNSサーバーの設定を検証し外部利用やDNSSEC無効を警告
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
        return any(addr in net for net in _PRIVATE_NETS)
    except ValueError:
        return False


def scan() -> dict:
    category = "dns"
    servers = _get_nameservers()

    external: List[str] = []
    invalid: List[str] = []
    details = {"servers": servers, "warnings": []}

    try:
        for ip in servers:
            if not _is_private(ip):
                external.append(ip)
    except Exception as exc:
        details["error"] = str(exc)
        return {"category": category, "score": 0, "details": details}

    if external:
        details["warnings"].append("External DNS detected: " + ", ".join(external))
        details["external_servers"] = external

    if invalid:
        details["warnings"].append("Invalid DNS server IP: " + ", ".join(invalid))
        details["invalid_servers"] = invalid

    dnssec_enabled = None
    try:
        valid = [ip for ip in servers if ip not in invalid]
        if valid:
            pkt = IP(dst=valid[0]) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com"), ad=1)
            resp = sr1(pkt, timeout=2, verbose=False)
            if resp and resp.haslayer(DNS):
                dnssec_enabled = bool(getattr(resp[DNS], "ad", 0))
    except Exception as exc:
        details["error"] = str(exc)
        return {"category": category, "score": 0, "details": details}

    details["dnssec_enabled"] = bool(dnssec_enabled)
    if dnssec_enabled is False:
        details["warnings"].append("DNSSEC is disabled")

    return {"category": category, "score": 0, "details": details}
