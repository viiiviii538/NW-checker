"""Static scan for risky open ports using basic socket checks."""

# 危険なポートが開放されていないか確認する簡易チェック
from __future__ import annotations

import socket
from typing import Dict, List, Tuple

# 一般的に危険とされるポート番号のリスト
# 日本語コメントでポートの用途を説明
RISKY_PORTS: Tuple[int, ...] = (
    21,  # FTP
    22,  # SSH
    23,  # Telnet
    25,  # SMTP
    53,  # DNS
    80,  # HTTP
    110,  # POP3
    139,  # NetBIOS
    143,  # IMAP
    443,  # HTTPS
    445,  # SMB
    3389,  # RDP
)


def scan(target_host: str = "127.0.0.1") -> Dict[str, object]:
    """Check *target_host* for open ports considered risky."""
    category = "ports"
    open_ports: List[int] = []
    details: Dict[str, object] = {"target": target_host}

    last_exc: Exception | None = None
    tried = 0

    try:
        for port in RISKY_PORTS:
            tried += 1
            try:
                with socket.create_connection((target_host, port), timeout=0.5):
                    open_ports.append(port)
            except OSError as e:
                # 接続失敗（閉じてる等）は無視するが、最後の例外は覚えておく
                last_exc = e
                continue

        details["open_ports"] = open_ports

        # 全部失敗（1つも接続成功なし）なら error を付ける
        if not open_ports and last_exc is not None and tried > 0:
            details["error"] = str(last_exc)

        # スコアは開いてたポート数
        return {"category": category, "score": len(open_ports), "details": details}

    except Exception as e:
        # 想定外の例外は error を付けて score=0
        details.update({"open_ports": [], "error": str(e)})
        return {"category": category, "score": 0, "details": details}
