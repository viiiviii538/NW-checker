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
    """Check *target_host* for open ports considered risky.

    Returns
    -------
    dict
        {"category", "score", "details"} 形式。
        エラー時は score=0 で details に "error" を含む。
    """

    category = "ports"
    open_ports: List[int] = []
    details: Dict[str, object] = {"target": target_host}

    try:
        for port in RISKY_PORTS:
            try:
                with socket.create_connection((target_host, port), timeout=0.5):
                    open_ports.append(port)
            except OSError:
                continue

        details["open_ports"] = open_ports
        return {"category": category, "score": 0, "details": details}

    except Exception as exc:
        details["open_ports"] = []
        details["error"] = str(exc)
        return {"category": category, "score": 0, "details": details}



if __name__ == "__main__":
    import json
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    print(json.dumps(scan(host), indent=2, ensure_ascii=False))
