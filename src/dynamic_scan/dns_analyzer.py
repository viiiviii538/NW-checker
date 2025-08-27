import socket
from pathlib import Path
from typing import Dict, Optional, Callable, Tuple

# DNS 逆引き結果のキャッシュ
_dns_cache: Dict[str, str] = {}


def load_blacklist(path: str = "configs/domain_blacklist.txt") -> set[str]:
    """ブラックリストファイルを読み込み"""
    with open(path, encoding="utf-8") as f:
        return {
            line.strip().lower()
            for line in f
            if line.strip() and not line.startswith("#")
        }


# 逆引きドメインのブラックリスト
DOMAIN_BLACKLIST = load_blacklist()


def reverse_dns_lookup(
    ip_addr: str,
    *,
    gethostbyaddr: Optional[Callable[[str], Tuple[str, list[str], list[str]]]] = None,
) -> str | None:
    """IP アドレスの逆引きを行いキャッシュする"""

    # 既に逆引き済みならキャッシュを返す
    cached = _dns_cache.get(ip_addr)
    if isinstance(cached, str):
        return cached

    gha = gethostbyaddr or socket.gethostbyaddr
    try:
        host, _, _ = gha(ip_addr)
        host = host.rstrip(".").lower()
        _dns_cache[ip_addr] = host  # 成功時はキャッシュ
        return host
    except Exception:
        return None
