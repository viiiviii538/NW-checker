import time

from fastapi.testclient import TestClient
from src import server


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
