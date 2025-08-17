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

    Parameters
    ----------
    target_host: str
        スキャン対象ホスト名。省略時は ``localhost`` を使用。

    Returns
    -------
    dict
        ``{category, score, details}`` 形式の辞書を返す。
        ``details`` には ``open_ports`` のリストを格納。
    """

    open_ports: List[int] = []
    error = ""
    try:
        for port in RISKY_PORTS:
            try:
                # ソケット接続を試み、成功すればポートは開いているとみなす
                with socket.create_connection((target_host, port), timeout=0.5):
                    open_ports.append(port)
            except OSError:
                # 接続失敗時はポートが閉じていると判断
                continue
    except Exception as exc:  # pragma: no cover - 想定外エラー
        error = str(exc)
        open_ports = []

    details = {"target": target_host, "open_ports": open_ports}
    if error:
        details["error"] = error

    return {
        "category": "ports",
        "score": 0 if error else len(open_ports),
        "details": details,
    }


if __name__ == "__main__":
    import json
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    print(json.dumps(scan(host), indent=2, ensure_ascii=False))
