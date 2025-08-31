from contextlib import closing
import asyncio
import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import List, Set

# 設定ファイルとデータベースのパス
CONFIG_PATH = Path("configs/approved_devices.json")
DB_PATH = Path("dynamic_scan_results.db")

# 既知デバイス集合と WebSocket リスナー
# Set of approved/seen device MAC addresses. Populated on module import.
_known_devices: Set[str] = set()
_listeners: List[asyncio.Queue] = []


def _load_approved_devices() -> None:
    """approved_devices.json を読み込んで既知デバイス集合を初期化"""
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                _known_devices.update({m.lower() for m in data})
    except Exception:
        # ファイルが存在しない場合は空集合のまま
        pass


_load_approved_devices()


def add_listener(queue: asyncio.Queue) -> None:
    """アラート送信用のキューを登録"""
    _listeners.append(queue)


def remove_listener(queue: asyncio.Queue) -> None:
    """登録済みのキューを削除"""
    if queue in _listeners:
        _listeners.remove(queue)


def track_device(mac_addr: str) -> bool:
    """デバイスの MAC アドレスを追跡し、新規なら DB と WebSocket に通知.

    Returns True if the address was newly registered, otherwise False.
    """
    mac = mac_addr.lower()
    if not mac or mac in _known_devices:
        return False
    _known_devices.add(mac)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                mac TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO devices (mac, first_seen) VALUES (?, ?)",
            (mac, timestamp),
        )
        conn.commit()
    for q in list(_listeners):
        q.put_nowait({"mac": mac, "first_seen": timestamp})
    return True
