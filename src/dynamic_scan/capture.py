import asyncio
from scapy.all import AsyncSniffer


async def capture_packets(queue: asyncio.Queue, interface: str | None = None, duration: int | None = None) -> None:
    """Capture packets using Scapy and put them onto the provided queue.

    Parameters
    ----------
    queue: asyncio.Queue
        Queue used to pass packets to the analyser.
    interface: str | None, optional
        Network interface to sniff on. Defaults to Scapy's default interface.
    duration: int | None, optional
        Number of seconds to run the sniffer. If ``None`` the sniffer runs
        indefinitely until cancelled.
    """

    def _enqueue(packet):
        queue.put_nowait(packet)

    sniffer = AsyncSniffer(iface=interface, prn=_enqueue)
    sniffer.start()
    try:
        if duration is None:
            await asyncio.Event().wait()  # Run until cancelled
        else:
            await asyncio.sleep(duration)
    finally:
        sniffer.stop()
