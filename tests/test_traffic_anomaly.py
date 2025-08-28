from src.dynamic_scan import traffic_anomaly


def test_spike_detection(monkeypatch):
    traffic_anomaly._stats.clear()
    monkeypatch.setattr(traffic_anomaly, 'SPIKE_THRESHOLD', 100)
    mac = 'aa:bb'
    traffic_anomaly.update_traffic_stats(mac, 50)
    traffic_anomaly.update_traffic_stats(mac, 60)
    assert traffic_anomaly.detect_spike(mac) is False
    traffic_anomaly.update_traffic_stats(mac, 300)
    assert traffic_anomaly.detect_spike(mac) is True


def test_continuous_traffic(monkeypatch):
    traffic_anomaly._stats.clear()
    mac = 'cc:dd'
    fake_time = [0]

    def fake_time_func():
        return fake_time[0]

    monkeypatch.setattr(traffic_anomaly.time, 'time', fake_time_func)
    monkeypatch.setattr(traffic_anomaly, 'CONTINUOUS_DURATION', 5)
    traffic_anomaly.update_traffic_stats(mac, 10)  # t=0
    fake_time[0] += 3
    traffic_anomaly.update_traffic_stats(mac, 10)  # t=3
    fake_time[0] += 3
    assert traffic_anomaly.detect_spike(mac) is True


def test_reset_after_gap(monkeypatch):
    """通信が途切れると統計がリセットされる"""
    traffic_anomaly._stats.clear()
    fake_time = [0]

    monkeypatch.setattr(traffic_anomaly.time, "time", lambda: fake_time[0])
    monkeypatch.setattr(traffic_anomaly, "CONTINUOUS_GAP", 1)

    mac = "aa:bb"
    traffic_anomaly.update_traffic_stats(mac, 100)  # t=0
    fake_time[0] += 2  # gap > CONTINUOUS_GAP
    traffic_anomaly.update_traffic_stats(mac, 50)  # t=2 -> stats reset

    assert traffic_anomaly._stats[mac]["count"] == 1
    assert traffic_anomaly.detect_spike(mac) is False


def test_single_sample_spike(monkeypatch):
    """初回サンプルでも閾値超過でスパイク判定"""
    traffic_anomaly._stats.clear()
    monkeypatch.setattr(traffic_anomaly, "SPIKE_THRESHOLD", 100)
    mac = "aa:bb"
    traffic_anomaly.update_traffic_stats(mac, 150)
    assert traffic_anomaly.detect_spike(mac) is True


def test_stats_isolation(monkeypatch):
    """MACごとの統計が互いに影響しない"""
    traffic_anomaly._stats.clear()
    monkeypatch.setattr(traffic_anomaly, "SPIKE_THRESHOLD", 100)

    mac1, mac2 = "00:11", "22:33"
    traffic_anomaly.update_traffic_stats(mac1, 50)
    traffic_anomaly.update_traffic_stats(mac2, 150)

    assert traffic_anomaly.detect_spike(mac1) is False
    assert traffic_anomaly.detect_spike(mac2) is True
    assert traffic_anomaly._stats[mac1]["count"] == 1
    assert traffic_anomaly._stats[mac2]["count"] == 1
