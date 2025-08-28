"""Protocol detection utilities for dynamic scanning.

危険ポートの判定を行うモジュール。
"""
from typing import Optional

# 危険とされるポート番号集合
DANGEROUS_PORTS: set[int] = {21, 23, 3389, 445}


def is_dangerous_protocol(src_port: Optional[int], dst_port: Optional[int]) -> bool:
    """判断: 指定ポートが危険ポートか?"""
    return any(
        port in DANGEROUS_PORTS for port in (src_port, dst_port) if port is not None
    )


def analyze_packet(packet) -> bool:
    """パケット内のポートを解析し危険プロトコルか判定する"""
    src = getattr(packet, "src_port", getattr(packet, "sport", None))
    dst = getattr(packet, "dst_port", getattr(packet, "dport", None))
    return is_dangerous_protocol(src, dst)
