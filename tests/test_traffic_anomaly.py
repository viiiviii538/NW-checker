from src.dynamic_scan import traffic_anomaly


def test_spike_detection(monkeypatch):
    traffic_anomaly._stats.clear()
    monkeypatch.setattr(traffic_anomaly, "SPIKE_THRESHOLD", 100)
    mac = "aa:bb"
    traffic_anomaly.update_traffic_stats(mac, 50)
    traffic_anomaly.update_traffic_stats(mac, 60)
    assert traffic_anomaly.detect_spike(mac) is False
    traffic_anomaly.update_traffic_stats(mac, 300)
    assert traffic_anomaly.detect_spike(mac) is True


def test_continuous_traffic(monkeypatch):
    traffic_anomaly._stats.clear()
    mac = "cc:dd"
    fake_time = [0]

    def fake_time_func():
        return fake_time[0]

    monkeypatch.setattr(traffic_anomaly.time, "time", fake_time_func)
    monkeypatch.setattr(traffic_anomaly, "CONTINUOUS_DURATION", 5)
    traffic_anomaly.update_traffic_stats(mac, 10)  # t=0
    fake_time[0] += 3
    traffic_anomaly.update_traffic_stats(mac, 10)  # t=3
    fake_time[0] += 3
    assert traffic_anomaly.detect_spike(mac) is True
