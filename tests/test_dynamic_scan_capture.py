import asyncio
import pytest

from src.dynamic_scan import capture


def _patch_parser(monkeypatch):
    """Helper to patch parser.parse_packet with identity for tests."""
    monkeypatch.setattr(capture.parser, "parse_packet", lambda pkt: pkt)


def test_capture_packets_enqueue(monkeypatch):
    _patch_parser(monkeypatch)
    class FakeSniffer:
        def __init__(self, iface=None, prn=None):
            self.prn = prn

        def start(self):
            # 呼び出されるとパケットを即座にキューへ投入
            self.prn("pkt")

        def stop(self):  # pragma: no cover - 本テストでは処理なし
            pass

    # AsyncSniffer をモックし、capture_packets 内で使用する
    monkeypatch.setattr(capture, "AsyncSniffer", FakeSniffer)

    queue: asyncio.Queue = asyncio.Queue()
    # duration=0 とすることで即終了させる
    asyncio.run(capture.capture_packets(queue, duration=0))
    assert queue.get_nowait() == "pkt"


def test_capture_packets_uses_parser(monkeypatch):
    called = {}

    def fake_parse(pkt):
        called["pkt"] = pkt
        return f"parsed-{pkt}"

    monkeypatch.setattr(capture.parser, "parse_packet", fake_parse)

    class FakeSniffer:
        def __init__(self, iface=None, prn=None):
            self.prn = prn

        def start(self):
            self.prn("raw")

        def stop(self):  # pragma: no cover - 本テストでは処理なし
            pass

    monkeypatch.setattr(capture, "AsyncSniffer", FakeSniffer)

    queue: asyncio.Queue = asyncio.Queue()
    asyncio.run(capture.capture_packets(queue, duration=0))
    assert called["pkt"] == "raw"
    assert queue.get_nowait() == "parsed-raw"


def test_capture_packets_stops_after_duration(monkeypatch):
    _patch_parser(monkeypatch)
    class FakeSniffer:
        def __init__(self, iface=None, prn=None):
            self.started = False
            self.stopped = False
            FakeSniffer.instance = self

        def start(self):
            self.started = True

        def stop(self):  # pragma: no cover - nothing to do in test
            self.stopped = True

    async def fake_sleep(seconds: int):
        fake_sleep.called = seconds

    fake_sleep.called = None

    # モックを適用し、sleep を即時完了させる
    monkeypatch.setattr(capture, "AsyncSniffer", FakeSniffer)
    monkeypatch.setattr(capture.asyncio, "sleep", fake_sleep)

    queue: asyncio.Queue = asyncio.Queue()
    asyncio.run(capture.capture_packets(queue, duration=1))

    assert FakeSniffer.instance.started is True
    assert FakeSniffer.instance.stopped is True
    assert fake_sleep.called == 1


def test_capture_packets_stops_when_cancelled(monkeypatch):
    _patch_parser(monkeypatch)
    class FakeSniffer:
        def __init__(self, iface=None, prn=None):
            self.started = False
            self.stopped = False
            FakeSniffer.instance = self

        def start(self):
            self.started = True

        def stop(self):  # pragma: no cover - nothing to do in test
            self.stopped = True

    # AsyncSniffer をモックし、capture_packets 内で使用する
    monkeypatch.setattr(capture, "AsyncSniffer", FakeSniffer)

    queue: asyncio.Queue = asyncio.Queue()

    async def run_and_cancel():
        # duration=None で起動し、タスクをキャンセル
        task = asyncio.create_task(capture.capture_packets(queue))
        await asyncio.sleep(0)
        assert FakeSniffer.instance.started is True
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run_and_cancel())

    assert FakeSniffer.instance.stopped is True
