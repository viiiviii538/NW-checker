import asyncio
from scapy.all import AsyncSniffer

from . import parser


async def capture_packets(
    queue: asyncio.Queue,
    interface: str | None = None,
    duration: int | None = None,
) -> None:
    """Capture packets and enqueue them for analysis.

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

    # Callback invoked for each captured packet; parse it and enqueue for
    # analysis so downstream tasks work with a simple, normalized structure.
    def _enqueue(packet) -> None:
        parsed = parser.parse_packet(packet)
        queue.put_nowait(parsed)

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
