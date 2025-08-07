import asyncio

from src.dynamic_scan import scheduler, capture, analyze, storage


def test_scheduler_start_and_stop(monkeypatch):
    async def inner():
        sched = scheduler.DynamicScanScheduler()

        async def dummy_capture(queue, interface=None, duration=None):
            return

        async def dummy_analyse(queue, storage_obj, approved_macs=None):
            return

        monkeypatch.setattr(capture, "capture_packets", dummy_capture)
        monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

        sched.start(duration=0, interval=1)
        assert sched.scheduler is not None
        assert sched.job is not None

        # ダミータスクを設定し stop でキャンセルされるか確認
        t1 = asyncio.create_task(asyncio.sleep(1))
        t2 = asyncio.create_task(asyncio.sleep(1))
        sched.capture_task = t1
        sched.analyse_task = t2

        await sched.stop()
        assert sched.scheduler is None
        assert sched.job is None
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

        async def dummy_capture(queue, interface=None, duration=None):
            flags["capture"] = True

        async def dummy_analyse(queue, storage_obj, approved_macs=None):
            flags["analyse"] = True

        monkeypatch.setattr(capture, "capture_packets", dummy_capture)
        monkeypatch.setattr(analyze, "analyse_packets", dummy_analyse)

        await sched._run_scan(interface=None, duration=None, approved_macs=None)
        assert flags["capture"] and flags["analyse"]
        assert sched.capture_task is None
        assert sched.analyse_task is None

    asyncio.run(inner())
