import json
import asyncio
import sqlite3
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

    async def save(self, data: Dict[str, Any]) -> None:
        async with self._lock:
            current: List[Dict[str, Any]] = json.loads(self.path.read_text(encoding="utf-8"))
            current.append(data)
            self.path.write_text(json.dumps(current), encoding="utf-8")

    def get_all(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))


# --- 永続化ストレージ（SQLite） ---

DB_PATH = Path("dynamic_scan_history.db")


def _init_db() -> None:
    """必要なテーブルを作成する。"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS results (timestamp TEXT, data TEXT)"
        )
        conn.commit()


_init_db()


async def save_result(result: Dict[str, Any]) -> None:
    """結果をSQLiteに保存する。"""

    def _insert(data: Dict[str, Any]) -> None:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO results (timestamp, data) VALUES (?, ?)",
                (data["timestamp"], json.dumps(data)),
            )
            conn.commit()

    data = dict(result)
    data.setdefault("timestamp", datetime.utcnow().isoformat())
    await asyncio.to_thread(_insert, data)


def fetch_results(start: str, end: str) -> List[Dict[str, Any]]:
    """指定期間の結果を取得する。日付は YYYY-MM-DD 形式。"""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT data FROM results WHERE date(timestamp) BETWEEN ? AND ? ORDER BY timestamp",
            (start, end),
        )
        rows = cur.fetchall()
    return [json.loads(row[0]) for row in rows]

