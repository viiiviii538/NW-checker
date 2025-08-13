import json
import asyncio
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class Storage:
    """解析結果を SQLite で保持するストレージ層"""

    def __init__(self, db_path: str = "dynamic_scan_results.db") -> None:
        self.db_path = Path(db_path)
        self._lock = asyncio.Lock()
        self._listeners: List[asyncio.Queue] = []
        self._recent: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self) -> None:
        """SQLite テーブルを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_listener(self, queue: asyncio.Queue) -> None:
        """結果更新時に通知を受け取るキューを追加"""
        self._listeners.append(queue)

    def remove_listener(self, queue: asyncio.Queue) -> None:
        """通知キューを削除"""
        if queue in self._listeners:
            self._listeners.remove(queue)

    async def save_result(self, data: Dict[str, Any]) -> None:
        """結果を保存し、リスナーへ通知"""
        # タイムゾーン付きISO形式でタイムスタンプを付与
        record = {"timestamp": datetime.now(timezone.utc).isoformat(), **data}

        async with self._lock:
            await asyncio.to_thread(self._insert_record, record)
            self._recent.append(record)
        for q in list(self._listeners):
            q.put_nowait(record)

    def _insert_record(self, record: Dict[str, Any]) -> None:
        """SQLite に 1 件のレコードを書き込む"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO results (timestamp, data) VALUES (?, ?)",
                (record["timestamp"], json.dumps(record)),
            )
            conn.commit()

    def get_all(self) -> List[Dict[str, Any]]:
        """現在のスキャンセッションの結果を取得"""
        return list(self._recent)

    def fetch_results(self, start: str, end: str) -> List[Dict[str, Any]]:
        """指定期間の結果を取得"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT data FROM results WHERE date(timestamp) BETWEEN ? AND ? ORDER BY timestamp",
                (start, end),
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def fetch_history(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """保存された結果を期間・条件で検索する"""
        query = "SELECT data FROM results WHERE 1=1"
        params: List[Any] = []

        start = filters.get("start")
        if start:
            query += " AND timestamp >= ?"
            params.append(start)

        end = filters.get("end")
        if end:
            query += " AND timestamp <= ?"
            params.append(end)

        device = filters.get("device")
        if device:
            query += " AND json_extract(data, '$.src_ip') = ?"
            params.append(device)

        protocol = filters.get("protocol")
        if protocol:
            query += " AND json_extract(data, '$.protocol') = ?"
            params.append(protocol)

        query += " ORDER BY timestamp"
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
        return [json.loads(r[0]) for r in rows]
