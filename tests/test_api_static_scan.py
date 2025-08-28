import time
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from src import server

pytestmark = pytest.mark.fastapi


def test_static_scan_success(monkeypatch):
    def fake_run_all():
        return {"findings": {"dummy": {"score": 1, "details": {}}}, "risk_score": 1}

    monkeypatch.setattr(server.static_scan, "run_all", fake_run_all)

    called = {}

    def fake_pdf(data, path):
        called["path"] = path

    monkeypatch.setattr(server, "create_pdf", fake_pdf)

    client = TestClient(server.app)
    resp = client.get("/static_scan", params={"report": "true"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["findings"]["dummy"]["score"] == 1
    assert body["risk_score"] == 1
    assert body["report_path"] == server.REPORT_PATH
    assert called["path"] == server.REPORT_PATH


def test_static_scan_error(monkeypatch):
    def failing_run_all():
        raise RuntimeError("boom")

    monkeypatch.setattr(server.static_scan, "run_all", failing_run_all)

    client = TestClient(server.app)
    resp = client.get("/static_scan")

    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"
    assert "boom" in body["message"]


def test_static_scan_timeout(monkeypatch):
    def slow_run_all():
        time.sleep(1)

    monkeypatch.setattr(server.static_scan, "run_all", slow_run_all)
    monkeypatch.setattr(server, "STATIC_SCAN_TIMEOUT", 0.01)

    client = TestClient(server.app)
    resp = client.get("/static_scan")

    assert resp.status_code == 504
    body = resp.json()
    assert body["status"] == "timeout"

