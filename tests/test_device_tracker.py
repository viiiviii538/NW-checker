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


def test_load_approved_devices(tmp_path, monkeypatch):
    cfg = tmp_path / "approved.json"
    cfg.write_text('["AA:BB:CC:DD:EE:FF"]')
    monkeypatch.setattr(device_tracker, "CONFIG_PATH", cfg)
    device_tracker._known_devices.clear()
    device_tracker._load_approved_devices()
    assert "aa:bb:cc:dd:ee:ff" in device_tracker._known_devices


def test_startup_loads_config(monkeypatch):
    """デフォルトの設定ファイルがインポート時に読み込まれること"""
    # モジュールを再読み込みして approved_devices.json を読み込ませる
    import importlib

    monkeypatch.setattr(device_tracker, "_known_devices", set())
    importlib.reload(device_tracker)
    assert "00:11:22:33:44:55" in device_tracker._known_devices
