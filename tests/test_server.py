import sys
import time
import types
import importlib

from fastapi.testclient import TestClient


def _import_server(monkeypatch, run_all):
    module = types.ModuleType('static_scan')
    module.run_all = run_all
    monkeypatch.setitem(sys.modules, 'static_scan', module)
    from src import server
    importlib.reload(server)
    return server


def test_static_scan_success(monkeypatch):
    def fake_run_all():
        return {'findings': {'ports': ['22']}, 'risk_score': 5}

    server = _import_server(monkeypatch, fake_run_all)
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

    server = _import_server(monkeypatch, slow_run_all)
    monkeypatch.setattr(server, 'STATIC_SCAN_TIMEOUT', 0.05)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 504
    assert resp.json()['status'] == 'timeout'


def test_static_scan_error(monkeypatch):
    def bad_run_all():
        raise RuntimeError('boom')

    server = _import_server(monkeypatch, bad_run_all)
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

    server = _import_server(monkeypatch, weird_run_all)
    client = TestClient(server.app)

    resp = client.get('/static_scan')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    assert data['findings'] == ['80/tcp open http']
    assert data['risk_score'] is None
