import asyncio
import json

from src.dynamic_scan import scheduler, capture, analyze, storage


def test_scheduler_start_and_stop(monkeypatch):
    async def inner():
        sched = scheduler.DynamicScanScheduler()

        def dummy_capture(interface=None, duration=None):
            return asyncio.Queue(), asyncio.create_task(asyncio.sleep(0))

        async def dummy_analyse(queue, storage_obj, approved_macs=None):
            return

        monkeypatch.setattr(capture, "capture_packets", dummy_capture)
        monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)
        monkeypatch.setenv("BLACKLIST_FEED_URL", "http://example.com/feed.json")
        monkeypatch.setenv("BLACKLIST_UPDATE_INTERVAL_HOURS", "1")
        monkeypatch.setattr(scheduler.blacklist_updater, "update", lambda url: None)

        sched.start(duration=0, interval=1)
        assert sched.scheduler is not None
        assert sched.job is not None
        assert sched.blacklist_job is not None
        assert sched.blacklist_job.args == ("http://example.com/feed.json",)

        # ダミータスクを設定し stop でキャンセルされるか確認
        t1 = asyncio.create_task(asyncio.sleep(1))
        t2 = asyncio.create_task(asyncio.sleep(1))
        sched.capture_task = t1
        sched.analyse_task = t2

        await sched.stop()
        assert sched.scheduler is None
        assert sched.job is None
        assert sched.blacklist_job is None
        assert t1.cancelled()
        assert t2.cancelled()
        assert sched.capture_task is None
        assert sched.analyse_task is None

    asyncio.run(inner())


def test_run_scan_executes_tasks(monkeypatch, tmp_path):
    async def inner():
        sched = scheduler.DynamicScanScheduler()
        sched.storage = storage.Storage(tmp_path / "res.db")
        flags = {"capture": False, "analyse": False}

        def dummy_capture(interface=None, duration=None):
            flags["capture"] = True
            return asyncio.Queue(), asyncio.create_task(asyncio.sleep(0))

        async def dummy_analyse(queue, storage_obj, approved_macs=None):
            flags["analyse"] = True

        monkeypatch.setattr(capture, "capture_packets", dummy_capture)
        monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

        await sched._run_scan(interface=None, duration=None, approved_macs=None)
        assert flags["capture"] and flags["analyse"]
        assert sched.capture_task is None
        assert sched.analyse_task is None

    asyncio.run(inner())


def test_scheduler_loads_config(monkeypatch, tmp_path):
    async def inner():
        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "blacklist_feed_url": "http://conf.example.com/feed.csv",
                    "blacklist_update_interval_hours": 2,
                }
            )
        )
        monkeypatch.delenv("BLACKLIST_FEED_URL", raising=False)
        monkeypatch.delenv("BLACKLIST_UPDATE_INTERVAL_HOURS", raising=False)
        monkeypatch.setattr(scheduler, "CONFIG_PATH", config_path)
        monkeypatch.setattr(scheduler.blacklist_updater, "update", lambda url: None)

        sched = scheduler.DynamicScanScheduler()
        sched.start(duration=0, interval=1)
        assert sched.blacklist_job is not None
        assert sched.blacklist_job.args == ("http://conf.example.com/feed.csv",)
        await sched.stop()

    asyncio.run(inner())


def test_no_blacklist_job_without_feed_url(monkeypatch, tmp_path):
    async def inner():
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({}))
        monkeypatch.delenv("BLACKLIST_FEED_URL", raising=False)
        monkeypatch.delenv("BLACKLIST_UPDATE_INTERVAL_HOURS", raising=False)
        monkeypatch.setattr(scheduler, "CONFIG_PATH", config_path)

        sched = scheduler.DynamicScanScheduler()
        sched.start(duration=0, interval=1)
        assert sched.blacklist_job is None
        await sched.stop()

    asyncio.run(inner())
