import time
from collections import deque
from typing import Dict, Any

# 統計情報の保持
_stats: Dict[str, Dict[str, Any]] = {}

# 過去のサンプル数の上限
MAX_SAMPLES = 10
# スパイク判定の閾値（バイト）
SPIKE_THRESHOLD = 1_000_000
# 常時通信検知用の継続時間閾値（秒）
CONTINUOUS_DURATION = 60
# 通信が途切れたとみなす間隔（秒）
CONTINUOUS_GAP = 10

def update_traffic_stats(mac: str, bytes: int) -> None:
    """通信量統計を更新する。

    Args:
        mac: デバイスの MAC アドレス
        bytes: 今回観測した通信量
    """
    now = time.time()
    entry = _stats.get(mac)
    if entry is None:
        entry = {
            "history": deque(maxlen=MAX_SAMPLES),
            "total": 0,
            "count": 0,
            "start_time": now,
            "last_seen": now,
        }
        _stats[mac] = entry
    else:
        # 一定時間通信がなければ統計をリセット
        if now - entry["last_seen"] > CONTINUOUS_GAP:
            entry["history"].clear()
            entry["total"] = 0
            entry["count"] = 0
            entry["start_time"] = now
    entry["history"].append(bytes)
    entry["total"] += bytes
    entry["count"] += 1
    entry["last_seen"] = now

def detect_spike(mac: str) -> bool:
    """過去平均 ± 閾値で通信スパイクを検知する。

    スパイク判定に加え、継続時間が一定閾値を超えた常時通信も検出する。
    """
    entry = _stats.get(mac)
    if not entry:
        return False
    now = time.time()
    # 常時通信の検出
    if now - entry["start_time"] > CONTINUOUS_DURATION:
        return True
    latest = entry["history"][-1]
    if entry["count"] == 1:
        return latest > SPIKE_THRESHOLD
    avg = (entry["total"] - latest) / (entry["count"] - 1)
    return latest > avg + SPIKE_THRESHOLD
