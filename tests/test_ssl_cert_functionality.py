import ssl
import socket

from src.scans import ssl_cert


class DummySocket:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False


class DummySSLSocket:
    def __init__(self, cert):
        self._cert = cert
    def getpeercert(self):
        return self._cert
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False


def test_ssl_cert_returns_subject(monkeypatch):
    cert = {"subject": ((("commonName", "example.com"),),)}

    def fake_create_connection(addr, timeout=3):
        return DummySocket()

    def fake_wrap_socket(sock, server_hostname=None):
        return DummySSLSocket(cert)

    class DummyContext:
        def wrap_socket(self, sock, server_hostname=None):
            return fake_wrap_socket(sock, server_hostname)

    monkeypatch.setattr(socket, "create_connection", fake_create_connection)
    monkeypatch.setattr(ssl, "create_default_context", lambda: DummyContext())

    result = ssl_cert.scan("example.com")
    assert result["details"]["subject"] == cert["subject"]

