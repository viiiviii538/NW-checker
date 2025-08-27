import socket
from pathlib import Path
from typing import Dict, Optional, Callable, Tuple

# DNS 逆引き結果のキャッシュ (IP -> (ホスト名, ブラックリスト判定))
_dns_cache: Dict[str, Tuple[str, bool]] = {}


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
) -> Tuple[str | None, bool | None]:
    """IP アドレスの逆引きを行いキャッシュする。

    戻り値は (ホスト名, ブラックリスト判定) のタプル。
    逆引きに失敗しキャッシュも無い場合は (None, None) を返す。
    """
    gha = gethostbyaddr or socket.gethostbyaddr
    try:
        host, _, _ = gha(ip_addr)
        host = host.rstrip(".").lower()
        blacklisted = host in DOMAIN_BLACKLIST
        _dns_cache[ip_addr] = (host, blacklisted)  # 成功時はキャッシュ
        return host, blacklisted
    except Exception:
        cached = _dns_cache.get(ip_addr)
        return cached if cached else (None, None)
