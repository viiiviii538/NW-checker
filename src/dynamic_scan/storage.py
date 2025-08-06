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

    async def save(self, data: Dict[str, Any]) -> None:
        async with self._lock:
            current: List[Dict[str, Any]] = json.loads(self.path.read_text(encoding="utf-8"))
            current.append(data)
            self.path.write_text(json.dumps(current), encoding="utf-8")

    def get_all(self) -> List[Dict[str, Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))
