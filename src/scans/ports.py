"""Static scan for risky open ports using basic socket checks."""

from __future__ import annotations

import socket
from typing import Dict, List, Tuple

# 一般的に危険とされるポート番号のリスト
RISKY_PORTS: Tuple[int, ...] = (
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    139,
    143,
    443,
    445,
    3389,
)


def scan(target_host: str = "127.0.0.1") -> Dict[str, object]:
    """Check common risky ports on *target_host*.

    Returns
    -------
    dict
        結果は ``{category, score, details}`` の形式で返す。
    """

    open_ports: List[int] = []
    for port in RISKY_PORTS:
        try:
            # ソケット接続を試み、成功すればポートは開いているとみなす
            with socket.create_connection((target_host, port), timeout=0.5):
                open_ports.append(port)
        except OSError:
            continue

    return {
        "category": "ports",
        "score": len(open_ports),
        "details": {"target": target_host, "open_ports": open_ports},
    }


if __name__ == "__main__":
    import json
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    print(json.dumps(scan(host), indent=2, ensure_ascii=False))
