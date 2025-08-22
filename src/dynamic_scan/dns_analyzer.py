import socket
from typing import Callable, Dict, Optional, Tuple

# DNS 逆引き結果のキャッシュ
_dns_cache: Dict[str, str] = {}


def load_blacklist(path: str = "configs/domain_blacklist.txt") -> set[str]:
    """ドメインブラックリストを読み込む"""
    try:
        with open(path, encoding="utf-8") as f:
            return {
                line.strip().lower()
                for line in f
                if line.strip() and not line.startswith("#")
            }
    except Exception:
        return set()


DOMAIN_BLACKLIST = load_blacklist()


def reverse_dns_lookup(
    ip_addr: str,
    *,
    gethostbyaddr: Optional[Callable[[str], Tuple[str, list[str], list[str]]]] = None,
) -> Optional[str]:
    """IPアドレスの逆引きを行い結果をキャッシュする"""
    gha = gethostbyaddr or socket.gethostbyaddr
    try:
        host, _, _ = gha(ip_addr)
        host = host.rstrip(".").lower()
        _dns_cache[ip_addr] = host
        return host
    except Exception:
        cached = _dns_cache.get(ip_addr)
        return cached if isinstance(cached, str) else None
