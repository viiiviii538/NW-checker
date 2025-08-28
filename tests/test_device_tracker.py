import asyncio
import sqlite3

from src.dynamic_scan import device_tracker


def test_track_device_records_and_alerts(tmp_path):
    # 使用するDBを一時ファイルに変更
    device_tracker.DB_PATH = tmp_path / "dev.db"
    device_tracker._known_devices.clear()
    device_tracker._listeners.clear()

    # approved デバイスが既知として扱われること
    device_tracker._known_devices.add("00:11:22:33:44:55")
    assert device_tracker.track_device("00:11:22:33:44:55") is False

    # 新規デバイスを追跡
    q = asyncio.Queue()
    device_tracker.add_listener(q)
    assert device_tracker.track_device("66:77:88:99:aa:bb") is True
    alert = q.get_nowait()
    assert alert["mac"] == "66:77:88:99:aa:bb"

    with sqlite3.connect(device_tracker.DB_PATH) as conn:
        rows = conn.execute("SELECT mac FROM devices").fetchall()
    assert rows == [("66:77:88:99:aa:bb",)]
