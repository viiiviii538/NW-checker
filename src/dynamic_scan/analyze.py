import asyncio
import socket
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Iterable

import requests

# 危険とされるプロトコルの名称
DANGEROUS_PROTOCOLS = {"telnet", "ftp", "rdp"}


def geoip_lookup(ip: str) -> Dict[str, Any]:
    """GeoIP 情報を取得する。
    外部 API を利用し、取得できない場合は空 dict を返す。
    """
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if response.ok:
            data = response.json()
            return {"country": data.get("country_name"), "ip": ip}
    except Exception:
        pass
    return {}


def reverse_dns_lookup(ip: str) -> str | None:
    """DNS 逆引きを行い、ホスト名を返す。失敗時は None。"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None


def is_dangerous_protocol(protocol: str) -> bool:
    """危険プロトコルか判定する。"""
    return protocol.lower() in DANGEROUS_PROTOCOLS


def is_unapproved_device(mac: str, approved_macs: Iterable[str]) -> bool:
    """未承認デバイス (MACアドレス) か判定する。"""
    return mac not in set(approved_macs)


def detect_traffic_anomaly(traffic_stats: Dict[str, int], key: str, size: int, threshold: int = 1_000_000) -> bool:
    """通信量を集計し、閾値を超えた場合に異常とみなす。"""
    traffic_stats[key] += size
    return traffic_stats[key] > threshold


def is_night_traffic(timestamp: float, start_hour: int = 0, end_hour: int = 6) -> bool:
    """深夜帯の通信か判定する。"""
    hour = datetime.fromtimestamp(timestamp).hour
    return start_hour <= hour < end_hour


async def analyse_packets(queue: asyncio.Queue, storage, approved_macs: Iterable[str] | None = None) -> None:
    """キューからパケットを取得し解析する。"""
    approved = set(approved_macs or [])
    traffic_stats: Dict[str, int] = defaultdict(int)

    while True:
        packet = await queue.get()

        src_ip = getattr(packet, "src_ip", getattr(packet, "ip_src", None))
        dst_ip = getattr(packet, "dst_ip", getattr(packet, "ip_dst", None))
        protocol = getattr(packet, "protocol", getattr(getattr(packet, "payload", None), "name", "unknown"))
        mac = getattr(packet, "src_mac", getattr(packet, "mac", getattr(packet, "src", "")))
        size = getattr(packet, "size", getattr(packet, "len", 0))
        timestamp = getattr(packet, "timestamp", getattr(packet, "time", datetime.now().timestamp()))

        geoip = await asyncio.to_thread(geoip_lookup, src_ip) if src_ip else {}
        dns = reverse_dns_lookup(src_ip) if src_ip else None
        dangerous = is_dangerous_protocol(protocol)
        unapproved = is_unapproved_device(mac, approved)
        anomaly = detect_traffic_anomaly(traffic_stats, src_ip or mac, size)
        night = is_night_traffic(timestamp)

        result = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": protocol,
            "geoip": geoip,
            "reverse_dns": dns,
            "dangerous_protocol": dangerous,
            "unapproved_device": unapproved,
            "traffic_anomaly": anomaly,
            "night_traffic": night,
        }

        await storage.save(result)
        queue.task_done()
