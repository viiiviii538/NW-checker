from __future__ import annotations

import asyncio
import json
import os
from contextlib import suppress
from pathlib import Path
from typing import Iterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import blacklist_updater, capture, analyze, storage


CONFIG_PATH = Path(__file__).with_name("config.json")


def load_blacklist_config(path: Path | None = None) -> tuple[str | None, int]:
    """環境変数または設定ファイルからブラックリスト更新設定を読み込む"""
    path = path or CONFIG_PATH
    feed_url = os.getenv("BLACKLIST_FEED_URL")
    interval_env = os.getenv("BLACKLIST_UPDATE_INTERVAL_HOURS")
    try:
        interval_hours = int(interval_env) if interval_env is not None else None
    except ValueError:
        interval_hours = None
    if not feed_url or interval_hours is None:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not feed_url:
                feed_url = data.get("blacklist_feed_url")
            if interval_hours is None:
                interval_hours = int(data.get("blacklist_update_interval_hours", 12))
        except Exception:
            if interval_hours is None:
                interval_hours = 12
    if interval_hours is None:
        interval_hours = 12
    return feed_url, interval_hours


class DynamicScanScheduler:
    """APScheduler を用いて定期的なダイナミックスキャンを管理するクラス"""

    def __init__(self) -> None:
        self.scheduler: AsyncIOScheduler | None = None
        self.job = None
        self.blacklist_job = None
        self.capture_task: asyncio.Task | None = None
        self.analyse_task: asyncio.Task | None = None
        self.storage: storage.Storage = storage.Storage()

    async def _run_scan(self, interface: str | None, duration: int | None, approved_macs: Iterable[str] | None) -> None:
        """実際に 1 回のスキャンを実行する内部メソッド"""
        queue, self.capture_task = capture.capture_packets(
            interface=interface, duration=duration
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
        if self.blacklist_job:
            self.blacklist_job.remove()
        # APScheduler でコルーチンを定期実行
        self.job = self.scheduler.add_job(
            self._run_scan,
            trigger="interval",
            seconds=interval,
            args=[interface, duration, approved_macs],
            max_instances=1,
        )
        feed_url, interval_hours = load_blacklist_config()
        if feed_url:
            self.blacklist_job = self.scheduler.add_job(
                blacklist_updater.update,
                trigger="interval",
                hours=interval_hours,
                args=[feed_url],
            )

    async def stop(self) -> None:
        """スケジュールされたジョブと進行中のタスクを停止"""
        if self.job:
            self.job.remove()
            self.job = None
        if self.blacklist_job:
            self.blacklist_job.remove()
            self.blacklist_job = None
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
