from __future__ import annotations

"""Utility functions to normalise raw scapy packets for analysis."""

from types import SimpleNamespace
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Packet


def parse_packet(packet: Packet) -> SimpleNamespace:
    """Convert a Scapy packet into a simple namespace.

    The analyser only needs a handful of common fields. This helper extracts
    them and returns a lightweight object that mimics the attributes used in
    :mod:`src.dynamic_scan.analyze`.
    """
    if packet is None:
        return SimpleNamespace()

    src_mac = dst_mac = src_ip = dst_ip = protocol = None
    # パケットサイズとタイムスタンプを取得
    size = len(packet)
    timestamp = getattr(packet, "time", None)

    ether = packet.getlayer(Ether)
    if ether is not None:
        src_mac = ether.src
        dst_mac = ether.dst

    ip_layer = packet.getlayer(IP)
    if ip_layer is not None:
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst

    # プロトコルは L4 レイヤー名を優先
    if packet.getlayer(TCP):
        protocol = "tcp"
    elif packet.getlayer(UDP):
        protocol = "udp"
    elif ip_layer is not None:
        protocol = str(ip_layer.proto)

    return SimpleNamespace(
        src_mac=src_mac,
        dst_mac=dst_mac,
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        size=size,
        timestamp=timestamp,
    )
