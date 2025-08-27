"""Protocol detection utilities.

Defines dangerous ports and provides helpers to flag dangerous protocols
based on source/destination port numbers.
"""

from __future__ import annotations

from typing import Any


# Ports commonly associated with insecure or high-risk services
DANGEROUS_PORTS: set[int] = {21, 23, 3389, 445}


def is_dangerous_protocol(src_port: Any, dst_port: Any) -> bool:
    """Return True if either port is considered dangerous.

    Non-integer values are ignored.
    """
    ports = set()
    for p in (src_port, dst_port):
        if isinstance(p, int):
            ports.add(p)
    return any(p in DANGEROUS_PORTS for p in ports)


def analyze_packet(pkt: Any) -> bool:
    """Check packet ports and flag dangerous protocols."""
    src_port = getattr(pkt, "src_port", getattr(pkt, "sport", None))
    dst_port = getattr(pkt, "dst_port", getattr(pkt, "dport", None))
    return is_dangerous_protocol(src_port, dst_port)
