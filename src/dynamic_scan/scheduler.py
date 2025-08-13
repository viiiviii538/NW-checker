from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Iterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import capture, analyze, storage


class DynamicScanScheduler:
    """APScheduler を用いて定期的なダイナミックスキャンを管理するクラス"""

    def __init__(self) -> None:
        self.scheduler: AsyncIOScheduler | None = None
        self.job = None
        self.capture_task: asyncio.Task | None = None
        self.analyse_task: asyncio.Task | None = None
        self.storage: storage.Storage = storage.Storage()

    async def _run_scan(self, interface: str | None, duration: int | None, approved_macs: Iterable[str] | None) -> None:
        """実際に 1 回のスキャンを実行する内部メソッド"""
        queue: asyncio.Queue = asyncio.Queue()
        self.capture_task = asyncio.create_task(
            capture.capture_packets(queue, interface=interface, duration=duration)
        )
        self.analyse_task = asyncio.create_task(
            analyze.analyse_packets(queue, self.storage, approved_macs=approved_macs or [])
        )
        try:
            await asyncio.gather(self.capture_task, self.analyse_task)
        finally:
            self.capture_task = None
            self.analyse_task = None

    def start(
        self,
        *,
        interface: str | None = None,
        duration: int | None = None,
        approved_macs: Iterable[str] | None = None,
        interval: int = 3600,
    ) -> None:
        """スケジューラを開始し、定期スキャンを設定する"""
        # ストレージを新たに生成（テスト時は monkeypatch で差し替え可能）
        self.storage = storage.Storage()
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()
            self.scheduler.start()
        if self.job:
            self.job.remove()
        # APScheduler でコルーチンを定期実行
        self.job = self.scheduler.add_job(
            self._run_scan,
            "interval",
            seconds=interval,
            args=[interface, duration, approved_macs],
            max_instances=1,
        )

    async def stop(self) -> None:
        """スケジュールされたジョブと進行中のタスクを停止"""
        if self.job:
            self.job.remove()
            self.job = None
        for task in (self.capture_task, self.analyse_task):
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
        self.capture_task = self.analyse_task = None
        if self.scheduler and self.scheduler.running:
            try:
                self.scheduler.shutdown(wait=False)
            except RuntimeError:
                # イベントループが既に閉じている場合は無視
                pass
            self.scheduler = None
