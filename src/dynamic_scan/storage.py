import json
import asyncio
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
