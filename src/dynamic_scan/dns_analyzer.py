import socket
from collections import OrderedDict
from pathlib import Path
from typing import Callable, Optional, Tuple

# DNS 逆引き結果のキャッシュ
_dns_cache: "OrderedDict[str, str]" = OrderedDict()
# キャッシュの上限数
_DNS_CACHE_MAX = 256


def load_blacklist(path: str | None = None) -> set[str]:
    """ブラックリストファイルを読み込み"""
    path_obj = (
        Path(path)
        if path
        else Path(__file__).resolve().parents[2] / "configs" / "domain_blacklist.txt"
    )
    try:
        with path_obj.open(encoding="utf-8") as f:
            return {
                line.strip().lower()
                for line in f
                if line.strip() and not line.startswith("#")
            }
    except FileNotFoundError:
        return set()


# 逆引きドメインのブラックリスト
DOMAIN_BLACKLIST = load_blacklist()


def reverse_dns_lookup(
    ip_addr: str,
    *,
    gethostbyaddr: Optional[Callable[[str], Tuple[str, list[str], list[str]]]] = None,
) -> str | None:
    """IP アドレスの逆引きを行いキャッシュする

    成功した結果は LRU 方式で ``_dns_cache`` に保存し、同じ IP への
    再問い合わせを避ける。
    """
    # まずキャッシュを確認
    cached = _dns_cache.get(ip_addr)
    if cached is not None:
        return cached

    gha = gethostbyaddr or socket.gethostbyaddr
    try:
        host, _, _ = gha(ip_addr)
        host = host.rstrip(".").lower()
        _dns_cache[ip_addr] = host
        _dns_cache.move_to_end(ip_addr)
        # キャッシュ上限を超えたら最も古いものを削除
        if len(_dns_cache) > _DNS_CACHE_MAX:
            _dns_cache.popitem(last=False)
        return host
    except Exception:
        return None
