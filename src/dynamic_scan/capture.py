import asyncio
from scapy.all import AsyncSniffer

from . import parser


def capture_packets(
    interface: str | None = None,
    *,
    duration: int | None = None,
) -> tuple[asyncio.Queue, asyncio.Task]:
    """Start sniffing packets and enqueue parsed results.

    Parameters
    ----------
    interface: str | None, optional
        Network interface to sniff on. Defaults to Scapy's default interface.
    duration: int | None, keyword-only, optional
        Number of seconds to run the sniffer. ``None`` means run until cancelled.

    Returns
    -------
    tuple[asyncio.Queue, asyncio.Task]
        A queue where parsed packets are enqueued and the running sniffer task
        which should be awaited or cancelled by the caller.
    """

    queue: asyncio.Queue = asyncio.Queue()

    # Callback invoked for each captured packet; parse it and enqueue for
    # analysis so downstream consumers can operate on normalized structures.
    def _enqueue(packet) -> None:
        parsed = parser.parse_packet(packet)
        queue.put_nowait(parsed)

    async def _run() -> None:
        sniffer = AsyncSniffer(iface=interface, prn=_enqueue)
        sniffer.start()
        try:
            if duration is None:
                # Sleep until cancelled; ``Event`` is never set so this awaits
                # forever until the task is cancelled by the caller.
                await asyncio.Event().wait()
            else:
                await asyncio.sleep(duration)
        finally:
            sniffer.stop()

    task = asyncio.create_task(_run())
    return queue, task
