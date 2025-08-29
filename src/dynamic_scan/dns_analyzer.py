import socket
import time
from typing import Callable, Dict, Optional, Tuple

# DNS 逆引き結果のキャッシュ {ip: (hostname, expire_at)}
_dns_cache: Dict[str, Tuple[str, float]] = {}


def load_blacklist(path: str = "configs/domain_blacklist.txt") -> set[str]:
    """ブラックリストファイルを読み込み"""
    try:
        with open(path, encoding="utf-8") as f:
            return {
                line.strip().lower()
                for line in f
                if line.strip() and not line.startswith("#")
            }
    except FileNotFoundError:
        return set()


# 逆引きドメインのブラックリスト
DOMAIN_BLACKLIST = load_blacklist()


def is_blacklisted(host: Optional[str]) -> bool:
    """ドメインがブラックリストに含まれるか判定"""
    if not host:
        return False
    return host.lower() in DOMAIN_BLACKLIST


def reverse_dns_lookup(
    ip_addr: str,
    *,
    resolver: Optional[Callable[[str], Tuple[str, list[str], list[str]]]] = None,
    cache_ttl: int = 3600,
) -> str | None:
    """IP アドレスの逆引きを行いキャッシュする"""

    now = time.time()
    cached = _dns_cache.get(ip_addr)
    if cached:
        host, expires_at = cached
        if expires_at > now:
            return host
        del _dns_cache[ip_addr]

    resolver = resolver or socket.gethostbyaddr
    try:
        host, _, _ = resolver(ip_addr)
        host = host.rstrip(".").lower()
        _dns_cache[ip_addr] = (host, now + cache_ttl)  # 成功時はキャッシュ
        return host
    except Exception:
        return None
