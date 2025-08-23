import asyncio
import time
import types
import sys

import httpx
from fastapi.testclient import TestClient

scans_stub = types.ModuleType("src.scans")
scans_stub.__path__ = []
sys.modules["src.scans"] = scans_stub

report_pkg = types.ModuleType("src.report")
report_pkg.__path__ = []
pdf_stub = types.ModuleType("src.report.pdf")
pdf_stub.create_pdf = lambda data, path: None
sys.modules["src.report"] = report_pkg
sys.modules["src.report.pdf"] = pdf_stub

from src import server


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


def test_static_scan_non_dict(monkeypatch):
    """run_allが辞書以外を返した場合のハンドリングを確認"""

    def weird_run_all():
        return ["80/tcp open http"]

    monkeypatch.setattr(server.static_scan, "run_all", weird_run_all)

    client = TestClient(server.app)
    resp = client.get("/static_scan")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["findings"] == ["80/tcp open http"]
    assert body["risk_score"] is None


def test_static_scan_does_not_block(monkeypatch):
    """Static scan runs in background so other endpoints stay responsive."""

    def slow_run_all():
        time.sleep(0.2)
        return {}

    monkeypatch.setattr(server.static_scan, "run_all", slow_run_all)

    async def make_requests():
        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            slow_task = asyncio.create_task(client.get("/static_scan"))
            await asyncio.sleep(0.01)
            start = time.perf_counter()
            resp = await client.get("/nope")
            elapsed = time.perf_counter() - start
            await slow_task
            return resp, elapsed

    resp, elapsed = asyncio.run(make_requests())
    assert resp.status_code == 404
    assert elapsed < 0.1

