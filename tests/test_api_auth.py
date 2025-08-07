import pytest
from fastapi.testclient import TestClient

from src import api


def test_auth_middleware_enforces_token(monkeypatch):
    client = TestClient(api.app)
    prev = api.API_TOKEN
    api.API_TOKEN = "s3cret"
    try:
        resp = client.get("/scan/dynamic/results")
        assert resp.status_code == 401
        resp2 = client.get(
            "/scan/dynamic/results",
            headers={"Authorization": "Bearer s3cret"},
        )
        assert resp2.status_code == 200
    finally:
        api.API_TOKEN = prev
