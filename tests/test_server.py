import asyncio
import logging
import time
import pytest

import httpx

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from src import server

pytestmark = pytest.mark.fastapi


def test_static_scan_success(monkeypatch):
    def fake_run_all():
        return {'findings': {'ports': ['22']}, 'risk_score': 5}

    monkeypatch.setattr(server.static_scan, 'run_all', fake_run_all)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    assert data['findings']['ports'] == ['22']
    assert data['risk_score'] == 5


def test_static_scan_timeout(monkeypatch):
    def slow_run_all():
        time.sleep(0.2)

    monkeypatch.setattr(server.static_scan, 'run_all', slow_run_all)
    monkeypatch.setattr(server, 'STATIC_SCAN_TIMEOUT', 0.05)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 504
    assert resp.json()['status'] == 'timeout'


def test_static_scan_error(monkeypatch):
    def bad_run_all():
        raise RuntimeError('boom')

    monkeypatch.setattr(server.static_scan, 'run_all', bad_run_all)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 500
    body = resp.json()
    assert body['status'] == 'error'
    assert 'boom' in body['message']


def test_static_scan_non_dict(monkeypatch):
    """run_allが辞書以外を返した場合のハンドリングを確認"""

    def weird_run_all():
        return ['80/tcp open http']

    monkeypatch.setattr(server.static_scan, 'run_all', weird_run_all)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    assert data['findings'] == ['80/tcp open http']
    assert data['risk_score'] is None


def test_static_scan_none(monkeypatch):
    """run_allがNoneを返した場合のハンドリングを確認"""

    def none_run_all():
        return None

    monkeypatch.setattr(server.static_scan, 'run_all', none_run_all)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    assert data['findings'] is None
    assert data['risk_score'] is None


def test_static_scan_pdf_report(monkeypatch):
    """PDFレポート生成の呼び出しを確認"""

    def fake_run_all():
        return {'findings': {'ports': {'score': 5}}, 'risk_score': 5}

    monkeypatch.setattr(server.static_scan, 'run_all', fake_run_all)

    called: dict = {}

    def fake_create_pdf(data, path):
        called['data'] = data
        called['path'] = path

    monkeypatch.setattr(server, 'create_pdf', fake_create_pdf)
    client = TestClient(server.app)

    resp = client.get('/static_scan', params={'report': 'true'})
    assert resp.status_code == 200
    assert called['data']['findings']['ports']['score'] == 5
    assert called['path'] == '/tmp/static_scan_report.pdf'
    assert resp.json()['report_path'] == '/tmp/static_scan_report.pdf'


def test_static_scan_does_not_block_other_requests(monkeypatch):
    """Static scan runs in background thread so other requests respond."""

    def slow_run_all():
        time.sleep(0.2)
        return {}

    monkeypatch.setattr(server.static_scan, 'run_all', slow_run_all)

    async def make_requests():
        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            slow_task = asyncio.create_task(client.get('/static_scan'))
            await asyncio.sleep(0.01)
            start = time.perf_counter()
            resp = await client.get('/nope')
            elapsed = time.perf_counter() - start
            await slow_task
            return resp, elapsed

    resp, elapsed = asyncio.run(make_requests())
    assert resp.status_code == 404
    assert elapsed < 0.1


def test_static_scan_logs_success(monkeypatch, caplog):
    """ログ出力（成功時）を確認"""

    def fake_run_all():
        return {}

    monkeypatch.setattr(server.static_scan, 'run_all', fake_run_all)
    client = TestClient(server.app)

    with caplog.at_level(logging.INFO):
        client.get('/static_scan')

    assert 'Starting static scan' in caplog.text
    assert 'Static scan completed' in caplog.text


def test_static_scan_logs_timeout(monkeypatch, caplog):
    """ログ出力（タイムアウト時）を確認"""

    def slow_run_all():
        time.sleep(0.2)

    monkeypatch.setattr(server.static_scan, 'run_all', slow_run_all)
    monkeypatch.setattr(server, 'STATIC_SCAN_TIMEOUT', 0.05)
    client = TestClient(server.app)

    with caplog.at_level(logging.INFO):
        client.get('/static_scan')

    assert 'Starting static scan' in caplog.text
    assert 'Static scan timed out' in caplog.text


def test_static_scan_logs_error(monkeypatch, caplog):
    """ログ出力（エラー時）を確認"""

    def bad_run_all():
        raise RuntimeError('boom')

    monkeypatch.setattr(server.static_scan, 'run_all', bad_run_all)
    client = TestClient(server.app)

    with caplog.at_level(logging.INFO):
        client.get('/static_scan')

    assert 'Starting static scan' in caplog.text
    assert 'Static scan failed' in caplog.text
