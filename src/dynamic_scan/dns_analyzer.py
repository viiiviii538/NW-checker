import socket
from typing import Callable, Optional, Tuple, Dict

# DNS 逆引き結果のキャッシュ
_dns_cache: Dict[str, str | None] = {}


def reverse_dns_lookup(
    ip_addr: str,
    *,
    gethostbyaddr: Optional[Callable[[str], Tuple[str, list[str], list[str]]]] = None,
) -> Optional[str]:
    """与えられたIPの逆引きを行い、結果をキャッシュする"""
    if ip_addr in _dns_cache:
        return _dns_cache[ip_addr]
    resolver = gethostbyaddr or socket.gethostbyaddr
    try:
        host, _, _ = resolver(ip_addr)
        host = host.rstrip('.').lower()
        _dns_cache[ip_addr] = host
        return host
    except Exception:
        _dns_cache[ip_addr] = None
        return None


def load_blacklist(path: str = "configs/domain_blacklist.txt") -> set[str]:
    """ドメインブラックリストを読み込む"""
    try:
        with open(path, encoding="utf-8") as f:
            return {
                line.strip().lower()
                for line in f
                if line.strip() and not line.startswith('#')
            }
    except OSError:
        return set()


DOMAIN_BLACKLIST = load_blacklist()


def is_blacklisted(hostname: Optional[str]) -> bool:
    """ホスト名がブラックリストに含まれるか判定"""
    if not hostname:
        return False
    return hostname.lower() in DOMAIN_BLACKLIST
