import asyncio

from src.dynamic_scan import capture


def test_capture_packets_enqueue(monkeypatch):
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
