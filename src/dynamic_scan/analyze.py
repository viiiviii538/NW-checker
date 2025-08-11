import asyncio
import socket
from dataclasses import asdict, dataclass
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Iterable
import json
from pathlib import Path

import requests

# 危険とされるプロトコルの名称
DANGEROUS_PROTOCOLS = {"telnet", "ftp", "rdp"}
# DNS 逆引きのブラックリスト
DNS_BLACKLIST = {"malicious.example"}

CONFIG_PATH = Path(__file__).with_name("config.json")


@dataclass
class AnalysisResult:
    """解析結果を共通形式で表すデータクラス"""

    src_ip: str | None = None
    dst_ip: str | None = None
    protocol: str | None = None
    geoip: Dict[str, Any] | None = None
    reverse_dns: str | None = None
    reverse_dns_blacklisted: bool | None = None
    dangerous_protocol: bool | None = None
    new_device: bool | None = None
    unapproved_device: bool | None = None
    traffic_anomaly: bool | None = None
    out_of_hours: bool | None = None

    def to_dict(self) -> Dict[str, Any]:
        """None でないフィールドのみ dict 化して返す"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def merge(cls, *results: "AnalysisResult") -> "AnalysisResult":
        """複数の解析結果を一つにまとめる"""
        merged = cls()
        for res in results:
            for key, value in asdict(res).items():
                if value is not None:
                    setattr(merged, key, value)
        return merged


# DNS 履歴と検出済みデバイスの簡易メモリ
_dns_history: Dict[str, str] = {}
_known_devices: set[str] = set()


def geoip_lookup(ip: str) -> Dict[str, Any]:
    """GeoIP 情報を取得する。
    ローカル GeoIP2 DB が利用可能であれば優先し、
    それ以外は外部 API を利用する。取得できない場合は空 dict を返す。
    """
    # GeoIP2 データベースの利用を試みる
    try:  # pragma: no cover - 環境により存在しない可能性が高いため
        import geoip2.database

        reader = geoip2.database.Reader("/usr/share/GeoIP/GeoLite2-Country.mmdb")
        try:
            resp = reader.country(ip)
            return {"country": resp.country.name, "ip": ip}
        finally:
            reader.close()
    except Exception:
        pass

    # 外部 API へのフォールバック
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if response.ok:
            data = response.json()
            return {"country": data.get("country_name"), "ip": ip}
    except Exception:
        pass
    return {}


def reverse_dns_lookup(ip: str) -> str | None:
    """DNS 逆引きを行い、結果を履歴に保持する。"""
    if ip in _dns_history:
        return _dns_history[ip]
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        _dns_history[ip] = hostname
        return hostname
    except Exception:
        return None


def is_dangerous_protocol(protocol: str | None) -> bool:
    """危険プロトコルか判定する。
    文字列以外が渡された場合は危険ではないとみなす。
    """
    if not isinstance(protocol, str):
        return False
    return protocol.lower() in DANGEROUS_PROTOCOLS


def is_unapproved_device(mac: str, approved_macs: Iterable[str]) -> bool:
    """未承認デバイス (MACアドレス) か判定する。"""
    return mac not in set(approved_macs)


def load_threshold(path: Path | None = None, default: int = 1_000_000) -> int:
    """設定ファイルから閾値を読み込む。存在しない場合はデフォルト値を返す。"""
    path = path or CONFIG_PATH
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("traffic_threshold", default))
    except Exception:
        return default


def detect_traffic_anomaly(
    traffic_stats: Dict[str, int],
    key: str,
    size: int,
    threshold: int | None = None,
) -> bool:
    """通信量を集計し、閾値を超えた場合に異常とみなす。"""
    if threshold is None:
        threshold = load_threshold()
    traffic_stats[key] += size
    return traffic_stats[key] > threshold


def is_night_traffic(timestamp: float, start_hour: int = 0, end_hour: int = 6) -> bool:
    """深夜帯の通信か判定する。"""
    hour = datetime.fromtimestamp(timestamp).hour
    return start_hour <= hour < end_hour


def attach_geoip(result: AnalysisResult, ip: str | None) -> AnalysisResult:
    """指定 IP の GeoIP 情報を解析結果に保存する"""
    if ip:
        result.geoip = geoip_lookup(ip)
        if result.src_ip is None:
            result.src_ip = ip
    return result


def assign_geoip_info(packet) -> AnalysisResult:
    """GeoIP 情報をパケットに付与する"""
    src_ip = getattr(packet, "src_ip", getattr(packet, "ip_src", None))
    dst_ip = getattr(packet, "dst_ip", getattr(packet, "ip_dst", None))
    result = AnalysisResult(src_ip=src_ip, dst_ip=dst_ip)
    return attach_geoip(result, src_ip)


def record_dns_history(packet) -> AnalysisResult:
    """DNS 履歴を記録しブラックリストを確認"""
    src_ip = getattr(packet, "src_ip", getattr(packet, "ip_src", None))
    if not src_ip:
        return AnalysisResult()
    hostname = reverse_dns_lookup(src_ip)
    blacklisted = hostname in DNS_BLACKLIST if hostname else None
    return AnalysisResult(reverse_dns=hostname, reverse_dns_blacklisted=blacklisted)


def detect_dangerous_protocols(packet) -> AnalysisResult:
    """危険なプロトコルを検出"""
    protocol = getattr(packet, "protocol", getattr(getattr(packet, "payload", None), "name", "unknown"))
    dangerous = is_dangerous_protocol(protocol)
    return AnalysisResult(protocol=protocol, dangerous_protocol=dangerous)


def track_new_devices(packet) -> AnalysisResult:
    """新たに観測されたデバイスを追跡"""
    mac = getattr(packet, "src_mac", getattr(packet, "mac", getattr(packet, "src", "")))
    is_new = mac not in _known_devices
    if is_new:
        _known_devices.add(mac)
    return AnalysisResult(new_device=is_new)


def detect_traffic_anomalies(packet, stats, threshold: int | None = None) -> AnalysisResult:
    """通信量の異常を検出"""
    key = getattr(packet, "src_ip", getattr(packet, "ip_src", getattr(packet, "src_mac", "")))
    size = getattr(packet, "size", getattr(packet, "len", 0))
    anomaly = detect_traffic_anomaly(stats, key, size, threshold=threshold)
    return AnalysisResult(traffic_anomaly=anomaly)


def detect_out_of_hours(packet, schedule) -> AnalysisResult:
    """時間外通信を検出"""
    timestamp = getattr(packet, "timestamp", getattr(packet, "time", datetime.now().timestamp()))
    start_hour, end_hour = schedule
    hour = datetime.fromtimestamp(timestamp).hour
    out = hour < start_hour or hour >= end_hour
    return AnalysisResult(out_of_hours=out)


async def analyse_packets(
    queue: asyncio.Queue,
    storage,
    approved_macs: Iterable[str] | None = None,
    schedule: tuple[int, int] = (0, 6),
) -> None:
    """キューからパケットを取得し解析する。"""

    approved = set(approved_macs or [])
    traffic_stats: Dict[str, int] = defaultdict(int)

    while True:
        packet = await queue.get()

        geoip_res = await asyncio.to_thread(assign_geoip_info, packet)
        dns_res = await asyncio.to_thread(record_dns_history, packet)
        dangerous_res = detect_dangerous_protocols(packet)
        new_dev_res = track_new_devices(packet)
        traffic_res = detect_traffic_anomalies(packet, traffic_stats)
        out_res = detect_out_of_hours(packet, schedule)

        mac = getattr(packet, "src_mac", getattr(packet, "mac", getattr(packet, "src", "")))
        unapproved = is_unapproved_device(mac, approved)
        unapproved_res = AnalysisResult(unapproved_device=unapproved)

        combined = AnalysisResult.merge(
            geoip_res,
            dns_res,
            dangerous_res,
            new_dev_res,
            traffic_res,
            out_res,
            unapproved_res,
        )

        await storage.save_result(combined.to_dict())
        queue.task_done()
