import json
import asyncio
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class Storage:
    """解析結果を SQLite で保持するストレージ層"""

    def __init__(
        self, db_path: str = "dynamic_scan_results.db", *, max_recent: int = 100
    ) -> None:
        """ストレージを初期化

        Args:
            db_path: SQLite のファイルパス
            max_recent: メモリ上に保持する最新結果の上限件数
        """
        self.db_path = Path(db_path)
        self._lock = asyncio.Lock()
        self._listeners: List[asyncio.Queue] = []
        self._recent_limit = max_recent
        self._recent: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self) -> None:
        """SQLite テーブルを初期化"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dns_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    hostname TEXT NOT NULL,
                    blacklisted INTEGER NOT NULL
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

    async def save_dns_history(self, ip: str, hostname: str, blacklisted: bool) -> None:
        """逆引き結果を DNS 履歴として保存"""
        record = (
            datetime.now().astimezone().isoformat(timespec="seconds"),
            ip,
            hostname,
            int(blacklisted),
        )
        async with self._lock:
            await asyncio.to_thread(self._insert_dns_history, record)

    # 上部の import はそのまま

    # save_result: UTC→ローカルに変更
    async def save_result(self, data: Dict[str, Any]) -> None:
        # ローカルタイムゾーンのISO（+09:00付き）
        record = {
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            **data,
        }

        async with self._lock:
            await asyncio.to_thread(self._insert_record, record)
            self._recent.append(record)
            if len(self._recent) > self._recent_limit:
                self._recent.pop(0)
        for q in list(self._listeners):
            q.put_nowait(record)

    # fetch_results: 全角スペース除去＆日付文字列比較
    def fetch_results(self, start_date: str, end_date: str):
        """start～end を両端含む（日単位・'YYYY-MM-DD'）。"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute(
                """
                SELECT data
                FROM results
                WHERE substr(timestamp, 1, 10) >= ?
                  AND substr(timestamp, 1, 10) <= ?
                ORDER BY rowid ASC
                """,
                (start_date, end_date),
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def _insert_record(self, record: Dict[str, Any]) -> None:
        """SQLite に 1 件のレコードを書き込む"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO results (timestamp, data) VALUES (?, ?)",
                (record["timestamp"], json.dumps(record)),
            )
            conn.commit()

    def _insert_dns_history(self, record: tuple[str, str, str, int]) -> None:
        """DNS 履歴を 1 件書き込む"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                "INSERT INTO dns_history (timestamp, ip, hostname, blacklisted) VALUES (?, ?, ?, ?)",
                record,
            )
            conn.commit()

    def get_all(self) -> List[Dict[str, Any]]:
        """現在のスキャンセッションの結果を取得"""
        return list(self._recent)

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
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute(query, params).fetchall()
        return [json.loads(r[0]) for r in rows]

    def fetch_dns_history(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """DNS 履歴を期間指定で取得"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute(
                """
                SELECT timestamp, ip, hostname, blacklisted
                FROM dns_history
                WHERE substr(timestamp, 1, 10) >= ?
                  AND substr(timestamp, 1, 10) <= ?
                ORDER BY rowid ASC
                """,
                (start_date, end_date),
            ).fetchall()
        return [
            {
                "timestamp": ts,
                "ip": ip,
                "hostname": host,
                "blacklisted": bool(bl),
            }
            for ts, ip, host, bl in rows
        ]
