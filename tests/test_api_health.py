import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from src.api import app  # ← あなたのFastAPIアプリのエントリポイントをimport

pytestmark = pytest.mark.fastapi


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
