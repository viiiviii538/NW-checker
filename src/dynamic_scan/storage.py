import json
import asyncio
import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class Storage:
    """解析結果を JSON 形式で保持するストレージ層"""

    def __init__(self, file_path: str = "dynamic_scan_results.json") -> None:
        self.path = Path(file_path)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")
        self._lock = asyncio.Lock()
        self._listeners: List[asyncio.Queue] = []

    def add_listener(self, queue: asyncio.Queue) -> None:
        """結果更新時に通知を受け取るキューを追加"""
        self._listeners.append(queue)

    def remove_listener(self, queue: asyncio.Queue) -> None:
        """通知キューを削除"""
        if queue in self._listeners:
            self._listeners.remove(queue)

    async def save(self, data: Dict[str, Any]) -> None:
        async with self._lock:
            current: List[Dict[str, Any]] = json.loads(self.path.read_text(encoding="utf-8"))
            current.append(data)
            self.path.write_text(json.dumps(current), encoding="utf-8")
        for q in list(self._listeners):
            q.put_nowait(data)

    def get_all(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))


# --- Persistent history storage using SQLite ---

# データベースファイルのパス。テスト時は環境変数で差し替え可能。
DB_FILE = Path(os.getenv("DYNAMIC_SCAN_DB", "dynamic_scan_history.db"))


def _init_db() -> None:
    """SQLite データベースを初期化する。"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                data TEXT
            )
            """
        )
        conn.commit()


_init_db()


def save_result(result: Dict[str, Any]) -> None:
    """解析結果を永続化する。"""
    ts = result.get("timestamp")
    if isinstance(ts, (int, float)):
        ts = datetime.fromtimestamp(ts).isoformat()
    elif ts is None:
        ts = datetime.utcnow().isoformat()
    result["timestamp"] = ts
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO results (timestamp, data) VALUES (?, ?)",
            (ts, json.dumps(result)),
        )
        conn.commit()


def fetch_results(start: str, end: str) -> List[Dict[str, Any]]:
    """指定期間の結果を取得する。"""
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(
            "SELECT data FROM results WHERE date(timestamp) BETWEEN date(?) AND date(?) ORDER BY timestamp",
            (start, end),
        ).fetchall()
    return [json.loads(r[0]) for r in rows]
