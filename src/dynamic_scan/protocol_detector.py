"""Protocol detection utilities for dynamic scanning.

危険ポートの判定を行うモジュール。
"""

from typing import Optional

# 危険とされるポート番号集合
# FTP(21), Telnet(23), RDP(3389), SMB(445) などの典型的な脆弱サービス
# VNC や WinRM(5985/5986) などの管理用プロトコルも監視対象とする
DANGEROUS_PORTS: set[int] = {
    21,  # FTP
    23,  # Telnet
    3389,  # RDP
    445,  # SMB
    5900,  # VNC
    5901,  # VNC alt
    5985,  # WinRM HTTP
    5986,  # WinRM HTTPS
    2323,  # Telnet alternate
}


def is_dangerous_protocol(src_port: Optional[int], dst_port: Optional[int]) -> bool:
    """判断: 指定ポートが危険ポートか?"""
    return any(
        port in DANGEROUS_PORTS for port in (src_port, dst_port) if port is not None
    )


def analyze_packet(pkt) -> bool:
    """パケット内のポートを解析し危険プロトコルか判定する"""
    src_port = getattr(pkt, "src_port", getattr(pkt, "sport", None))
    dst_port = getattr(pkt, "dst_port", getattr(pkt, "dport", None))
    return is_dangerous_protocol(src_port, dst_port)
