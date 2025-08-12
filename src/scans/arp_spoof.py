"""Active ARP spoofing test using scapy."""

from __future__ import annotations

import re
import subprocess
import time
from typing import Dict

from scapy.all import ARP, send  # type: ignore


# デフォルトで注入するダミーのIPとMAC
FAKE_IP = "1.2.3.4"
FAKE_MAC = "de:ad:be:ef:00:01"


def _get_arp_table() -> Dict[str, str]:
    """Parse system ARP table into an ``ip -> mac`` mapping."""

    try:
        output = subprocess.check_output(["arp", "-an"], text=True)
    except Exception:  # pragma: no cover - OSに依存するため
        return {}

    table: Dict[str, str] = {}
    for line in output.splitlines():
        m = re.search(r"\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-f:]{17})", line, re.I)
        if m:
            table[m.group(1)] = m.group(2)
    return table


def scan(
    wait: float = 1.0,
    fake_ip: str = FAKE_IP,
    fake_mac: str = FAKE_MAC,
) -> dict:
    """Inject a spoofed ARP reply and watch for table changes.

    Parameters
    ----------
    wait:
        Packet送信後に待機する秒数。
    fake_ip:
        ARPテーブルに注入するIPアドレス。
    fake_mac:
        ``fake_ip`` に紐付ける偽のMACアドレス。
    """

    before = _get_arp_table()

    try:
        pkt = ARP(
            op=2,  # is-at
            psrc=fake_ip,
            hwsrc=fake_mac,
            pdst=fake_ip,
            hwdst="ff:ff:ff:ff:ff:ff",
        )
        send(pkt, verbose=False)
        time.sleep(wait)
    except Exception as exc:  # pragma: no cover - 実行環境による
        return {
            "category": "arp_spoof",
            "score": 0,
            "details": {"error": str(exc)},
        }

    after = _get_arp_table()
    changed = before.get(fake_ip) != fake_mac and after.get(fake_ip) == fake_mac
    explanation = (
        "ARP table updated with spoofed entry"
        if changed
        else "No ARP poisoning detected"
    )

    return {
        "category": "arp_spoof",
        "score": 5 if changed else 0,
        "details": {"vulnerable": changed, "explanation": explanation},
    }

